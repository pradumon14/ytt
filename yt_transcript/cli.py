"""
Main Command Line Interface (CLI) entry point for ytt (yt-transcript).

Author: Pradumon Sahani
"""

import os
import sys
import argparse
from typing import List, Dict, Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

from yt_transcript import __version__, __author__
from yt_transcript.utils import (
    parse_inputs,
    copy_to_clipboard,
    estimate_tokens,
    sanitize_filename
)
from yt_transcript.extractor import TranscriptExtractor
from yt_transcript.formatter import TranscriptFormatter, chunk_text
from yt_transcript.manual import show_manual
from yt_transcript.templates import apply_template, TEMPLATES
from yt_transcript.completions import generate_completion

console = Console()


def build_parser() -> argparse.ArgumentParser:
    """
    Build argparse argument parser for ytt CLI options.

    Returns:
        argparse.ArgumentParser: Configured argument parser object.
    """
    parser = argparse.ArgumentParser(
        prog="ytt",
        description=f"Extract, clean, and format YouTube video and playlist transcripts for LLMs, documentation, and RAG context.\nDeveloper: {__author__}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "inputs",
        nargs="*",
        help="YouTube Video URLs, Playlist URLs, Shorts, Video IDs, or local text file containing URLs/IDs."
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (e.g. transcript.md) or directory path (e.g. ./transcripts/)."
    )

    parser.add_argument(
        "--combine",
        action="store_true",
        help="Combine all extracted transcripts (from playlists or multiple videos) into a SINGLE file."
    )

    parser.add_argument(
        "-f", "--format",
        type=str,
        default="markdown",
        choices=["markdown", "llm", "text", "json", "jsonl", "srt", "vtt"],
        help="Output format style for LLM prompts or document files."
    )

    parser.add_argument(
        "-s", "--search",
        type=str,
        help="Search for a specific keyword or phrase inside the transcript and highlight matches."
    )

    parser.add_argument(
        "--template",
        type=str,
        choices=list(TEMPLATES.keys()),
        help="Wrap transcript in an AI prompt template (summary, qna, takeaways, flashcards)."
    )

    parser.add_argument(
        "-l", "--lang",
        type=str,
        default="en",
        help="Preferred language code(s), comma-separated (e.g. 'en', 'es,en')."
    )

    parser.add_argument(
        "-t", "--translate",
        type=str,
        help="Translate transcript into specified language code (e.g. 'en', 'es', 'de')."
    )

    parser.add_argument(
        "-c", "--copy",
        action="store_true",
        help="Automatically copy the extracted transcript to clipboard."
    )

    parser.add_argument(
        "--no-timestamps",
        action="store_true",
        help="Exclude timestamps from markdown/text output."
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata header (Title, URL, Channel) from output."
    )

    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Chunk output into blocks of N estimated tokens (great for fitting LLM context windows)."
    )

    parser.add_argument(
        "--list-langs",
        action="store_true",
        help="List all available transcript languages for the target video."
    )

    parser.add_argument(
        "-m", "--manual",
        action="store_true",
        help="Display the interactive help manual and developer user guide."
    )

    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Suppress rich terminal summary boxes; only print raw output to stdout (useful for piping)."
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"ytt (yt-transcript) v{__version__} - Developer: {__author__}"
    )

    return parser


def main():
    """
    CLI main function handling argument parsing, playlist/video fetching, 
    formatting, output rendering, and clipboard operations.
    """
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd in ["manual", "man", "guide"]:
            show_manual()
            sys.exit(0)
        elif cmd in ["completion", "completions"]:
            shell = sys.argv[2] if len(sys.argv) > 2 else "bash"
            try:
                print(generate_completion(shell))
            except ValueError as e:
                console.print(f"[bold red]Error:[/] {e}", file=sys.stderr)
            sys.exit(0)

    parser = build_parser()
    args = parser.parse_args()

    if args.manual:
        show_manual()
        sys.exit(0)

    if not args.inputs:
        parser.print_help()
        console.print(f"\n[bold cyan]Tip:[/] Run [bold green]ytt --manual[/] for the full guide | [italic]Developer: {__author__}[/]", file=sys.stderr)
        sys.exit(1)

    video_ids, playlists = parse_inputs(args.inputs)
    
    all_video_items = []
    for v_id in video_ids:
        all_video_items.append({'id': v_id, 'title': f'Video {v_id}', 'source_playlist': None})
        
    for pl in playlists:
        pl_title = pl.get('title', 'Playlist')
        if not args.quiet:
            console.print(f"[bold magenta][Playlist][/] [bold]{pl_title}[/] ({len(pl.get('videos', []))} videos)")
        for v in pl.get('videos', []):
            all_video_items.append({
                'index': v.get('index'),
                'id': v.get('id'),
                'title': v.get('title'),
                'source_playlist': pl_title
            })

    if not all_video_items:
        console.print("[bold red]Error:[/] No valid YouTube Video IDs or Playlists found.", file=sys.stderr)
        sys.exit(1)

    extractor = TranscriptExtractor()
    languages = [l.strip() for l in args.lang.split(",")]

    # Handle --list-langs mode
    if args.list_langs:
        for item in all_video_items:
            v_id = item['id']
            try:
                langs = extractor.list_languages(v_id)
                table = Table(title=f"Available Transcripts for Video: [bold cyan]{item['title']}[/] ({v_id})")
                table.add_column("Language Code", style="green")
                table.add_column("Language Name", style="bold")
                table.add_column("Auto-Generated?", style="magenta")
                table.add_column("Translatable?", style="blue")
                
                for l_item in langs:
                    table.add_row(
                        l_item["language_code"],
                        l_item["language"],
                        "Yes" if l_item["is_generated"] else "No",
                        "Yes" if l_item["is_translatable"] else "No"
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[bold red]Error listing languages for {v_id}:[/] {e}", file=sys.stderr)
        sys.exit(0)

    combined_outputs = []
    total_words = 0
    total_tokens = 0

    is_combining = args.combine or (len(all_video_items) > 1 and args.output and not args.output.endswith("/") and not os.path.isdir(args.output) and not os.path.exists(args.output) and "." in os.path.basename(args.output))

    # Process each video
    for idx, item in enumerate(all_video_items, 1):
        v_id = item['id']
        try:
            if not args.quiet:
                prefix = f"[{idx}/{len(all_video_items)}]" if len(all_video_items) > 1 else "[*]"
                console.print(f"[bold blue]{prefix} Processing Video:[/] {v_id} ({item['title']})")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                if not args.quiet:
                    task1 = progress.add_task(description="Fetching video metadata...", total=None)
                metadata = extractor.get_metadata(v_id)
                if item['title'] and item['title'] != f'Video {v_id}':
                    metadata.title = item['title']
                
                if not args.quiet:
                    progress.update(task1, description="Extracting transcript...", total=None)
                snippets = extractor.fetch_transcript(
                    video_id=v_id,
                    languages=languages,
                    translate_to=args.translate
                )

            formatter = TranscriptFormatter(metadata, snippets)
            formatted_content = formatter.format(
                output_format=args.format,
                include_timestamps=not args.no_timestamps,
                include_metadata=not args.no_metadata,
                search_query=args.search
            )

            if args.template:
                formatted_content = apply_template(formatted_content, args.template)

            word_count = len(formatted_content.split())
            tokens = estimate_tokens(formatted_content)
            total_words += word_count
            total_tokens += tokens

            if is_combining:
                section_header = f"\n\n# Video {idx}: {metadata.title}\n" if len(all_video_items) > 1 else ""
                combined_outputs.append(section_header + formatted_content)
            else:
                if args.output:
                    out_dir = args.output
                    if not out_dir.endswith("/") and not os.path.isdir(out_dir):
                        os.makedirs(out_dir, exist_ok=True)

                    ext = args.format if args.format != 'llm' else 'md'
                    safe_title = sanitize_filename(metadata.title)
                    filename = f"{idx:02d}_{safe_title}.{ext}"
                    filepath = os.path.join(out_dir, filename)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(formatted_content)

                    if not args.quiet:
                        console.print(f"[bold green][Saved][/] {filepath} ({word_count:,} words)")
                else:
                    if not args.quiet:
                        console.print(Panel(
                            f"[bold]Title:[/] {metadata.title}\n"
                            f"[bold]Channel:[/] {metadata.author}\n"
                            f"[bold]URL:[/] {metadata.url}\n"
                            f"[bold]Stats:[/] {word_count:,} words | ~{tokens:,} LLM tokens",
                            title=f"[bold blue]Transcript {idx}/{len(all_video_items)}[/]",
                            border_style="blue"
                        ))
                        syntax = Syntax(
                            formatted_content,
                            "markdown" if args.format in ["markdown", "llm"] else args.format,
                            theme="monokai",
                            line_numbers=False
                        )
                        console.print(syntax)
                    else:
                        print(formatted_content)

        except Exception as e:
            console.print(f"[bold red]Error processing video '{v_id}':[/] {e}", file=sys.stderr)

    if is_combining and combined_outputs:
        final_combined = "\n\n---\n\n".join(combined_outputs)
        
        if args.chunk_size:
            chunks = chunk_text(final_combined, chunk_tokens=args.chunk_size)
            if len(chunks) > 1:
                final_combined = ""
                for c_idx, chunk in enumerate(chunks, 1):
                    final_combined += f"\n<!-- --- CHUNK {c_idx}/{len(chunks)} --- -->\n{chunk}\n"

        if args.output:
            out_file = args.output
            if os.path.isdir(out_file):
                ext = args.format if args.format != 'llm' else 'md'
                out_file = os.path.join(out_file, f"combined_playlist_transcript.{ext}")

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(final_combined)

            if not args.quiet:
                console.print(Panel(
                    f"[bold green]Combined transcripts saved successfully.[/]\n"
                    f"[bold]Total Videos Processed:[/] {len(all_video_items)}\n"
                    f"[bold]Output File:[/] [link=file://{os.path.abspath(out_file)}]{out_file}[/link]\n"
                    f"[bold]Combined Stats:[/] {total_words:,} words | ~{total_tokens:,} LLM tokens\n"
                    f"[italic gray]Developer: {__author__}[/]",
                    title="[bold green]Playlist Combined Output Ready for AI Upload[/]",
                    border_style="green"
                ))
        else:
            if not args.quiet:
                console.print(Panel(
                    f"[bold]Combined Videos:[/] {len(all_video_items)}\n"
                    f"[bold]Stats:[/] {total_words:,} words | ~{total_tokens:,} LLM tokens\n"
                    f"[italic gray]Developer: {__author__}[/]",
                    title="[bold blue]Combined Transcript Summary[/]",
                    border_style="blue"
                ))
                syntax = Syntax(
                    final_combined,
                    "markdown" if args.format in ["markdown", "llm"] else args.format,
                    theme="monokai",
                    line_numbers=False
                )
                console.print(syntax)
            else:
                print(final_combined)

        if args.copy:
            if copy_to_clipboard(final_combined):
                if not args.quiet:
                    console.print("[bold green][Copied] Combined transcript copied to system clipboard.[/]")


if __name__ == "__main__":
    main()

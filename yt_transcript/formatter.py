import json
import math
import re
from typing import List, Dict, Any, Optional
from yt_transcript.extractor import VideoMetadata, TranscriptItem
from yt_transcript.utils import format_timestamp, estimate_tokens

def reconstruct_paragraphs(
    items: List[TranscriptItem],
    max_pause_sec: float = 2.0,
    max_paragraph_words: int = 120
) -> List[Dict[str, Any]]:
    """
    Reconstruct raw transcript snippet fragments into readable paragraphs.
    Groups lines based on speaker pauses (time gap > max_pause_sec) or sentence endings.
    """
    if not items:
        return []

    paragraphs = []
    current_text_bits = []
    current_start = items[0].start
    last_end = items[0].start + items[0].duration

    for item in items:
        gap = item.start - last_end
        text = item.text.strip()
        
        if not text:
            continue

        words_count = sum(len(b.split()) for b in current_text_bits)
        is_sentence_end = current_text_bits and current_text_bits[-1].endswith(('.', '?', '!'))
        is_long_pause = gap > max_pause_sec
        is_too_long = words_count >= max_paragraph_words

        if current_text_bits and (is_long_pause or is_sentence_end or is_too_long):
            p_text = " ".join(current_text_bits)
            paragraphs.append({
                "start": current_start,
                "timestamp": format_timestamp(current_start),
                "text": p_text
            })
            current_text_bits = []
            current_start = item.start

        current_text_bits.append(text)
        last_end = item.start + item.duration

    if current_text_bits:
        p_text = " ".join(current_text_bits)
        paragraphs.append({
            "start": current_start,
            "timestamp": format_timestamp(current_start),
            "text": p_text
        })

    return paragraphs

class TranscriptFormatter:
    def __init__(self, metadata: VideoMetadata, items: List[TranscriptItem]):
        self.metadata = metadata
        self.items = items
        self.paragraphs = reconstruct_paragraphs(items)

    def filter_by_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Filter paragraphs to only those matching the search query (case-insensitive).
        """
        if not query:
            return self.paragraphs
            
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        matching = []
        for p in self.paragraphs:
            if pattern.search(p["text"]):
                matching.append(p)
        return matching

    def format(
        self,
        output_format: str = "markdown",
        include_timestamps: bool = True,
        include_metadata: bool = True,
        search_query: Optional[str] = None
    ) -> str:
        """
        Format transcript into requested format:
        markdown, llm, text, json, jsonl, srt, vtt
        """
        target_paragraphs = self.filter_by_search(search_query) if search_query else self.paragraphs
        
        fmt = output_format.lower()
        if fmt == "markdown" or fmt == "md":
            return self._format_markdown(target_paragraphs, include_timestamps, include_metadata, search_query)
        elif fmt == "llm" or fmt == "prompt":
            return self._format_llm(target_paragraphs)
        elif fmt == "text" or fmt == "txt":
            return self._format_text(target_paragraphs, include_timestamps)
        elif fmt == "json":
            return self._format_json(target_paragraphs)
        elif fmt == "jsonl":
            return self._format_jsonl(target_paragraphs)
        elif fmt == "srt":
            return self._format_srt()
        elif fmt == "vtt":
            return self._format_vtt()
        else:
            raise ValueError(f"Unsupported output format: '{output_format}'.")

    def _format_markdown(self, paragraphs: List[Dict[str, Any]], include_timestamps: bool, include_metadata: bool, search_query: Optional[str]) -> str:
        full_text = " ".join(p["text"] for p in paragraphs)
        word_count = len(full_text.split())
        tokens = estimate_tokens(full_text)

        lines = []
        if include_metadata:
            lines.append(f"# {self.metadata.title}")
            lines.append(f"- **Channel:** [{self.metadata.author}]({self.metadata.author_url})" if self.metadata.author_url else f"- **Channel:** {self.metadata.author}")
            lines.append(f"- **URL:** {self.metadata.url}")
            if search_query:
                lines.append(f"- **Search Query:** `{search_query}` (Found {len(paragraphs)} matching paragraphs)")
            lines.append(f"- **Word Count:** {word_count:,} | **Estimated Tokens:** ~{tokens:,}")
            lines.append("\n---\n")

        if not paragraphs and search_query:
            lines.append(f"*No paragraphs found matching search query: '{search_query}'*")

        for p in paragraphs:
            text = p["text"]
            if search_query:
                # Highlight query terms in bold yellow markdown syntax
                pattern = re.compile(f"({re.escape(search_query)})", re.IGNORECASE)
                text = pattern.sub(r"**\1**", text)

            if include_timestamps:
                lines.append(f"**[{p['timestamp']}]** {text}\n")
            else:
                lines.append(f"{text}\n")

        return "\n".join(lines).strip()

    def _format_llm(self, paragraphs: List[Dict[str, Any]]) -> str:
        full_text = "\n\n".join(p["text"] for p in paragraphs)
        header = f'<youtube_transcript title="{self.metadata.title}" channel="{self.metadata.author}" url="{self.metadata.url}">'
        footer = '</youtube_transcript>'
        return f"{header}\n\n{full_text}\n\n{footer}"

    def _format_text(self, paragraphs: List[Dict[str, Any]], include_timestamps: bool) -> str:
        lines = []
        for p in paragraphs:
            if include_timestamps:
                lines.append(f"[{p['timestamp']}] {p['text']}")
            else:
                lines.append(p['text'])
        return "\n\n".join(lines)

    def _format_json(self, paragraphs: List[Dict[str, Any]]) -> str:
        full_text = " ".join(p["text"] for p in paragraphs)
        data = {
            "metadata": {
                "video_id": self.metadata.video_id,
                "title": self.metadata.title,
                "author": self.metadata.author,
                "url": self.metadata.url,
                "word_count": len(full_text.split()),
                "estimated_tokens": estimate_tokens(full_text)
            },
            "paragraphs": paragraphs,
            "raw_snippets": [
                {"text": i.text, "start": i.start, "duration": i.duration}
                for i in self.items
            ]
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _format_jsonl(self, paragraphs: List[Dict[str, Any]]) -> str:
        lines = []
        for p in paragraphs:
            obj = {
                "video_id": self.metadata.video_id,
                "start": p["start"],
                "timestamp": p["timestamp"],
                "text": p["text"]
            }
            lines.append(json.dumps(obj, ensure_ascii=False))
        return "\n".join(lines)

    def _format_srt(self) -> str:
        lines = []
        for idx, item in enumerate(self.items, 1):
            start_srt = self._sec_to_srt_time(item.start)
            end_srt = self._sec_to_srt_time(item.start + item.duration)
            lines.append(f"{idx}")
            lines.append(f"{start_srt} --> {end_srt}")
            lines.append(item.text)
            lines.append("")
        return "\n".join(lines)

    def _format_vtt(self) -> str:
        lines = ["WEBVTT", ""]
        for idx, item in enumerate(self.items, 1):
            start_vtt = self._sec_to_vtt_time(item.start)
            end_vtt = self._sec_to_vtt_time(item.start + item.duration)
            lines.append(f"{start_vtt} --> {end_vtt}")
            lines.append(item.text)
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _sec_to_srt_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def _sec_to_vtt_time(seconds: float) -> str:
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d}.{millis:03d}"

def chunk_text(text: str, chunk_tokens: int = 2000, overlap_tokens: int = 200) -> List[str]:
    """
    Split text into chunks based on estimated token size with overlapping context.
    """
    words = text.split()
    if not words:
        return []

    words_per_chunk = int(chunk_tokens * 0.75)
    words_overlap = int(overlap_tokens * 0.75)

    if len(words) <= words_per_chunk:
        return [text]

    chunks = []
    start_idx = 0
    total_words = len(words)

    while start_idx < total_words:
        end_idx = min(start_idx + words_per_chunk, total_words)
        chunk_words = words[start_idx:end_idx]
        chunks.append(" ".join(chunk_words))
        if end_idx == total_words:
            break
        start_idx += (words_per_chunk - words_overlap)

    return chunks

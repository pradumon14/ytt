"""
Interactive Rich terminal help manual and user guide for ytt.

Author: Pradumon Sahani
"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from yt_transcript import __version__, __author__

MANUAL_TEXT = f"""
# YTT Manual and User Guide
**Developer:** {__author__} | **Version:** {__version__}

`ytt` (YouTube Transcript Extractor) is a command-line utility designed to extract, clean, format, and prepare YouTube video and playlist transcripts for **LLMs (ChatGPT, Claude, Gemini, Cursor)**, AI file uploads, documentation, and RAG pipelines.

---

## 1. Quick Commands Reference

| Command | Action |
|---|---|
| `ytt <URL>` | Extract and preview formatted transcript in Markdown. |
| `ytt <URL> -f llm -c` | Format as XML prompt block and copy to clipboard. |
| `ytt <URL> -o doc.md` | Save transcript directly to `doc.md` file. |
| `ytt <PLAYLIST_URL> --combine -o full_playlist.md` | Extract entire playlist into ONE merged file for AI upload. |
| `ytt <PLAYLIST_URL> -o ./playlist_folder/` | Extract playlist into separate files per video. |
| `ytt <URL> --no-timestamps -f text` | Extract clean continuous prose with no timestamps. |
| `ytt <URL> --chunk-size 2000` | Chunk long podcast/video into 2k token blocks. |
| `ytt <URL> -t en` | Auto-translate non-English transcript to English. |
| `ytt <URL> --list-langs` | List all available caption languages. |
| `ytt urls.txt -o ./out/` | Batch process multiple URLs from a file. |
| `ytt <URL> -q | llm` | Pipe raw transcript silently into unix tools. |

---

## 2. YouTube Playlist and Batch Processing

`ytt` seamlessly extracts full YouTube playlists. You can handle playlist outputs in two ways:

### Option A: Combine All Playlist Transcripts into ONE Consolidated File (`--combine`)
Ideal for uploading a single complete file to ChatGPT, Claude Projects, Gemini, or Custom GPTs:
```bash
ytt "https://www.youtube.com/playlist?list=PL..." --combine -o my_course_playlist.md
```

### Option B: Save Separate Files for Each Video in a Folder
Saves numbered individual files (e.g. `01_Intro.md`, `02_Setup.md`) inside an output directory:
```bash
ytt "https://www.youtube.com/playlist?list=PL..." -o ./course_transcripts/
```

---

## 3. AI Upload and Prompt Engineering Tips

### Uploading to Claude, ChatGPT, and Gemini (File Uploads)
1. Use `-o filename.md` or `-o folder/` to create `.md` or `.txt` files.
2. Direct file upload: Attach the `.md` or `.txt` file directly in your ChatGPT/Claude conversation window or Project Knowledge Base.
3. XML Prompt Format (`-f llm`): Wraps transcript in clean `<youtube_transcript>` tags to prevent AI prompt confusion:
   ```bash
   ytt "https://youtu.be/dQw4w9WgXcQ" -f llm -c
   ```

---

## 4. Full Command Options Reference

```text
ytt [options] [inputs ...]
```

### Positional Arguments
- `inputs`: YouTube Video URLs, Playlist URLs (`list=...`), 11-character Video IDs, or local text files (`urls.txt`).

### Output Control Flags
- `-o, --output <PATH>`: Output file path (e.g. `transcript.md`) or directory path.
- `--combine`: Combine all extracted transcripts (from playlists or multiple URLs) into a single file.
- `-f, --format <FORMAT>`: Format style: `markdown` (default), `llm`, `text`, `json`, `jsonl`, `srt`, `vtt`.

### Formatting and Modifiers
- `-c, --copy`: Automatically copy output to clipboard.
- `--no-timestamps`: Remove timestamp labels `[01:23]`.
- `--no-metadata`: Exclude header title/URL metadata block.
- `--chunk-size <TOKENS>`: Split long transcripts into N estimated LLM token blocks.

### Language and Translation
- `-l, --lang <LANGS>`: Preferred transcript language code(s) (e.g. `en`, `es,en`). Default: `en`.
- `-t, --translate <LANG>`: Translate transcript to target language code (e.g. `en`, `fr`).
- `--list-langs`: Display table of available caption tracks.

### System and Interface
- `-q, --quiet`: Quiet mode; suppresses rich boxes, prints raw output for piping.
- `-m, --manual`: Display this manual.
- `-v, --version`: Display version information and developer credits.

---

## Author and Credits
Developed by **Pradumon Sahani**.
"""

def show_manual():
    """
    Render formatted markdown manual in the terminal.
    """
    console = Console()
    console.print(Panel(f"[bold cyan]YTT — YouTube Transcript CLI User Guide[/]\n[italic]Developer: {__author__}[/]", style="cyan"))
    md = Markdown(MANUAL_TEXT)
    console.print(md)

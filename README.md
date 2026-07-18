# ytt (yt-transcript)

A professional, high-performance command-line utility for extracting, cleaning, and formatting YouTube video and playlist transcripts for Large Language Models (ChatGPT, Claude, Gemini, Cursor), AI file uploads, documentation, and RAG pipelines.

**Author:** Pradumon Sahani  
**License:** MIT  

---

## Key Capabilities

- **YouTube Playlist Extraction:** Process entire YouTube playlists concurrently or sequentially.
- **Combined or Separate File Outputs:**
  - `--combine`: Merge all transcripts into a single consolidated file ready for AI document uploads.
  - Separate Files: Output numbered, sanitized `.md` or `.txt` files per video into a target directory.
- **LLM Context Optimization:** Exports clean Markdown, `<youtube_transcript>` XML tags, JSON, JSONL, SRT, or WebVTT.
- **Intelligent Paragraph Reconstruction:** Automatically merges noisy caption line fragments into continuous, readable prose.
- **LLM Token Estimation:** Displays word count and estimated LLM tokens for prompt engineering.
- **Context Chunking (`--chunk-size`):** Splits long podcast transcripts into token blocks with overlapping context.
- **In-Transcript Keyword Search (`-s / --search`):** Search and highlight matching sections with exact timestamps.
- **AI Prompt Templates (`--template`):** Wrap transcripts into pre-built prompts for summaries, FAQs, key takeaways, and flashcards.
- **Clipboard Integration (`-c`):** Copy formatted output directly to system clipboard.
- **Multi-language and Translation:** Extract native captions or auto-translate to target languages (`-t en`).

---

## Installation

Install locally in editable mode:

```bash
git clone https://github.com/pradumon14/ytt.git
cd ytt
pip install -e .
```

After installation, the `ytt`, `ytx`, `yt-transcript`, `yt2md`, and `yt2text` commands are available globally in your terminal.

---

## Usage Reference

### 1. Basic Transcript Extraction
```bash
ytt "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 2. Extract Playlist into a Single File for AI Upload
```bash
ytt "https://www.youtube.com/playlist?list=PLAYLIST_ID" --combine -o playlist_summary.md
```

### 3. Copy XML Prompt Block Directly to Clipboard
```bash
ytt "https://youtu.be/VIDEO_ID" -f llm -c
```

### 4. Search Keywords inside a Transcript
```bash
ytt "https://youtu.be/VIDEO_ID" --search "neural network"
```

### 5. Apply AI Prompt Template
```bash
ytt "https://youtu.be/VIDEO_ID" --template summary
```

### 6. Interactive User Guide
```bash
ytt manual
```

---

## Development and Testing

Run unit tests:
```bash
python3 -m unittest discover -s tests
```

---

## Author and License

Developed by **Pradumon Sahani**.  
Distributed under the MIT License.

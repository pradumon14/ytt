# 🎥 ytt (yt-transcript)

A fast, powerful CLI tool to extract, clean, and format YouTube video and playlist transcripts for **LLMs (ChatGPT, Claude, Gemini, Cursor)**, AI file uploads, documentation, RAG pipelines, and search indexes.

**Developer:** Pradumon Sahani

---

## ⚡ Key Features

- **YouTube Playlist Extraction:** Extract entire playlists at once!
- **Combined or Separate File Outputs:**
  - `--combine`: Merge all transcripts into a single file ready to upload directly into ChatGPT/Claude Projects.
  - Separate files: Save organized, numbered `.md` files per video into a target directory.
- **AI File Upload Ready:** Generates `.md`, `.txt`, `.json`, or `<youtube_transcript>` XML formatted files for seamless drag-and-drop into ChatGPT, Claude, and Gemini context windows.
- **Intelligent Paragraph Reconstruction:** Merges auto-caption fragments into continuous prose based on speech pauses.
- **LLM Token Estimator:** Displays estimated LLM token counts (`~tokens`) and word counts.
- **Context Chunking (`--chunk-size`):** Splits long transcripts into N-token blocks with overlapping context.
- **Languages & Auto-Translation:** Extract transcripts in any language (`-l es,en`) or auto-translate to your target language (`-t en`).
- **One-Click Clipboard Copy (`-c`):** Copy formatted transcripts straight to clipboard.
- **Short Commands:** Run `ytt` or `ytx`.

---

## 🛠️ Usage Examples

### 1. Extract Full Playlist into ONE Combined File for AI Upload
```bash
ytt "https://www.youtube.com/playlist?list=PL..." --combine -o course_transcripts.md
```

### 2. Extract Playlist into Separate Files per Video
```bash
ytt "https://www.youtube.com/playlist?list=PL..." -o ./playlist_folder/
```

### 3. Extract Single Video & Copy Prompt Block to Clipboard
```bash
ytt "https://youtu.be/dQw4w9WgXcQ" -f llm -c
```

### 4. Interactive Help Manual
```bash
ytt manual
```

---

## 👨‍💻 Developer Credits
Developed by **Pradumon Sahani**.

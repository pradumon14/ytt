# ytt (yt-transcript)

A professional, high-performance command-line utility for extracting, cleaning, and formatting YouTube video and playlist transcripts for Large Language Models (ChatGPT, Claude, Gemini, Cursor), AI file uploads, documentation, and RAG pipelines.

**Author:** Pradumon Sahani  
**License:** MIT  

---

## Key Capabilities

- **YouTube Playlist Extraction:** Process entire YouTube playlists into combined or separate files.
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

## Cross-Platform Installation Guide

`ytt` requires **Python 3.8+**. Choose the installation guide for your operating system below.

### 1. Linux (Ubuntu, Debian, Fedora, Arch)

```bash
# Update packages and ensure Git and Python 3 are installed
sudo apt update && sudo apt install -y git python3 python3-pip xclip

# Clone the repository
git clone https://github.com/pradumon14/ytt.git
cd ytt

# Install ytt globally in editable mode
pip install -e .
```
*Note: Installing `xclip` or `wl-copy` enables automatic clipboard copying (`-c`).*

---

### 2. macOS (Terminal / iTerm2)

```bash
# Ensure Git and Python 3 are available (via Xcode tools or Homebrew)
xcode-select --install

# Clone the repository
git clone https://github.com/pradumon14/ytt.git
cd ytt

# Install ytt globally
pip3 install -e .
```
*Note: Clipboard support (`-c`) works natively via macOS `pbcopy`.*

---

### 3. Windows (PowerShell / Command Prompt / WSL)

#### Option A: PowerShell / Command Prompt
```powershell
# Clone the repository
git clone https://github.com/pradumon14/ytt.git
cd ytt

# Install ytt
python -m pip install -e .
```

#### Option B: Windows Subsystem for Linux (WSL)
```bash
git clone https://github.com/pradumon14/ytt.git
cd ytt
pip install -e .
```
*Note: Clipboard support works out of the box on Windows.*

---

### 4. Android (Termux)

```bash
# Update packages and install Python and Git
pkg update && pkg install -y python git termux-api

# Clone the repository
git clone https://github.com/pradumon14/ytt.git
cd ytt

# Install ytt
pip install -e .
```
*Note: Install the Termux:API app from F-Droid for native clipboard integration (`-c`).*

---

### 5. Isolated Installation via `pipx` (Recommended)

`pipx` installs CLI tools in isolated environments while making binaries available system-wide:

```bash
# Install pipx if not already installed
pip install pipx
pipx ensurepath

# Install ytt directly from Git repository
pipx install git+https://github.com/pradumon14/ytt.git
```

---

### 6. Docker Container

For containerized environments or CI/CD pipelines:

```bash
# Build the Docker image
docker build -t ytt .

# Run ytt inside Docker
docker run --rm ytt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

---

## Usage Guide Across Devices

After installation, the commands `ytt`, `ytx`, `yt-transcript`, `yt2md`, and `yt2text` are accessible system-wide.

### Command Syntax

```bash
ytt [options] [inputs ...]
```

### Examples

#### 1. Extract Single Video Transcript
```bash
ytt "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

#### 2. Extract Full Playlist into a Single File for AI Upload
```bash
ytt "https://www.youtube.com/playlist?list=PLAYLIST_ID" --combine -o course_summary.md
```

#### 3. Extract Playlist as Individual Files per Video
```bash
ytt "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o ./transcripts_folder/
```

#### 4. Copy Prompt XML Format Directly to Clipboard
```bash
ytt "https://youtu.be/dQw4w9WgXcQ" -f llm -c
```

#### 5. Search Keywords inside Transcript
```bash
ytt "https://youtu.be/dQw4w9WgXcQ" --search "machine learning"
```

#### 6. Apply AI Prompt Template
```bash
ytt "https://youtu.be/dQw4w9WgXcQ" --template summary
```

#### 7. Interactive Terminal User Guide
```bash
ytt manual
```

---

## Command Reference Table

| Option | Long Flag | Description |
|---|---|---|
| `-o` | `--output` | Output file path (e.g. `doc.md`) or directory path. |
| | `--combine` | Combine playlist transcripts into a single file. |
| `-f` | `--format` | Format style: `markdown` (default), `llm`, `text`, `json`, `jsonl`, `srt`, `vtt`. |
| `-s` | `--search` | Search for keyword or phrase and highlight matches. |
| | `--template` | Apply AI prompt template (`summary`, `qna`, `takeaways`, `flashcards`). |
| `-c` | `--copy` | Copy output directly to system clipboard. |
| | `--no-timestamps` | Exclude timestamps from output. |
| | `--no-metadata` | Exclude header title/URL metadata block. |
| | `--chunk-size` | Split long output into N estimated LLM token blocks. |
| `-l` | `--lang` | Preferred language code(s) (e.g. `en`, `es`). Default: `en`. |
| `-t` | `--translate` | Target language code for auto-translation (e.g. `en`). |
| `-q` | `--quiet` | Quiet mode for unix piping. |
| `-m` | `--manual` | Display interactive user guide. |
| `-v` | `--version` | Display version information and developer credits. |

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

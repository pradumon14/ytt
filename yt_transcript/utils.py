"""
Utility functions for YouTube video ID extraction, playlist resolution, timestamp 
formatting, LLM token estimation, string sanitization, and system clipboard integration.

Author: Pradumon Sahani
"""

import os
import re
import subprocess
import shutil
from typing import List, Dict, Any, Tuple


def is_playlist_url(url_or_id: str) -> bool:
    """
    Determine whether the input string represents a YouTube Playlist URL.

    Args:
        url_or_id (str): Input URL or ID string to check.

    Returns:
        bool: True if input contains playlist markers, False otherwise.
    """
    url_or_id = url_or_id.strip()
    return "list=" in url_or_id or "/playlist" in url_or_id


def extract_playlist_videos(playlist_url: str) -> Dict[str, Any]:
    """
    Extract playlist metadata and constituent video entries using yt-dlp.

    Args:
        playlist_url (str): Valid YouTube playlist URL.

    Returns:
        Dict[str, Any]: Dictionary containing 'title' and 'videos' list.
    """
    import yt_dlp
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        title = info.get('title', 'YouTube Playlist')
        entries = info.get('entries', []) or []
        videos = []
        for idx, entry in enumerate(entries, 1):
            if isinstance(entry, dict) and entry.get('id'):
                videos.append({
                    'index': idx,
                    'id': entry.get('id'),
                    'title': entry.get('title', f'Video {idx}')
                })
        return {
            'title': title,
            'videos': videos
        }


def extract_video_id(url_or_id: str) -> str:
    """
    Extract the standard 11-character YouTube video ID from various URL formats or raw ID.

    Supported formats:
    - Standard URL: https://www.youtube.com/watch?v=VIDEO_ID
    - Short URL: https://youtu.be/VIDEO_ID
    - Shorts URL: https://www.youtube.com/shorts/VIDEO_ID
    - Embed URL: https://www.youtube.com/embed/VIDEO_ID
    - Raw ID: VIDEO_ID (11 characters)

    Args:
        url_or_id (str): Input string containing URL or ID.

    Returns:
        str: 11-character YouTube Video ID.

    Raises:
        ValueError: If video ID cannot be parsed from the input.
    """
    url_or_id = url_or_id.strip()
    
    if len(url_or_id) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
        
    patterns = [
        r'(?:v=|\/v\/|embed\/|shorts\/|live\/)([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
            
    raise ValueError(f"Invalid YouTube URL or Video ID: '{url_or_id}'")


def parse_inputs(inputs: List[str]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Parse command-line inputs including URLs, Video IDs, Playlists, and local URL list files.

    Args:
        inputs (List[str]): Input strings passed via CLI arguments.

    Returns:
        Tuple[List[str], List[Dict[str, Any]]]: Tuple containing:
            - List of individual video IDs.
            - List of resolved playlist metadata dictionaries.
    """
    video_ids = []
    playlists = []
    
    for item in inputs:
        item = item.strip()
        if not item:
            continue
            
        if is_playlist_url(item):
            try:
                p_info = extract_playlist_videos(item)
                playlists.append(p_info)
            except Exception as e:
                print(f"Warning: Could not extract playlist '{item}': {e}")
            continue

        if os.path.isfile(item):
            with open(item, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if is_playlist_url(line):
                            try:
                                p_info = extract_playlist_videos(line)
                                playlists.append(p_info)
                            except Exception:
                                pass
                        else:
                            try:
                                v_id = extract_video_id(line)
                                if v_id not in video_ids:
                                    video_ids.append(v_id)
                            except ValueError:
                                pass
        else:
            try:
                v_id = extract_video_id(item)
                if v_id not in video_ids:
                    video_ids.append(v_id)
            except ValueError:
                print(f"Warning: Could not parse '{item}' as YouTube Video/Playlist URL or ID.")
                
    return video_ids, playlists


def sanitize_filename(name: str) -> str:
    """
    Sanitize input title string for safe file naming across all filesystems.

    Args:
        name (str): Original title string.

    Returns:
        str: Sanitized filename safe for disk creation.
    """
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = re.sub(r'\s+', '_', name).strip('_')
    return name[:80] or "transcript"


def format_timestamp(seconds: float) -> str:
    """
    Convert numerical seconds into formatted HH:MM:SS or MM:SS timestamp string.

    Args:
        seconds (float): Time offset in seconds.

    Returns:
        str: Formatted timestamp string.
    """
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def estimate_tokens(text: str) -> int:
    """
    Estimate Large Language Model (LLM) token count for input text.
    Uses hybrid character and word length ratio heuristic (~4 chars/token, ~0.75 words/token).

    Args:
        text (str): Input text content.

    Returns:
        int: Estimated token count.
    """
    if not text:
        return 0
    words = text.split()
    char_estimate = len(text) / 4.0
    word_estimate = len(words) / 0.75
    return int((char_estimate + word_estimate) / 2)


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard across supported platforms:
    Termux, Linux (xclip/xsel/wl-copy), macOS (pbcopy), Windows, or pyperclip fallback.

    Args:
        text (str): Text content to copy.

    Returns:
        bool: True if successfully copied, False otherwise.
    """
    if shutil.which("termux-clipboard-set"):
        try:
            p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
            return p.returncode == 0
        except Exception:
            pass

    if shutil.which("xclip"):
        try:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
            return p.returncode == 0
        except Exception:
            pass

    if shutil.which("pbcopy"):
        try:
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode('utf-8'))
            return p.returncode == 0
        except Exception:
            pass

    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    return False

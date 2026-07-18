"""
YouTube metadata and transcript extraction engine.

Handles primary caption retrieval via youtube-transcript-api and fallback 
subtitles downloading via yt-dlp.

Author: Pradumon Sahani
"""

import json
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    InvalidVideoId
)


@dataclass
class VideoMetadata:
    """
    Data structure representing YouTube video metadata.
    """
    video_id: str
    title: str
    author: str
    url: str
    author_url: str = ""
    thumbnail_url: str = ""
    duration: float = 0.0


@dataclass
class TranscriptItem:
    """
    Data structure representing an individual transcript segment snippet.
    """
    text: str
    start: float
    duration: float


class TranscriptExtractor:
    """
    Extractor class responsible for fetching video metadata and transcript snippets.
    """
    def __init__(self):
        self.api = YouTubeTranscriptApi()

    def get_metadata(self, video_id: str) -> VideoMetadata:
        """
        Fetch video title, author, and channel details via YouTube oEmbed API.

        Args:
            video_id (str): 11-character YouTube Video ID.

        Returns:
            VideoMetadata: Object containing video details.
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        
        try:
            resp = requests.get(oembed_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return VideoMetadata(
                    video_id=video_id,
                    title=data.get("title", f"YouTube Video ({video_id})"),
                    author=data.get("author_name", "Unknown Channel"),
                    url=url,
                    author_url=data.get("author_url", ""),
                    thumbnail_url=data.get("thumbnail_url", "")
                )
        except Exception:
            pass
            
        return VideoMetadata(
            video_id=video_id,
            title=f"YouTube Video ({video_id})",
            author="Unknown",
            url=url
        )

    def list_languages(self, video_id: str) -> List[Dict[str, Any]]:
        """
        List available manual and auto-generated transcript languages for a video.

        Args:
            video_id (str): 11-character YouTube Video ID.

        Returns:
            List[Dict[str, Any]]: List of dictionaries detailing language options.
        """
        try:
            transcript_list = self.api.list(video_id)
            langs = []
            for t in transcript_list:
                langs.append({
                    "language_code": t.language_code,
                    "language": t.language,
                    "is_generated": t.is_generated,
                    "is_translatable": t.is_translatable
                })
            return langs
        except Exception as e:
            raise RuntimeError(f"Could not list languages for video {video_id}: {e}")

    def fetch_transcript(
        self,
        video_id: str,
        languages: Optional[List[str]] = None,
        translate_to: Optional[str] = None
    ) -> List[TranscriptItem]:
        """
        Fetch transcript snippets for a video with language selection and translation.

        Args:
            video_id (str): 11-character YouTube Video ID.
            languages (Optional[List[str]]): List of preferred language codes.
            translate_to (Optional[str]): Target language code for translation.

        Returns:
            List[TranscriptItem]: Parsed list of transcript item snippets.

        Raises:
            RuntimeError: If transcripts are disabled, missing, or unavailable.
        """
        if languages is None:
            languages = ['en']

        try:
            transcript_list = self.api.list(video_id)
            selected_transcript = None
            
            try:
                selected_transcript = transcript_list.find_transcript(languages)
            except Exception:
                try:
                    selected_transcript = transcript_list.find_generated_transcript(languages)
                except Exception:
                    available = list(transcript_list)
                    if available:
                        selected_transcript = available[0]

            if not selected_transcript:
                raise NoTranscriptFound(video_id, languages, transcript_list)

            if translate_to:
                if selected_transcript.is_translatable:
                    selected_transcript = selected_transcript.translate(translate_to)
                else:
                    raise RuntimeError(f"Transcript in language '{selected_transcript.language_code}' cannot be translated to '{translate_to}'.")

            raw_snippets = selected_transcript.fetch()
            
            items = []
            for s in raw_snippets:
                clean_text = s.text.replace("\n", " ").strip()
                items.append(TranscriptItem(
                    text=clean_text,
                    start=s.start,
                    duration=s.duration
                ))
                
            return items

        except TranscriptsDisabled:
            raise RuntimeError(f"Transcripts are disabled for video '{video_id}'.")
        except NoTranscriptFound:
            raise RuntimeError(f"No transcripts found for video '{video_id}' matching languages {languages}.")
        except VideoUnavailable:
            raise RuntimeError(f"Video '{video_id}' is unavailable or private.")
        except InvalidVideoId:
            raise RuntimeError(f"Invalid Video ID '{video_id}'.")
        except Exception:
            return self._fetch_fallback_ytdlp(video_id, languages)

    def _fetch_fallback_ytdlp(self, video_id: str, languages: List[str]) -> List[TranscriptItem]:
        """
        Fallback transcript extractor using yt-dlp automatic subtitle download.

        Args:
            video_id (str): 11-character YouTube Video ID.
            languages (List[str]): List of preferred language codes.

        Returns:
            List[TranscriptItem]: Extracted transcript items.
        """
        import yt_dlp
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': languages,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                subtitles = info.get('subtitles') or info.get('automatic_captions')
                if not subtitles:
                    raise RuntimeError("No subtitles found via yt-dlp fallback.")
                
                target_lang = languages[0] if languages else 'en'
                sub_tracks = subtitles.get(target_lang) or next(iter(subtitles.values()), None)
                if not sub_tracks:
                    raise RuntimeError(f"No subtitles track found for {target_lang}")

                json_track = next((t for t in sub_tracks if t.get('ext') == 'json3'), None)
                if json_track:
                    resp = requests.get(json_track['url'], timeout=10)
                    data = resp.json()
                    events = data.get('events', [])
                    items = []
                    for ev in events:
                        segs = ev.get('segs', [])
                        text = "".join(s.get('utf8', '') for s in segs).strip()
                        if text and text != '\n':
                            start_ms = ev.get('tStartMs', 0)
                            dur_ms = ev.get('dDurationMs', 0)
                            items.append(TranscriptItem(
                                text=text.replace('\n', ' '),
                                start=start_ms / 1000.0,
                                duration=dur_ms / 1000.0
                            ))
                    if items:
                        return items
                        
        except Exception as err:
            raise RuntimeError(f"Failed to retrieve transcript for video '{video_id}': {err}")

        raise RuntimeError(f"Could not retrieve transcript for video '{video_id}'.")

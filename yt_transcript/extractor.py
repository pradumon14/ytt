import json
import requests
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    InvalidVideoId,
    YouTubeTranscriptApiException
)

@dataclass
class VideoMetadata:
    video_id: str
    title: str
    author: str
    url: str
    author_url: str = ""
    thumbnail_url: str = ""
    duration: float = 0.0

@dataclass
class TranscriptItem:
    text: str
    start: float
    duration: float

class TranscriptExtractor:
    def __init__(self):
        self.api = YouTubeTranscriptApi()

    def get_metadata(self, video_id: str) -> VideoMetadata:
        """
        Fetch video metadata using YouTube oEmbed endpoint (fast and reliable).
        Falls back to default metadata if endpoint is unavailable.
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
        List available transcript languages for a video.
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
        Fetch transcript snippets for a video.
        - languages: priority list of language codes (e.g. ['en', 'es'])
        - translate_to: language code to translate into
        """
        if languages is None:
            languages = ['en']

        try:
            transcript_list = self.api.list(video_id)
            
            selected_transcript = None
            
            # 1. Try finding specified languages (manual or auto)
            try:
                selected_transcript = transcript_list.find_transcript(languages)
            except Exception:
                # 2. Fallback: try finding generated transcript or any available transcript
                try:
                    selected_transcript = transcript_list.find_generated_transcript(languages)
                except Exception:
                    # Pick the first available transcript if none match exact language request
                    available = list(transcript_list)
                    if available:
                        selected_transcript = available[0]

            if not selected_transcript:
                raise NoTranscriptFound(video_id, languages, transcript_list)

            # Check if user requested translation
            if translate_to:
                if selected_transcript.is_translatable:
                    selected_transcript = selected_transcript.translate(translate_to)
                else:
                    raise RuntimeError(f"Transcript in language '{selected_transcript.language_code}' cannot be translated to '{translate_to}'.")

            raw_snippets = selected_transcript.fetch()
            
            items = []
            for s in raw_snippets:
                # Clean html entities or raw line breaks
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
        except Exception as e:
            # Attempt yt-dlp fallback if YouTubeTranscriptApi encounters an unexpected error
            return self._fetch_fallback_ytdlp(video_id, languages)

    def _fetch_fallback_ytdlp(self, video_id: str, languages: List[str]) -> List[TranscriptItem]:
        """
        Fallback transcript extractor using yt-dlp subtitle download.
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
                
                # Pick best matching language
                target_lang = languages[0] if languages else 'en'
                sub_tracks = subtitles.get(target_lang) or next(iter(subtitles.values()), None)
                if not sub_tracks:
                    raise RuntimeError(f"No subtitles track found for {target_lang}")

                # Find json3 or vtt format
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

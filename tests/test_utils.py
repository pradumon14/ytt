import unittest
from yt_transcript.utils import extract_video_id, is_playlist_url, sanitize_filename, estimate_tokens, format_timestamp

class TestUtils(unittest.TestCase):
    def test_extract_video_id(self):
        url1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        url2 = "https://youtu.be/dQw4w9WgXcQ"
        url3 = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        raw_id = "dQw4w9WgXcQ"
        
        self.assertEqual(extract_video_id(url1), "dQw4w9WgXcQ")
        self.assertEqual(extract_video_id(url2), "dQw4w9WgXcQ")
        self.assertEqual(extract_video_id(url3), "dQw4w9WgXcQ")
        self.assertEqual(extract_video_id(raw_id), "dQw4w9WgXcQ")

    def test_is_playlist_url(self):
        pl_url = "https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj"
        normal_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertTrue(is_playlist_url(pl_url))
        self.assertFalse(is_playlist_url(normal_url))

    def test_sanitize_filename(self):
        unsafe = "What is Python? / * : < > |"
        safe = sanitize_filename(unsafe)
        self.assertNotIn("/", safe)
        self.assertNotIn("*", safe)
        self.assertIn("Python", safe)

    def test_format_timestamp(self):
        self.assertEqual(format_timestamp(65.0), "01:05")
        self.assertEqual(format_timestamp(3665.0), "01:01:05")

    def test_estimate_tokens(self):
        text = "Hello world this is a test transcript for LLMs."
        self.assertGreater(estimate_tokens(text), 0)

if __name__ == "__main__":
    unittest.main()

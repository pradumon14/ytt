import unittest
from yt_transcript.extractor import VideoMetadata, TranscriptItem
from yt_transcript.formatter import TranscriptFormatter, chunk_text, reconstruct_paragraphs

class TestFormatter(unittest.TestCase):
    def test_reconstruct_paragraphs(self):
        items = [
            TranscriptItem(text="Hello everyone", start=0.0, duration=1.5),
            TranscriptItem(text="welcome to this tutorial.", start=1.5, duration=2.0),
            TranscriptItem(text="Today we talk about AI.", start=5.0, duration=2.0)
        ]
        paragraphs = reconstruct_paragraphs(items)
        self.assertGreaterEqual(len(paragraphs), 1)
        self.assertIn("Hello everyone", paragraphs[0]["text"])

    def test_formatter_markdown(self):
        meta = VideoMetadata(video_id="test1234567", title="Test Title", author="Test Author", url="https://youtube.com")
        items = [TranscriptItem(text="Sample text line.", start=0.0, duration=1.0)]
        formatter = TranscriptFormatter(meta, items)
        md = formatter.format("markdown")
        self.assertIn("Test Title", md)
        self.assertIn("Sample text line.", md)

    def test_formatter_llm(self):
        meta = VideoMetadata(video_id="test1234567", title="Test Title", author="Test Author", url="https://youtube.com")
        items = [TranscriptItem(text="Sample text line.", start=0.0, duration=1.0)]
        formatter = TranscriptFormatter(meta, items)
        llm_output = formatter.format("llm")
        self.assertIn("<youtube_transcript", llm_output)
        self.assertIn("</youtube_transcript>", llm_output)

    def test_chunk_text(self):
        text = "word " * 1000
        chunks = chunk_text(text, chunk_tokens=200)
        self.assertGreater(len(chunks), 1)

if __name__ == "__main__":
    unittest.main()

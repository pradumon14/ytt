from setuptools import setup, find_packages

setup(
    name="yt-transcript-cli",
    version="1.0.0",
    description="CLI tool to extract, format, and prepare YouTube video transcripts for LLMs and documentation",
    author="Antigravity",
    packages=find_packages(),
    install_requires=[
        "youtube-transcript-api>=1.2.0",
        "rich>=13.0.0",
        "requests>=2.25.0",
        "yt-dlp>=2023.1.0"
    ],
    entry_points={
        "console_scripts": [
            "ytt=yt_transcript.cli:main",
            "ytx=yt_transcript.cli:main",
            "yt-transcript=yt_transcript.cli:main",
            "yt2text=yt_transcript.cli:main",
            "yt2md=yt_transcript.cli:main"
        ],
    },
    python_requires=">=3.8",
)

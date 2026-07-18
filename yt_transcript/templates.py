"""
AI Prompt Templates module for wrapping transcripts in structured LLM prompts.

Author: Pradumon Sahani
"""

from typing import Optional

TEMPLATES = {
    "summary": """---
# AI Prompt: Executive Summary Request

Please read the video transcript below and provide:
1. **Executive Summary** (3-5 concise bullet points summarizing the core message)
2. **Key Concepts and Technical Terms Introduced**
3. **Actionable Takeaways**

---

TRANSCRIPT:
{transcript}
""",
    "qna": """---
# AI Prompt: Question and Answer Extraction

Based strictly on the video transcript provided below, please generate:
1. **Top 5 Frequently Asked Questions (FAQs)** with clear, concise answers derived from the text.
2. **Key Arguments and Explanations** presented in the video.

---

TRANSCRIPT:
{transcript}
""",
    "takeaways": """---
# AI Prompt: Key Takeaways and Action Items

Summarize the key takeaways and actionable points from this video transcript in bulleted format. Group them by topic or timeline section where relevant.

---

TRANSCRIPT:
{transcript}
""",
    "flashcards": """---
# AI Prompt: Flashcards and Study Guide

Convert the following video transcript into a set of **Study Flashcards** formatted as:
- **Q:** [Question / Concept]
- **A:** [Explanation]

---

TRANSCRIPT:
{transcript}
"""
}


def apply_template(transcript: str, template_name: str) -> str:
    """
    Wrap transcript text in a pre-formatted LLM prompt template.

    Args:
        transcript (str): Formatted transcript text.
        template_name (str): Template key (summary, qna, takeaways, flashcards).

    Returns:
        str: Template-wrapped prompt content.
    """
    key = template_name.lower().strip()
    if key not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown prompt template '{template_name}'. Available templates: {available}")
    return TEMPLATES[key].format(transcript=transcript)

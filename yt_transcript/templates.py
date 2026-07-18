from typing import Optional

TEMPLATES = {
    "summary": """---
# 🤖 AI Prompt: Executive Summary Request

Please read the video transcript below and provide:
1. **Executive Summary** (3-5 concise bullet points summarizing the core message)
2. **Key Concepts & Technical Terms Introduced**
3. **Actionable Takeaways**

---

TRANSCRIPT:
{transcript}
""",
    "qna": """---
# 🤖 AI Prompt: Question & Answer Extraction

Based strictly on the video transcript provided below, please generate:
1. **Top 5 Frequently Asked Questions (FAQs)** with clear, concise answers derived from the text.
2. **Key Arguments & Explanations** presented in the video.

---

TRANSCRIPT:
{transcript}
""",
    "takeaways": """---
# 🤖 AI Prompt: Key Takeaways & Action Items

Summarize the key takeaways and actionable points from this video transcript in bulleted format. Group them by topic or timeline section where relevant.

---

TRANSCRIPT:
{transcript}
""",
    "flashcards": """---
# 🤖 AI Prompt: Flashcards & Study Guide

Convert the following video transcript into a set of **Anki/Study Flashcards** formatted as:
- **Q:** [Question / Concept]
- **A:** [Explanation]

---

TRANSCRIPT:
{transcript}
"""
}

def apply_template(transcript: str, template_name: str) -> str:
    """
    Wrap transcript in a pre-formatted LLM prompt template.
    """
    key = template_name.lower().strip()
    if key not in TEMPLATES:
        available = ", ".join(TEMPLATES.keys())
        raise ValueError(f"Unknown prompt template '{template_name}'. Available templates: {available}")
    return TEMPLATES[key].format(transcript=transcript)

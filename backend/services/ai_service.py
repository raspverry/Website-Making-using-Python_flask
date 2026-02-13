"""
AI service using OpenAI API. Model is configurable via AI_MODEL env var.
Currently defaults to gpt-5-mini.
"""

import logging
from typing import Optional

from openai import OpenAI

from backend.config import settings

logger = logging.getLogger(__name__)

# Rule-based fallback fixes
RULE_FIXES = {
    "img-alt": {
        "explanation": "Every image needs alternative text that describes its content or purpose. Screen readers read this text aloud to visually impaired users.",
        "fix_template": 'Add a descriptive alt attribute: <img src="..." alt="Description of what the image shows">. If the image is decorative, use an empty alt: <img src="..." alt="">.',
    },
    "form-label": {
        "explanation": "Form inputs need labels so screen reader users know what information to enter.",
        "fix_template": 'Add a <label> element linked to the input: <label for="input-id">Field Name</label><input id="input-id" ...>.',
    },
    "html-lang": {
        "explanation": "The lang attribute tells screen readers which language to use for pronunciation.",
        "fix_template": 'Add a lang attribute to the <html> tag: <html lang="en">.',
    },
    "page-title": {
        "explanation": "The page title appears in browser tabs and is the first thing a screen reader announces.",
        "fix_template": "Add a descriptive <title> in the <head>: <head><title>Page Name - Site Name</title></head>.",
    },
    "empty-link": {
        "explanation": "Links without text are invisible to screen reader users.",
        "fix_template": 'Add text inside the link, or use aria-label: <a href="..." aria-label="Description">.',
    },
    "empty-button": {
        "explanation": "Buttons without text can't be used by screen reader users.",
        "fix_template": 'Add text inside the button, or use aria-label: <button aria-label="Action">.',
    },
    "heading-order": {
        "explanation": "Headings create an outline of the page. Skipping levels breaks this outline.",
        "fix_template": "Use headings in order: h1 > h2 > h3. Don't skip levels.",
    },
    "skip-nav": {
        "explanation": "A skip navigation link lets keyboard users jump directly to the main content.",
        "fix_template": 'Add a skip link as the first element: <a href="#main-content" class="sr-only">Skip to main content</a>.',
    },
    "landmark-main": {
        "explanation": "Landmark elements like <main> help screen reader users jump to different sections.",
        "fix_template": "Wrap your main content in a <main> element: <main>...your content...</main>.",
    },
    "meta-viewport": {
        "explanation": "Preventing users from zooming makes your site unusable for people with low vision.",
        "fix_template": 'Remove maximum-scale=1 and user-scalable=no from your viewport meta tag.',
    },
}


def get_client() -> Optional[OpenAI]:
    """Get OpenAI client if API key is configured."""
    if not settings.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_fix(rule_id: str, description: str, element_html: str = "") -> str:
    """Generate a fix suggestion. Uses AI if available, falls back to rules."""
    client = get_client()
    
    if client and element_html:
        try:
            return _ai_generate_fix(client, rule_id, description, element_html)
        except Exception as e:
            logger.warning("AI fix generation failed, using fallback: %s", e)
    
    rule_fix = RULE_FIXES.get(rule_id, {})
    explanation = rule_fix.get("explanation", description)
    fix = rule_fix.get("fix_template", "Review and fix according to WCAG 2.2 guidelines.")
    return f"{explanation}\n\nHow to fix: {fix}"


def _ai_generate_fix(client: OpenAI, rule_id: str, description: str, element_html: str) -> str:
    """Generate fix using OpenAI."""
    response = client.chat.completions.create(
        model=settings.AI_MODEL,
        messages=[
            {"role": "user", "content": f"""You are a web accessibility expert. A WCAG violation was found:

Rule: {rule_id}
Issue: {description}
HTML element: {element_html}

Provide:
1. A brief plain-English explanation of why this is a problem (1-2 sentences)
2. The exact code fix (show before/after HTML)

Keep it concise and actionable. No markdown formatting."""}
        ],
        max_tokens=300,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def generate_executive_summary(url: str, score: int, total_violations: int,
                                critical: int, serious: int, moderate: int,
                                violations_text: str) -> str:
    """Generate an executive summary. Uses AI if available."""
    client = get_client()
    
    if client:
        try:
            return _ai_executive_summary(client, url, score, total_violations,
                                          critical, serious, moderate, violations_text)
        except Exception as e:
            logger.warning("AI summary failed, using fallback: %s", e)
    
    return _fallback_summary(url, score, total_violations, critical, serious)


def _ai_executive_summary(client: OpenAI, url: str, score: int, total: int,
                           critical: int, serious: int, moderate: int,
                           violations_text: str) -> str:
    """Generate summary using OpenAI."""
    response = client.chat.completions.create(
        model=settings.AI_MODEL,
        messages=[
            {"role": "user", "content": f"""You are an expert web accessibility consultant. Create a brief executive summary.

Website: {url}
Score: {score}/100
Violations: {total} total ({critical} critical, {serious} serious, {moderate} moderate)
ADA Title II Deadline: April 24, 2026

Top violations:
{violations_text}

Write 3-4 concise paragraphs covering compliance status, critical issues, action plan, and effort estimate.
Plain English for non-technical business owners."""}
        ],
        max_tokens=600,
        temperature=0.4,
    )
    return response.choices[0].message.content or ""


def _fallback_summary(url: str, score: int, total: int, critical: int, serious: int) -> str:
    """Fallback summary without AI."""
    if score >= 90:
        status = f"Your website scored {score}/100. This is excellent."
    elif score >= 70:
        status = f"Your website scored {score}/100. Solid foundation but needs attention before the ADA deadline."
    elif score >= 50:
        status = f"Your website scored {score}/100. Significant gaps that put you at risk."
    else:
        status = f"Your website scored {score}/100. Critical barriers that could result in ADA lawsuits and fines up to $150,000."
    
    issues = f"Found {total} violations: {critical} critical, {serious} serious."
    recommendation = "Fix critical issues first, then serious ones. Re-scan to verify."
    
    return f"{status}\n\n{issues}\n\n{recommendation}"


def answer_question(question: str, url: str, score: int, violations_text: str) -> str:
    """Answer a user's question about accessibility issues."""
    client = get_client()
    
    if client:
        try:
            response = client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "user", "content": f"""You are PageGuard's AI accessibility assistant.

Website: {url}, Score: {score}/100

Violations:
{violations_text}

User question: {question}

Answer directly and concisely. Provide code examples if relevant. Under 200 words."""}
                ],
                max_tokens=400,
                temperature=0.4,
            )
            return response.choices[0].message.content or "Unable to generate response."
        except Exception as e:
            logger.warning("AI Q&A failed: %s", e)
    
    return f"Your site scored {score}/100. Fix critical issues first, then serious ones. Re-scan after fixing."

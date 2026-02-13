"""
AI-powered fix suggestions for accessibility violations.
Uses OpenAI API to generate plain-English explanations and code fixes.
Falls back to rule-based suggestions when API is unavailable.
"""

from flask import current_app

# Pre-built fix suggestions for each rule (fallback when no API key)
RULE_FIXES = {
    "img-alt": {
        "explanation": "Every image needs alternative text that describes its content or purpose. Screen readers read this text aloud to visually impaired users.",
        "fix_template": 'Add a descriptive alt attribute: <img src="..." alt="Description of what the image shows">. If the image is decorative, use an empty alt: <img src="..." alt="">.',
    },
    "form-label": {
        "explanation": "Form inputs need labels so screen reader users know what information to enter. Without labels, a form is essentially unusable for blind users.",
        "fix_template": 'Add a <label> element linked to the input: <label for="input-id">Field Name</label><input id="input-id" ...>. Or use aria-label: <input aria-label="Field Name" ...>.',
    },
    "html-lang": {
        "explanation": "The lang attribute tells screen readers which language to use for pronunciation. Without it, a screen reader might mispronounce every word on the page.",
        "fix_template": 'Add a lang attribute to the <html> tag: <html lang="en"> for English, <html lang="es"> for Spanish, <html lang="ko"> for Korean, etc.',
    },
    "page-title": {
        "explanation": "The page title appears in browser tabs and is the first thing a screen reader announces. It helps users identify pages and navigate between tabs.",
        "fix_template": "Add a descriptive <title> in the <head>: <head><title>Page Name - Site Name</title></head>. Make each page's title unique and descriptive.",
    },
    "empty-link": {
        "explanation": "Links without text are invisible to screen reader users. They hear 'link' but have no idea where the link goes.",
        "fix_template": 'Add text inside the link, or use aria-label: <a href="..." aria-label="Description of destination">. If the link contains only an icon, add a <span class="sr-only">Description</span> inside it.',
    },
    "empty-button": {
        "explanation": "Buttons without text can't be used by screen reader users because they don't know what action the button performs.",
        "fix_template": 'Add text inside the button, or use aria-label: <button aria-label="Close menu">X</button>. For icon-only buttons, always include aria-label.',
    },
    "heading-order": {
        "explanation": "Headings create an outline of the page. Skipping levels (e.g., h1 to h3) breaks this outline and makes navigation confusing for screen reader users who jump between headings.",
        "fix_template": "Use headings in order: h1 > h2 > h3. Don't skip levels. Use CSS to style headings instead of choosing heading levels based on visual size.",
    },
    "skip-nav": {
        "explanation": "A skip navigation link lets keyboard users jump directly to the main content, skipping the navigation menu. Without it, they must tab through every menu item on every page.",
        "fix_template": 'Add a skip link as the first element in <body>: <a href="#main-content" class="sr-only focus:not-sr-only">Skip to main content</a>. Then add id="main-content" to your main content area.',
    },
    "landmark-main": {
        "explanation": "Landmark elements like <main> help screen reader users jump to different sections of the page. Without <main>, they can't quickly find the primary content.",
        "fix_template": "Wrap your main content in a <main> element: <main>...your content...</main>. Also consider using <nav>, <header>, <footer>, and <aside> for other sections.",
    },
    "meta-viewport": {
        "explanation": "Preventing users from zooming makes your site unusable for people with low vision who need to enlarge text to read it.",
        "fix_template": 'Remove maximum-scale=1 and user-scalable=no from your viewport meta tag. Use: <meta name="viewport" content="width=device-width, initial-scale=1">.',
    },
}


def generate_fix(violation_rule_id, violation_description, element_html=""):
    """Generate a fix suggestion for a violation. Uses AI if available, falls back to rules."""
    api_key = current_app.config.get("OPENAI_API_KEY", "")

    # Use AI if API key is configured
    if api_key and element_html:
        try:
            return _ai_generate_fix(api_key, violation_rule_id, violation_description, element_html)
        except Exception:
            pass  # Fall through to rule-based

    # Rule-based fallback
    rule_fix = RULE_FIXES.get(violation_rule_id, {})
    explanation = rule_fix.get("explanation", violation_description)
    fix = rule_fix.get("fix_template", "Review and fix this accessibility issue according to WCAG 2.2 guidelines.")

    return f"{explanation}\n\nHow to fix: {fix}"


def _ai_generate_fix(api_key, rule_id, description, element_html):
    """Call OpenAI API to generate a contextual fix suggestion."""
    import json
    import requests as req

    prompt = f"""You are a web accessibility expert. A WCAG violation was found:

Rule: {rule_id}
Issue: {description}
HTML element: {element_html}

Provide:
1. A brief plain-English explanation of why this is a problem (1-2 sentences)
2. The exact code fix (show before/after HTML)

Keep it concise and actionable. No markdown formatting."""

    resp = req.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.3,
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]

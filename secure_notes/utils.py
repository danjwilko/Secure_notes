# secure_notes/utils.py

import bleach
import markdown

ALLOWED_TAGS = [
    "p", "br",
    "strong", "em",
    "ul", "ol", "li",
    "code", "pre",
    "blockquote",
    "h1", "h2", "h3",
    "a",
    "table", "thead", "tbody", "tr", "th", "td"
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}

def render_markdown(text):
    html = markdown.markdown(
        text,
        extensions=[
            "fenced_code",
            "tables",
            "nl2br",
        ],
    )

    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )

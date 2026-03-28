"""
Plugin: tools/text
Text utilities: word count, case convert, reverse, slug, etc.
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import re, unicodedata

router = APIRouter()

META = {
    "name": "Text Tools",
    "description": "Text utilities: analyze, transform, convert text",
    "endpoints": [
        {
            "path": "/analyze",
            "method": "GET",
            "description": "Analyze text — word count, char count, sentences",
            "params": {"text": "Text to analyze"},
            "example": "/api/tools/text/analyze?text=Hello+World",
        },
        {
            "path": "/case",
            "method": "GET",
            "description": "Convert text case",
            "params": {
                "text": "Input text",
                "to": "Target case: upper / lower / title / snake / camel / kebab",
            },
            "example": "/api/tools/text/case?text=hello+world&to=title",
        },
        {
            "path": "/slug",
            "method": "GET",
            "description": "Convert text to URL-friendly slug",
            "params": {"text": "Text to slugify"},
            "example": "/api/tools/text/slug?text=Hello+World+2024",
        },
        {
            "path": "/reverse",
            "method": "GET",
            "description": "Reverse a string",
            "params": {"text": "Text to reverse"},
            "example": "/api/tools/text/reverse?text=NexAPI",
        },
    ],
}


@router.get("/analyze", summary="Analyze Text")
async def analyze(text: str = Query(...)):
    words     = len(text.split())
    sentences = len(re.findall(r'[.!?]+', text)) or (1 if text.strip() else 0)
    paragraphs= len([p for p in text.split("\n\n") if p.strip()])
    reading_time = max(1, round(words / 200))  # avg 200 wpm
    return {
        "status": True,
        "creator": "NexAPI",
        "data": {
            "characters":           len(text),
            "characters_no_spaces": len(text.replace(" ", "")),
            "words":                words,
            "sentences":            sentences,
            "paragraphs":           max(1, paragraphs),
            "lines":                text.count("\n") + 1,
            "reading_time_min":     reading_time,
        },
    }


@router.get("/case", summary="Convert Case")
async def convert_case(
    text: str = Query(...),
    to:   str = Query(..., description="upper | lower | title | snake | camel | kebab"),
):
    to = to.lower()
    result = text
    if to == "upper":  result = text.upper()
    elif to == "lower": result = text.lower()
    elif to == "title": result = text.title()
    elif to == "snake":
        result = re.sub(r'[\s\-]+', '_', text).lower()
    elif to == "camel":
        words = re.split(r'[\s_\-]+', text)
        result = words[0].lower() + ''.join(w.capitalize() for w in words[1:])
    elif to == "kebab":
        result = re.sub(r'[\s_]+', '-', text).lower()
    else:
        return JSONResponse({"status": False, "message": "Invalid case type"}, status_code=400)
    return {
        "status": True,
        "creator": "NexAPI",
        "data": {"input": text, "output": result, "case": to},
    }


@router.get("/slug", summary="Slugify Text")
async def slugify(text: str = Query(...)):
    # Normalize unicode
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode()
    slug = re.sub(r'[^\w\s-]', '', ascii_text).strip().lower()
    slug = re.sub(r'[\s_-]+', '-', slug)
    return {
        "status": True,
        "creator": "NexAPI",
        "data": {"input": text, "slug": slug},
    }


@router.get("/reverse", summary="Reverse String")
async def reverse(text: str = Query(...)):
    return {
        "status": True,
        "creator": "NexAPI",
        "data": {"input": text, "reversed": text[::-1]},
    }

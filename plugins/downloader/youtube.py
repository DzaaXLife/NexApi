"""
Plugin: downloader/youtube
Get YouTube video info and download links via yt-dlp style API
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx, re

router = APIRouter()

META = {
    "name": "YouTube Downloader",
    "description": "Get YouTube video/audio download links",
    "endpoints": [
        {
            "path": "/",
            "method": "GET",
            "description": "Get YouTube video info and download links",
            "params": {"url": "YouTube video URL"},
            "example": "/api/downloader/youtube?url=https://youtu.be/xxxx",
        }
    ],
}


def extract_video_id(url: str) -> str | None:
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/)([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


@router.get("/", summary="YouTube Downloader")
async def youtube_dl(url: str = Query(..., description="YouTube video URL")):
    """Get YouTube video info and download links."""

    vid = extract_video_id(url)
    if not vid:
        return JSONResponse({"status": False, "message": "Invalid YouTube URL"}, status_code=400)

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            # Use cobalt.tools public API (open source)
            res = await client.post(
                "https://api.cobalt.tools/",
                json={"url": url, "vQuality": "720"},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
            )
            cobalt = res.json()

        # Also get basic info from noembed
        async with httpx.AsyncClient(timeout=10) as client:
            info_res = await client.get(
                f"https://noembed.com/embed?url=https://www.youtube.com/watch?v={vid}"
            )
            info = info_res.json()

        download_url = cobalt.get("url") or cobalt.get("tunnel")
        status = cobalt.get("status")

        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "video_id": vid,
                "title":    info.get("title", "Unknown"),
                "author":   info.get("author_name", "Unknown"),
                "thumbnail": f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg",
                "embed_url": f"https://www.youtube.com/embed/{vid}",
                "download": {
                    "url":    download_url,
                    "status": status,
                    "note":   "Direct download link (expires). Use within 1 hour.",
                } if download_url else {
                    "status": "unavailable",
                    "note": "Download unavailable for this video",
                },
            },
        }

    except httpx.TimeoutException:
        return JSONResponse({"status": False, "message": "Request timeout"}, status_code=504)
    except Exception as e:
        return JSONResponse({"status": False, "message": str(e)}, status_code=500)

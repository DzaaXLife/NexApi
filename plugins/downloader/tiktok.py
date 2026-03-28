"""
Plugin: downloader/tiktok
Scrapes TikTok video info & download link (no watermark via tikwm.com API)
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx, time

router = APIRouter()

META = {
    "name": "TikTok Downloader",
    "description": "Download TikTok video without watermark",
    "endpoints": [
        {
            "path": "/",
            "method": "GET",
            "description": "Get TikTok video download link",
            "params": {"url": "TikTok video URL"},
            "example": "/api/downloader/tiktok?url=https://vm.tiktok.com/xxxx",
        }
    ],
}


@router.get("/", summary="TikTok Downloader")
async def tiktok_dl(url: str = Query(..., description="TikTok video URL")):
    """
    Download TikTok video without watermark.
    Uses tikwm.com public API.
    """
    if not url:
        return JSONResponse({"status": False, "message": "URL is required"}, status_code=400)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(
                "https://www.tikwm.com/api/",
                data={"url": url, "count": 12, "cursor": 0, "hd": 1},
            )
            data = res.json()

        if data.get("code") != 0:
            return JSONResponse({
                "status": False,
                "message": data.get("msg", "Failed to fetch video"),
            }, status_code=400)

        d = data["data"]
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "id":        d.get("id"),
                "title":     d.get("title"),
                "duration":  d.get("duration"),
                "author": {
                    "username": d.get("author", {}).get("unique_id"),
                    "nickname": d.get("author", {}).get("nickname"),
                    "avatar":   d.get("author", {}).get("avatar"),
                },
                "stats": {
                    "plays":   d.get("play_count"),
                    "likes":   d.get("digg_count"),
                    "comments":d.get("comment_count"),
                    "shares":  d.get("share_count"),
                },
                "download": {
                    "nowatermark": f"https://www.tikwm.com{d.get('play')}",
                    "watermark":   f"https://www.tikwm.com{d.get('wmplay')}",
                    "audio":       f"https://www.tikwm.com{d.get('music')}",
                    "cover":       f"https://www.tikwm.com{d.get('cover')}",
                },
            },
        }

    except httpx.TimeoutException:
        return JSONResponse({"status": False, "message": "Request timeout"}, status_code=504)
    except Exception as e:
        return JSONResponse({"status": False, "message": str(e)}, status_code=500)

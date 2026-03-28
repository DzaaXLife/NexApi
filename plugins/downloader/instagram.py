"""
Plugin: downloader/instagram
Download Instagram reels/photos via instaloader-compatible scraping
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx, re, json

router = APIRouter()

META = {
    "name": "Instagram Downloader",
    "description": "Download Instagram Reels, Photos, and Videos",
    "endpoints": [
        {
            "path": "/",
            "method": "GET",
            "description": "Get Instagram media download link",
            "params": {"url": "Instagram post/reel URL"},
            "example": "/api/downloader/instagram?url=https://www.instagram.com/reel/xxxx",
        }
    ],
}


@router.get("/", summary="Instagram Downloader")
async def instagram_dl(url: str = Query(..., description="Instagram post/reel/photo URL")):
    """Download Instagram Reels, Photos, Videos."""

    if not url or "instagram.com" not in url:
        return JSONResponse({"status": False, "message": "Invalid Instagram URL"}, status_code=400)

    try:
        # Use snapinsta public API approach
        async with httpx.AsyncClient(
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
        ) as client:
            # Try using a public scraping approach via saveinsta
            res = await client.post(
                "https://v3.saveinsta.app/api/ajaxSearch",
                data={"q": url, "t": "media", "lang": "en"},
                headers={"X-Requested-With": "XMLHttpRequest"},
            )
            data = res.json()

        if data.get("status") != "ok":
            return JSONResponse({
                "status": False,
                "message": "Could not fetch media. Try with a public post.",
            }, status_code=400)

        # Parse links from HTML response
        html = data.get("data", "")
        links = re.findall(r'href="(https://[^"]+\.(?:mp4|jpg|jpeg|png)[^"]*)"', html)
        types = ["video" if ".mp4" in l else "image" for l in links]

        if not links:
            return JSONResponse({"status": False, "message": "No media found"}, status_code=404)

        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "url": url,
                "media": [{"type": t, "url": l} for t, l in zip(types, links)],
            },
        }

    except httpx.TimeoutException:
        return JSONResponse({"status": False, "message": "Request timeout"}, status_code=504)
    except Exception as e:
        return JSONResponse({"status": False, "message": str(e)}, status_code=500)

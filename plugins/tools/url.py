"""
Plugin: tools/url
URL utilities: expand short URLs, validate, parse
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import httpx
import urllib.parse

router = APIRouter()

META = {
    "name": "URL Tools",
    "description": "Expand short URLs, validate and parse any URL",
    "endpoints": [
        {
            "path": "/expand",
            "method": "GET",
            "description": "Expand a shortened URL to its final destination",
            "params": {"url": "Shortened URL (bit.ly, tinyurl, etc.)"},
            "example": "/api/tools/url/expand?url=https://bit.ly/xxxx",
        },
        {
            "path": "/parse",
            "method": "GET",
            "description": "Parse URL components (scheme, host, path, params)",
            "params": {"url": "Any URL to parse"},
            "example": "/api/tools/url/parse?url=https://example.com/path?foo=bar",
        },
        {
            "path": "/validate",
            "method": "GET",
            "description": "Check if a URL is reachable",
            "params": {"url": "URL to check"},
            "example": "/api/tools/url/validate?url=https://example.com",
        },
    ],
}


@router.get("/expand", summary="Expand Short URL")
async def expand(url: str = Query(..., description="Short URL to expand")):
    try:
        async with httpx.AsyncClient(
            timeout=10,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as client:
            res = await client.head(url)
            final_url = str(res.url)
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "original": url,
                "expanded": final_url,
                "hops": len(res.history) + 1,
                "redirected": final_url != url,
            },
        }
    except Exception as e:
        return JSONResponse({"status": False, "message": str(e)}, status_code=400)


@router.get("/parse", summary="Parse URL")
async def parse(url: str = Query(..., description="URL to parse")):
    try:
        parsed = urllib.parse.urlparse(url)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "url":      url,
                "scheme":   parsed.scheme,
                "host":     parsed.netloc,
                "path":     parsed.path,
                "params":   params,
                "fragment": parsed.fragment or None,
                "is_secure": parsed.scheme == "https",
            },
        }
    except Exception as e:
        return JSONResponse({"status": False, "message": str(e)}, status_code=400)


@router.get("/validate", summary="Validate / Check URL")
async def validate(url: str = Query(..., description="URL to check")):
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            res = await client.head(url, headers={"User-Agent": "Mozilla/5.0"})
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "url":         url,
                "reachable":   True,
                "status_code": res.status_code,
                "final_url":   str(res.url),
                "content_type": res.headers.get("content-type"),
            },
        }
    except Exception as e:
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "url":       url,
                "reachable": False,
                "error":     str(e),
            },
        }

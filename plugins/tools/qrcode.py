"""
Plugin: tools/qrcode
Generate QR codes from text or URL
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, RedirectResponse
import urllib.parse

router = APIRouter()

META = {
    "name": "QR Code Generator",
    "description": "Generate QR code image from any text or URL",
    "endpoints": [
        {
            "path": "/",
            "method": "GET",
            "description": "Generate QR code — returns redirect to image",
            "params": {
                "text": "Text or URL to encode",
                "size": "Image size in pixels (default: 300)",
                "color": "Foreground color hex (default: 000000)",
                "bg": "Background color hex (default: ffffff)",
            },
            "example": "/api/tools/qrcode?text=https://example.com",
        },
        {
            "path": "/json",
            "method": "GET",
            "description": "Returns QR code URL as JSON",
            "params": {"text": "Text or URL to encode"},
            "example": "/api/tools/qrcode/json?text=hello+world",
        },
    ],
}


def build_qr_url(text: str, size: int, color: str, bg: str) -> str:
    encoded = urllib.parse.quote(text)
    color = color.lstrip("#")
    bg = bg.lstrip("#")
    return f"https://api.qrserver.com/v1/create-qr-code/?data={encoded}&size={size}x{size}&color={color}&bgcolor={bg}&format=png"


@router.get("/", summary="Generate QR Code (image redirect)")
async def qr_image(
    text:  str = Query(..., description="Text or URL to encode"),
    size:  int = Query(300, ge=100, le=1000, description="Size in pixels"),
    color: str = Query("000000", description="Foreground color hex"),
    bg:    str = Query("ffffff", description="Background color hex"),
):
    """Returns a redirect to the generated QR code PNG image."""
    url = build_qr_url(text, size, color, bg)
    return RedirectResponse(url)


@router.get("/json", summary="Generate QR Code (JSON)")
async def qr_json(
    text:  str = Query(..., description="Text or URL to encode"),
    size:  int = Query(300, ge=100, le=1000),
    color: str = Query("000000"),
    bg:    str = Query("ffffff"),
):
    """Returns QR code image URL as JSON."""
    url = build_qr_url(text, size, color, bg)
    return {
        "status": True,
        "creator": "NexAPI",
        "data": {
            "text":      text,
            "qr_url":    url,
            "size":      f"{size}x{size}",
            "color":     f"#{color.lstrip('#')}",
            "bg_color":  f"#{bg.lstrip('#')}",
        },
    }

"""
Plugin: tools/base64
Encode and decode Base64 strings
"""

from fastapi import APIRouter, Query, Body
from fastapi.responses import JSONResponse
import base64 as b64lib

router = APIRouter()

META = {
    "name": "Base64 Encoder/Decoder",
    "description": "Encode or decode Base64 strings",
    "endpoints": [
        {
            "path": "/encode",
            "method": "GET",
            "description": "Encode text to Base64",
            "params": {"text": "Plain text to encode"},
            "example": "/api/tools/base64/encode?text=Hello+World",
        },
        {
            "path": "/decode",
            "method": "GET",
            "description": "Decode Base64 to text",
            "params": {"text": "Base64 string to decode"},
            "example": "/api/tools/base64/decode?text=SGVsbG8gV29ybGQ=",
        },
    ],
}


@router.get("/encode", summary="Encode to Base64")
async def encode(text: str = Query(..., description="Text to encode")):
    try:
        encoded = b64lib.b64encode(text.encode()).decode()
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "input":   text,
                "encoded": encoded,
                "length":  len(encoded),
            },
        }
    except Exception as e:
        return JSONResponse({"status": False, "message": str(e)}, status_code=400)


@router.get("/decode", summary="Decode from Base64")
async def decode(text: str = Query(..., description="Base64 string to decode")):
    try:
        # Pad if needed
        padded = text + "=" * (-len(text) % 4)
        decoded = b64lib.b64decode(padded).decode("utf-8")
        return {
            "status": True,
            "creator": "NexAPI",
            "data": {
                "input":   text,
                "decoded": decoded,
                "length":  len(decoded),
            },
        }
    except Exception as e:
        return JSONResponse({"status": False, "message": f"Invalid Base64: {e}"}, status_code=400)

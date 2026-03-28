# NexAPI — Free Public REST API

Plugin-based public API service built with FastAPI.  
No login, no API key, no rate limit. Just request and get JSON back.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Then open: **http://localhost:8000**

---

## 📁 Project Structure

```
nexapi/
├── main.py                        # App entry point + plugin loader
├── requirements.txt
├── templates/
│   └── index.html                 # Landing page (auto-generated from registry)
├── static/                        # CSS / JS assets
└── plugins/
    ├── downloader/
    │   ├── tiktok.py              # GET /api/downloader/tiktok?url=...
    │   ├── instagram.py           # GET /api/downloader/instagram?url=...
    │   └── youtube.py             # GET /api/downloader/youtube?url=...
    └── tools/
        ├── qrcode.py              # GET /api/tools/qrcode?text=...
        ├── base64.py              # GET /api/tools/base64/encode?text=...
        ├── url.py                 # GET /api/tools/url/expand?url=...
        └── text.py                # GET /api/tools/text/analyze?text=...
```

---

## 🔌 Adding a New Plugin

1. Create a file: `plugins/{category}/{feature}.py`
2. Define a FastAPI `router` and a `META` dict
3. Restart the server — it auto-discovers everything

### Plugin Template

```python
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()

META = {
    "name": "My Feature",
    "description": "What this plugin does",
    "endpoints": [
        {
            "path": "/",
            "method": "GET",
            "description": "Main endpoint",
            "params": {"q": "Search query"},
            "example": "/api/mycategory/myfeature?q=hello",
        }
    ],
}

@router.get("/", summary="My Endpoint")
async def my_endpoint(q: str = Query(...)):
    return {
        "status": True,
        "creator": "NexAPI",
        "data": {"result": q}
    }
```

---

## 📡 Available Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/downloader/tiktok?url=` | TikTok no-watermark download |
| GET | `/api/downloader/instagram?url=` | Instagram reels/photos |
| GET | `/api/downloader/youtube?url=` | YouTube video download |
| GET | `/api/tools/qrcode?text=` | Generate QR code (image) |
| GET | `/api/tools/qrcode/json?text=` | Generate QR code (JSON) |
| GET | `/api/tools/base64/encode?text=` | Base64 encode |
| GET | `/api/tools/base64/decode?text=` | Base64 decode |
| GET | `/api/tools/url/expand?url=` | Expand short URL |
| GET | `/api/tools/url/parse?url=` | Parse URL components |
| GET | `/api/tools/url/validate?url=` | Check if URL is reachable |
| GET | `/api/tools/text/analyze?text=` | Word/char count |
| GET | `/api/tools/text/case?text=&to=` | Convert case |
| GET | `/api/tools/text/slug?text=` | Slugify text |
| GET | `/api/tools/text/reverse?text=` | Reverse string |
| GET | `/api/registry` | List all endpoints |
| GET | `/ping` | Health check |
| GET | `/docs` | Swagger UI |

---

## 🌍 Deploy

```bash
# Production
uvicorn main:app --host 0.0.0.0 --port 80 --workers 4

# With Docker (create Dockerfile)
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

"""
NexAPI - Public API Service
Plugin-based architecture: plugins/{category}/{feature}.py
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import importlib, pkgutil, time, os, sys

# ── App ────────────────────────────────────────────────────
app = FastAPI(
    title="NexAPI",
    description="Free public API service — plugin-based",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── Plugin Registry ───────────────────────────────────────
PLUGIN_DIR = "plugins"
registry: dict[str, list[dict]] = {}   # category -> [endpoint_info]

def load_plugins():
    """Auto-discover and mount all plugins from plugins/{category}/{feature}.py"""
    plugins_path = os.path.join(os.path.dirname(__file__), PLUGIN_DIR)
    sys.path.insert(0, os.path.dirname(__file__))

    for category in sorted(os.listdir(plugins_path)):
        cat_path = os.path.join(plugins_path, category)
        if not os.path.isdir(cat_path) or category.startswith("_"):
            continue

        registry[category] = []

        for finder, name, _ in pkgutil.iter_modules([cat_path]):
            module = importlib.import_module(f"plugins.{category}.{name}")

            # Each plugin module exposes: router, META dict
            if hasattr(module, "router"):
                app.include_router(
                    module.router,
                    prefix=f"/api/{category}/{name}",
                    tags=[category.capitalize()],
                )

            if hasattr(module, "META"):
                info = module.META.copy()
                info["category"] = category
                info["feature"]  = name
                info["base_path"] = f"/api/{category}/{name}"
                registry[category].append(info)

load_plugins()

# ── API: Registry endpoint ────────────────────────────────
@app.get("/api/registry", tags=["System"])
def get_registry():
    """Returns all available endpoints grouped by category."""
    total = sum(len(v) for v in registry.values())
    return {
        "status": "ok",
        "total_endpoints": total,
        "categories": registry,
    }

# ── Landing page ──────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "registry": registry,
    })

# ── Health check ──────────────────────────────────────────
@app.get("/ping", tags=["System"])
def ping():
    return {"status": "ok", "timestamp": int(time.time())}

"""
CrimeVision.kz - Интеллектуальная система пространственно-временного анализа
и прогнозирования преступности по регионам Республики Казахстан
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import uvicorn
from pathlib import Path

from app.api import router as api_router
from app.database import init_db

app = FastAPI(
    title="CrimeVision.kz",
    description="Система анализа и прогнозирования преступности",
    version="1.0.0"
)

# Подключение роутеров
app.include_router(api_router, prefix="/api", tags=["api"])

# Статические файлы и шаблоны
static_dir = Path("static")
templates_dir = Path("templates")

static_dir.mkdir(exist_ok=True)
templates_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске"""
    init_db()
    print("✅ CrimeVision.kz запущен!")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Главная страница"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "ok", "service": "CrimeVision.kz"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


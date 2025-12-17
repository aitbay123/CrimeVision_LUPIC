"""
API endpoints для CrimeVision.kz
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime, timedelta
import pandas as pd
import json

from app.database import get_db_connection
from app.services.ml_service import MLService
from app.services.gis_service import GISService
from app.services.data_service import DataService

router = APIRouter()

ml_service = MLService()
gis_service = GISService()
data_service = DataService()


@router.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    """Загрузка CSV файла с данными о преступлениях"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Требуется CSV файл")
        
        df = pd.read_csv(file.file)
        result = data_service.save_to_db(df)
        
        return {
            "status": "success",
            "message": f"Загружено {result['count']} записей",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_summary_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None
):
    """Получить общую статистику"""
    try:
        stats = data_service.get_summary_stats(start_date, end_date, region)
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crimes")
async def get_crimes(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    crime_type: Optional[str] = None,
    limit: int = 1000
):
    """Получить список преступлений с фильтрами"""
    try:
        crimes = data_service.get_crimes(
            start_date, end_date, region, crime_type, limit
        )
        return JSONResponse(content={"crimes": crimes})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
async def get_heatmap_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None
):
    """Получить данные для тепловой карты"""
    try:
        heatmap_data = gis_service.get_heatmap_data(
            start_date, end_date, region
        )
        return JSONResponse(content=heatmap_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/map")
async def get_map_html(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None
):
    """Получить HTML с картой"""
    try:
        map_html = gis_service.generate_map(
            start_date, end_date, region
        )
        return JSONResponse(content={"map_html": map_html})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/timeline")
async def get_timeline(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    group_by: str = "month"
):
    """Получить динамику преступности по времени"""
    try:
        timeline = data_service.get_timeline(
            start_date, end_date, region, group_by
        )
        return JSONResponse(content=timeline)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/regions")
async def get_regions_comparison(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Сравнение регионов"""
    try:
        comparison = data_service.get_regions_comparison(start_date, end_date)
        return JSONResponse(content=comparison)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_forecast(
    region: Optional[str] = None,
    crime_type: Optional[str] = None,
    months: int = 3
):
    """Получить прогноз преступности"""
    try:
        forecast = ml_service.get_forecast(region, crime_type, months)
        return JSONResponse(content=forecast)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-assessment")
async def get_risk_assessment(
    region: Optional[str] = None
):
    """Оценка уровня риска по региону"""
    try:
        risk = ml_service.assess_risk(region)
        return JSONResponse(content=risk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions")
async def get_regions_list():
    """Список доступных регионов"""
    try:
        regions = data_service.get_regions_list()
        return JSONResponse(content={"regions": regions})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crime-types")
async def get_crime_types():
    """Список типов преступлений"""
    try:
        crime_types = data_service.get_crime_types()
        return JSONResponse(content={"crime_types": crime_types})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


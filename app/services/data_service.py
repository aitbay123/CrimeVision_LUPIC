"""
Сервис для работы с данными о преступлениях
"""
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import pandas as pd
from app.database import get_db_connection

REGIONS_KZ = {
    "Алматы": {"lat": 43.2220, "lon": 76.8512},
    "Астана": {"lat": 51.1694, "lon": 71.4491},
    "Шымкент": {"lat": 42.3419, "lon": 69.5901},
    "Алматинская область": {"lat": 45.0170, "lon": 78.3800},
    "Акмолинская область": {"lat": 51.1694, "lon": 71.4491},
    "Актюбинская область": {"lat": 50.2833, "lon": 57.1667},
    "Атырауская область": {"lat": 47.1167, "lon": 51.8833},
    "Западно-Казахстанская область": {"lat": 51.2364, "lon": 51.3760},
    "Жамбылская область": {"lat": 42.9000, "lon": 71.3667},
    "Карагандинская область": {"lat": 49.8014, "lon": 73.1059},
    "Костанайская область": {"lat": 53.2144, "lon": 63.6246},
    "Кызылординская область": {"lat": 44.8528, "lon": 65.5092},
    "Мангистауская область": {"lat": 43.6500, "lon": 51.1667},
    "Павлодарская область": {"lat": 52.2833, "lon": 76.9667},
    "Северо-Казахстанская область": {"lat": 54.8667, "lon": 69.1500},
    "Туркестанская область": {"lat": 43.3000, "lon": 68.2500},
    "Восточно-Казахстанская область": {"lat": 49.9789, "lon": 82.6103},
}


class DataService:
    """Сервис для работы с данными"""
    
    def save_to_db(self, df: pd.DataFrame) -> Dict:
        """Сохранить DataFrame в базу данных"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            try:
                # Определяем координаты региона
                region = row.get('region', 'Алматы')
                coords = REGIONS_KZ.get(region, REGIONS_KZ["Алматы"])
                
                cursor.execute("""
                    INSERT INTO crimes (date, region, city, crime_type, latitude, longitude, severity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    row.get('date', datetime.now().date()),
                    region,
                    row.get('city', ''),
                    row.get('crime_type', 'Другое'),
                    row.get('latitude', coords['lat']),
                    row.get('longitude', coords['lon']),
                    row.get('severity', 1)
                ))
                count += 1
            except Exception as e:
                print(f"Ошибка при сохранении записи: {e}")
                continue
        
        conn.commit()
        conn.close()
        return {"count": count}
    
    def get_summary_stats(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         region: Optional[str] = None) -> Dict:
        """Получить общую статистику"""
        conn = get_db_connection()
        
        query = "SELECT COUNT(*) as total, AVG(severity) as avg_severity FROM crimes WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if region:
            query += " AND region = ?"
            params.append(region)
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        row = cursor.fetchone()
        
        # Статистика по типам преступлений
        type_query = query.replace("COUNT(*) as total, AVG(severity) as avg_severity", 
                                  "crime_type, COUNT(*) as count")
        type_query += " GROUP BY crime_type"
        
        cursor.execute(type_query, params)
        crime_types = [{"type": r[0], "count": r[1]} for r in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total": row[0] or 0,
            "avg_severity": round(row[1] or 0, 2),
            "crime_types": crime_types
        }
    
    def get_crimes(self, start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   region: Optional[str] = None,
                   crime_type: Optional[str] = None,
                   limit: int = 1000) -> List[Dict]:
        """Получить список преступлений"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM crimes WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if region:
            query += " AND region = ?"
            params.append(region)
        if crime_type:
            query += " AND crime_type = ?"
            params.append(crime_type)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        crimes = []
        for row in rows:
            crimes.append({
                "id": row[0],
                "date": row[1],
                "region": row[2],
                "city": row[3],
                "crime_type": row[4],
                "latitude": row[5],
                "longitude": row[6],
                "severity": row[7]
            })
        
        conn.close()
        return crimes
    
    def get_timeline(self, start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    region: Optional[str] = None,
                    group_by: str = "month") -> Dict:
        """Получить динамику по времени"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if group_by == "month":
            date_format = "strftime('%Y-%m', date)"
        elif group_by == "week":
            date_format = "strftime('%Y-W%W', date)"
        else:
            date_format = "date"
        
        query = f"""
            SELECT {date_format} as period, COUNT(*) as count, AVG(severity) as avg_severity
            FROM crimes WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if region:
            query += " AND region = ?"
            params.append(region)
        
        query += f" GROUP BY {date_format} ORDER BY period"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        timeline = {
            "periods": [r[0] for r in rows],
            "counts": [r[1] for r in rows],
            "avg_severity": [round(r[2] or 0, 2) for r in rows]
        }
        
        conn.close()
        return timeline
    
    def get_regions_comparison(self, start_date: Optional[str] = None,
                              end_date: Optional[str] = None) -> Dict:
        """Сравнение регионов"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT region, COUNT(*) as count, AVG(severity) as avg_severity
            FROM crimes WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " GROUP BY region ORDER BY count DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        comparison = {
            "regions": [r[0] for r in rows],
            "counts": [r[1] for r in rows],
            "avg_severity": [round(r[2] or 0, 2) for r in rows]
        }
        
        conn.close()
        return comparison
    
    def get_regions_list(self) -> List[str]:
        """Список регионов"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT region FROM crimes ORDER BY region")
        regions = [r[0] for r in cursor.fetchall()]
        conn.close()
        return regions if regions else list(REGIONS_KZ.keys())
    
    def get_crime_types(self) -> List[str]:
        """Список типов преступлений"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT crime_type FROM crimes ORDER BY crime_type")
        types = [r[0] for r in cursor.fetchall()]
        conn.close()
        return types if types else ["Кража", "Грабёж", "Разбой", "Убийство", "Другое"]


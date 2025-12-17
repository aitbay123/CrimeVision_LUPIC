"""
GIS сервис для работы с картами и геоданными
"""
import folium
from folium.plugins import HeatMap
from typing import Optional, List, Dict
from app.services.data_service import DataService

data_service = DataService()


class GISService:
    """Сервис для работы с географическими данными"""
    
    # Центр Казахстана
    KAZAKHSTAN_CENTER = [48.0196, 66.9237]
    
    def get_heatmap_data(self, start_date: Optional[str] = None,
                        end_date: Optional[str] = None,
                        region: Optional[str] = None) -> Dict:
        """Получить данные для тепловой карты"""
        crimes = data_service.get_crimes(
            start_date=start_date,
            end_date=end_date,
            region=region,
            limit=5000
        )
        
        # Формируем список точек [lat, lon, weight]
        heatmap_points = []
        for crime in crimes:
            lat = crime.get('latitude')
            lon = crime.get('longitude')
            
            # Проверяем, что координаты валидны
            if lat is not None and lon is not None:
                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                    
                    # Проверяем, что координаты в разумных пределах для Казахстана
                    if 40.0 <= lat_float <= 55.0 and 46.0 <= lon_float <= 87.0:
                        weight = float(crime.get('severity', 1))
                        # Нормализуем вес (1-5)
                        weight = max(0.5, min(5.0, weight))
                        
                        heatmap_points.append([
                            lat_float,
                            lon_float,
                            weight
                        ])
                except (ValueError, TypeError):
                    # Пропускаем записи с невалидными координатами
                    continue
        
        return {
            "points": heatmap_points,
            "center": self.KAZAKHSTAN_CENTER,
            "count": len(heatmap_points)
        }
    
    def generate_map(self, start_date: Optional[str] = None,
                    end_date: Optional[str] = None,
                    region: Optional[str] = None) -> str:
        """Генерация HTML карты с тепловым слоем"""
        # Создаём карту
        m = folium.Map(
            location=self.KAZAKHSTAN_CENTER,
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Получаем данные для тепловой карты
        heatmap_data = self.get_heatmap_data(start_date, end_date, region)
        
        if heatmap_data['points']:
            # Добавляем тепловой слой
            HeatMap(
                heatmap_data['points'],
                min_opacity=0.2,
                max_zoom=18,
                radius=25,
                blur=15,
                gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1: 'red'}
            ).add_to(m)
        
        # Добавляем маркеры для крупных городов
        cities = [
            ("Алматы", 43.2220, 76.8512),
            ("Астана", 51.1694, 71.4491),
            ("Шымкент", 42.3419, 69.5901),
            ("Актобе", 50.2833, 57.1667),
            ("Караганда", 49.8014, 73.1059),
        ]
        
        for city, lat, lon in cities:
            folium.Marker(
                [lat, lon],
                popup=city,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Возвращаем HTML как строку
        return m._repr_html_()


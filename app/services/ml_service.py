"""
ML сервис для прогнозирования и оценки рисков
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from app.services.data_service import DataService

data_service = DataService()


class MLService:
    """Сервис машинного обучения"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
    
    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Подготовка признаков для модели"""
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_year'] = df['date'].dt.dayofyear
        
        # One-hot encoding для регионов (упрощённо)
        regions = df['region'].unique()
        for region in regions:
            df[f'region_{region}'] = (df['region'] == region).astype(int)
        
        return df
    
    def get_forecast(self, region: Optional[str] = None,
                    crime_type: Optional[str] = None,
                    months: int = 3) -> Dict:
        """Получить прогноз преступности"""
        try:
            # Получаем исторические данные
            crimes = data_service.get_crimes(region=region, limit=10000)
            
            if not crimes:
                # Если данных нет, возвращаем прогноз на основе средних значений
                return self._get_default_forecast(months)
            
            df = pd.DataFrame(crimes)
            if df.empty:
                return self._get_default_forecast(months)
            
            # Агрегируем по датам
            df['date'] = pd.to_datetime(df['date'])
            df_daily = df.groupby('date').size().reset_index(name='count')
            df_daily = df_daily.sort_values('date')
            
            # Подготовка данных для прогноза
            df_daily['day_number'] = (df_daily['date'] - df_daily['date'].min()).dt.days
            
            # Простая линейная регрессия для прогноза
            X = df_daily[['day_number']].values
            y = df_daily['count'].values
            
            if len(X) < 2:
                return self._get_default_forecast(months)
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Генерируем прогноз
            last_date = df_daily['date'].max()
            forecast_dates = []
            forecast_values = []
            
            for i in range(1, months + 1):
                future_date = last_date + timedelta(days=30 * i)
                days_ahead = (future_date - df_daily['date'].min()).days
                predicted = model.predict([[days_ahead]])[0]
                
                # Не даём отрицательные значения
                predicted = max(0, predicted)
                
                forecast_dates.append(future_date.strftime('%Y-%m-%d'))
                forecast_values.append(round(float(predicted), 2))
            
            return {
                "status": "success",
                "forecast": {
                    "dates": forecast_dates,
                    "values": forecast_values,
                    "region": region or "Все регионы",
                    "crime_type": crime_type or "Все типы"
                },
                "historical_avg": round(float(df_daily['count'].mean()), 2)
            }
        except Exception as e:
            print(f"Ошибка прогнозирования: {e}")
            return self._get_default_forecast(months)
    
    def _get_default_forecast(self, months: int) -> Dict:
        """Прогноз по умолчанию (если недостаточно данных)"""
        forecast_dates = []
        forecast_values = []
        
        base_date = datetime.now()
        avg_value = 50  # Среднее значение по умолчанию
        
        for i in range(1, months + 1):
            future_date = base_date + timedelta(days=30 * i)
            forecast_dates.append(future_date.strftime('%Y-%m-%d'))
            forecast_values.append(avg_value)
        
        return {
            "status": "success",
            "forecast": {
                "dates": forecast_dates,
                "values": forecast_values,
                "region": "Все регионы",
                "crime_type": "Все типы"
            },
            "historical_avg": avg_value,
            "note": "Прогноз на основе средних значений (недостаточно данных)"
        }
    
    def assess_risk(self, region: Optional[str] = None) -> Dict:
        """Оценка уровня риска"""
        try:
            # Получаем статистику за последние 3 месяца
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
            
            stats = data_service.get_summary_stats(
                start_date=start_date,
                end_date=end_date,
                region=region
            )
            
            total_crimes = stats.get('total', 0)
            avg_severity = stats.get('avg_severity', 1)
            
            # Простая логика оценки риска
            if total_crimes == 0:
                risk_level = "low"
                risk_score = 0
            elif total_crimes < 50:
                risk_level = "low"
                risk_score = 1
            elif total_crimes < 150:
                risk_level = "medium"
                risk_score = 2
            else:
                risk_level = "high"
                risk_score = 3
            
            # Учитываем тяжесть преступлений
            if avg_severity > 2.5:
                risk_score += 1
                if risk_level == "low":
                    risk_level = "medium"
                elif risk_level == "medium":
                    risk_level = "high"
            
            risk_labels = {
                "low": "Низкий",
                "medium": "Средний",
                "high": "Высокий"
            }
            
            return {
                "status": "success",
                "region": region or "Все регионы",
                "risk_level": risk_level,
                "risk_label": risk_labels.get(risk_level, "Неизвестно"),
                "risk_score": min(risk_score, 5),
                "total_crimes": total_crimes,
                "avg_severity": avg_severity,
                "period": f"{start_date} - {end_date}"
            }
        except Exception as e:
            print(f"Ошибка оценки риска: {e}")
            return {
                "status": "error",
                "region": region or "Все регионы",
                "risk_level": "unknown",
                "risk_label": "Недостаточно данных",
                "error": str(e)
            }


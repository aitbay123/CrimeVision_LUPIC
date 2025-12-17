"""
Генератор реалистичных данных о преступлениях для CrimeVision.kz
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Регионы Казахстана с координатами
REGIONS = {
    "Алматы": {"lat": 43.2220, "lon": 76.8512, "city": "Алматы", "weight": 25},
    "Астана": {"lat": 51.1694, "lon": 71.4491, "city": "Астана", "weight": 20},
    "Шымкент": {"lat": 42.3419, "lon": 69.5901, "city": "Шымкент", "weight": 10},
    "Алматинская область": {"lat": 43.2220, "lon": 76.8512, "city": "Талдыкорган", "weight": 8},
    "Акмолинская область": {"lat": 51.1694, "lon": 71.4491, "city": "Кокшетау", "weight": 5},
    "Актюбинская область": {"lat": 50.2833, "lon": 57.1667, "city": "Актобе", "weight": 6},
    "Атырауская область": {"lat": 47.1167, "lon": 51.8833, "city": "Атырау", "weight": 4},
    "Западно-Казахстанская область": {"lat": 51.2364, "lon": 51.3760, "city": "Уральск", "weight": 3},
    "Жамбылская область": {"lat": 42.9000, "lon": 71.3667, "city": "Тараз", "weight": 4},
    "Карагандинская область": {"lat": 49.8014, "lon": 73.1059, "city": "Караганда", "weight": 7},
    "Костанайская область": {"lat": 53.2144, "lon": 63.6246, "city": "Костанай", "weight": 3},
    "Кызылординская область": {"lat": 44.8528, "lon": 65.5092, "city": "Кызылорда", "weight": 2},
    "Мангистауская область": {"lat": 43.6500, "lon": 51.1667, "city": "Актау", "weight": 2},
    "Павлодарская область": {"lat": 52.2833, "lon": 76.9667, "city": "Павлодар", "weight": 4},
    "Северо-Казахстанская область": {"lat": 54.8667, "lon": 69.1500, "city": "Петропавловск", "weight": 3},
    "Туркестанская область": {"lat": 43.3000, "lon": 68.2500, "city": "Туркестан", "weight": 5},
    "Восточно-Казахстанская область": {"lat": 49.9789, "lon": 82.6103, "city": "Усть-Каменогорск", "weight": 4},
}

# Типы преступлений с вероятностями
CRIME_TYPES = {
    "Кража": {"probability": 0.45, "severity_range": (1, 2)},
    "Грабёж": {"probability": 0.25, "severity_range": (2, 3)},
    "Разбой": {"probability": 0.15, "severity_range": (3, 4)},
    "Убийство": {"probability": 0.03, "severity_range": (5, 5)},
    "Мошенничество": {"probability": 0.08, "severity_range": (2, 3)},
    "Вымогательство": {"probability": 0.02, "severity_range": (3, 4)},
    "Изнасилование": {"probability": 0.01, "severity_range": (4, 5)},
    "Другое": {"probability": 0.01, "severity_range": (1, 3)},
}

def generate_crime_data(start_date, end_date, num_records):
    """Генерация данных о преступлениях"""
    data = []
    
    # Временной диапазон
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    days = delta.days
    
    # Веса регионов для выборки
    regions_list = list(REGIONS.keys())
    region_weights = [REGIONS[r]["weight"] for r in regions_list]
    
    # Список типов преступлений с весами
    crime_types_list = list(CRIME_TYPES.keys())
    crime_weights = [CRIME_TYPES[ct]["probability"] for ct in crime_types_list]
    
    for i in range(num_records):
        # Случайная дата в диапазоне
        random_days = random.randint(0, days)
        date = start + timedelta(days=random_days)
        
        # Выбор региона с учётом весов
        region = random.choices(regions_list, weights=region_weights)[0]
        region_info = REGIONS[region]
        
        # Добавляем небольшую случайность к координатам
        lat = region_info["lat"] + random.uniform(-0.1, 0.1)
        lon = region_info["lon"] + random.uniform(-0.1, 0.1)
        
        # Выбор типа преступления
        crime_type = random.choices(crime_types_list, weights=crime_weights)[0]
        severity_range = CRIME_TYPES[crime_type]["severity_range"]
        severity = random.randint(severity_range[0], severity_range[1])
        
        # Сезонность: больше преступлений летом и зимой
        month = date.month
        if month in [6, 7, 8, 12, 1, 2]:
            if random.random() < 0.3:  # 30% шанс добавить ещё одну запись
                continue
        
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "region": region,
            "city": region_info["city"],
            "crime_type": crime_type,
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "severity": severity
        })
    
    return pd.DataFrame(data)

def main():
    """Основная функция"""
    print("Генерация датасета для CrimeVision.kz")
    print("-" * 50)
    
    # Параметры генерации
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    num_records = int(input("Сколько записей сгенерировать? (рекомендуется 1000-5000): ") or "2000")
    
    print(f"\nГенерация {num_records} записей с {start_date} по {end_date}...")
    
    df = generate_crime_data(start_date, end_date, num_records)
    
    # Сортируем по дате
    df = df.sort_values("date")
    
    # Сохраняем в CSV
    output_file = "data/generated_crimes.csv"
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    
    print(f"\n✅ Датасет сохранён в {output_file}")
    print(f"📊 Статистика:")
    print(f"   - Всего записей: {len(df)}")
    print(f"   - Период: {df['date'].min()} - {df['date'].max()}")
    print(f"   - Регионов: {df['region'].nunique()}")
    print(f"   - Типов преступлений: {df['crime_type'].nunique()}")
    print(f"\n📈 Распределение по регионам (топ-5):")
    print(df['region'].value_counts().head())
    print(f"\n📈 Распределение по типам преступлений:")
    print(df['crime_type'].value_counts())
    
    print(f"\n💡 Для загрузки в базу данных используйте веб-интерфейс или:")
    print(f"   python load_sample_data.py  # (измените путь к файлу в скрипте)")

if __name__ == "__main__":
    main()




"""
Скрипт для загрузки тестовых данных из sample_crimes.csv
"""
import pandas as pd
from app.services.data_service import DataService
from app.database import init_db

def load_sample_data():
    """Загрузить тестовые данные"""
    print("Инициализация базы данных...")
    init_db()
    
    print("Загрузка данных из sample_crimes.csv...")
    df = pd.read_csv('data/sample_crimes.csv')
    
    print(f"Найдено {len(df)} записей")
    
    service = DataService()
    result = service.save_to_db(df)
    
    print(f"[OK] Успешно загружено {result['count']} записей в базу данных!")
    print("\nТеперь можно запустить сервер: python main.py")

if __name__ == "__main__":
    load_sample_data()


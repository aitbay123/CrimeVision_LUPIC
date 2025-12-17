"""
Модуль работы с базой данных
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("data/crime_vision.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """Получить соединение с БД"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Инициализация базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица для преступлений
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            region TEXT NOT NULL,
            city TEXT,
            crime_type TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            severity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Индексы для быстрого поиска
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON crimes(date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON crimes(region)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crime_type ON crimes(crime_type)")
    
    conn.commit()
    conn.close()
    print("[OK] База данных инициализирована")


"""
Скрипт для проверки установленных зависимостей
"""
import sys

def check_module(module_name, import_name=None):
    """Проверить, установлен ли модуль"""
    if import_name is None:
        import_name = module_name
    
    try:
        __import__(import_name)
        print(f"[OK] {module_name} установлен")
        return True
    except ImportError as e:
        print(f"[ERROR] {module_name} НЕ установлен: {e}")
        return False

print(f"Python версия: {sys.version}")
print(f"Python путь: {sys.executable}")
print("-" * 50)

# Проверка зависимостей
modules = [
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("pandas", "pandas"),
    ("numpy", "numpy"),
    ("scikit-learn", "sklearn"),
    ("folium", "folium"),
    ("plotly", "plotly"),
    ("jinja2", "jinja2"),
]

all_ok = True
for module_name, import_name in modules:
    if not check_module(module_name, import_name):
        all_ok = False

print("-" * 50)

# Проверка импорта из нашего проекта
try:
    sys.path.insert(0, '.')
    from app.services.ml_service import MLService
    from app.services.data_service import DataService
    from app.services.gis_service import GISService
    print("[OK] Все модули проекта импортируются успешно")
except Exception as e:
    print(f"[ERROR] Ошибка импорта модулей проекта: {e}")
    all_ok = False

if all_ok:
    print("\n[SUCCESS] Все зависимости установлены! Можно запускать приложение.")
else:
    print("\n[WARNING] Некоторые зависимости не установлены. Запустите: pip install -r requirements.txt")


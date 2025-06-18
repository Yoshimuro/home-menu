#!/usr/bin/env python3
"""
Конфигурационный файл для домашнего меню
Позволяет легко настроить параметры без изменения основного кода
"""

# Сетевые настройки
HOST = "0.0.0.0"  # Слушать на всех интерфейсах
PORT = 8080       # Порт по умолчанию

# Настройки сервера
MAX_CONNECTIONS = 10        # Максимальное количество одновременных подключений
REQUEST_TIMEOUT = 30        # Таймаут запроса в секундах
CACHE_STATIC_FILES = True   # Кешировать статические файлы
CACHE_TIME = 3600          # Время кеширования в секундах (1 час)

# Мониторинг
ENABLE_MONITORING = False   # Включить мониторинг памяти
MONITOR_INTERVAL = 60      # Интервал проверки памяти в секундах
MEMORY_WARNING_THRESHOLD = 10240  # Предупреждение при RAM < 10MB (в KB)
DISK_WARNING_THRESHOLD = 5120     # Предупреждение при диске < 5MB (в KB)

# Логирование
ENABLE_DETAILED_LOGS = False  # Подробные логи (может занимать больше памяти)
LOG_ACCESS_REQUESTS = True    # Логировать все запросы
LOG_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"  # Формат времени в логах

# Пути к файлам
HTML_FILE = "index.html"
BACKUP_DIR = "/tmp/menu-backups"  # Директория для резервных копий (если создается)

# Заголовки безопасности
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
}

# Настройки для роутеров с очень ограниченными ресурсами
MINIMAL_MODE = False  # Отключает дополнительные функции для экономии памяти

# Кастомные MIME типы (если нужны)
CUSTOM_MIME_TYPES = {
    '.json': 'application/json',
    '.webp': 'image/webp',
}

# Мультиязычность (если планируется)
DEFAULT_LANGUAGE = "ru"
SUPPORTED_LANGUAGES = ["ru", "en"]

def get_config():
    """Возвращает конфигурацию как словарь"""
    return {
        'host': HOST,
        'port': PORT,
        'max_connections': MAX_CONNECTIONS,
        'request_timeout': REQUEST_TIMEOUT,
        'cache_static_files': CACHE_STATIC_FILES,
        'cache_time': CACHE_TIME,
        'enable_monitoring': ENABLE_MONITORING,
        'monitor_interval': MONITOR_INTERVAL,
        'memory_warning_threshold': MEMORY_WARNING_THRESHOLD,
        'disk_warning_threshold': DISK_WARNING_THRESHOLD,
        'enable_detailed_logs': ENABLE_DETAILED_LOGS,
        'log_access_requests': LOG_ACCESS_REQUESTS,
        'log_timestamp_format': LOG_TIMESTAMP_FORMAT,
        'html_file': HTML_FILE,
        'backup_dir': BACKUP_DIR,
        'security_headers': SECURITY_HEADERS,
        'minimal_mode': MINIMAL_MODE,
        'custom_mime_types': CUSTOM_MIME_TYPES,
        'default_language': DEFAULT_LANGUAGE,
        'supported_languages': SUPPORTED_LANGUAGES,
    }

def load_user_config():
    """Загружает пользовательскую конфигурацию, если файл существует"""
    try:
        import json
        import os
        
        user_config_path = 'user_config.json'
        if os.path.exists(user_config_path):
            with open(user_config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Обновляем глобальные переменные
            globals().update(user_config)
            print(f"✅ Загружена пользовательская конфигурация из {user_config_path}")
            
    except Exception as e:
        print(f"⚠️  Ошибка загрузки пользовательской конфигурации: {e}")

def create_sample_user_config():
    """Создает образец пользовательской конфигурации"""
    import json
    
    sample_config = {
        "PORT": 9000,
        "ENABLE_MONITORING": True,
        "ENABLE_DETAILED_LOGS": True,
        "MEMORY_WARNING_THRESHOLD": 15360,  # 15MB
    }
    
    try:
        with open('user_config.json.example', 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        print("✅ Создан образец конфигурации: user_config.json.example")
        print("   Скопируйте его в user_config.json и отредактируйте по необходимости")
    except Exception as e:
        print(f"❌ Ошибка создания образца конфигурации: {e}")

if __name__ == "__main__":
    # Если запускается напрямую, создает образец конфигурации
    print("🔧 Конфигурация домашнего меню")
    print("=" * 40)
    
    config = get_config()
    print("📋 Текущие настройки:")
    for key, value in config.items():
        print(f"   {key}: {value}")
    
    print("\n💡 Для создания пользовательской конфигурации:")
    create_sample_user_config() 
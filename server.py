#!/usr/bin/env python3
"""
Легкий веб-сервер для домашнего меню
Оптимизирован для роутеров с ограниченными ресурсами
"""

import http.server
import socketserver
import os
import sys
import argparse
import signal
import threading
import time
from urllib.parse import unquote
import json

class MenuHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Кастомный обработчик для сервера меню"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/' or self.path == '/index.html' or self.path == '':
            self.path = '/index.html'
        
        # Добавляем заголовки для кеширования статических файлов
        if self.path.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
            self.send_response(200)
            self.send_header('Cache-Control', 'max-age=3600')  # 1 час
            if self.path.endswith('.css'):
                self.send_header('Content-Type', 'text/css')
            elif self.path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            
            try:
                with open(self.path[1:], 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404)
            return
        
        super().do_GET()
    
    def log_message(self, format, *args):
        """Упрощенное логирование для экономии ресурсов"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Многопоточный TCP сервер для обработки нескольких подключений"""
    allow_reuse_address = True
    daemon_threads = True

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    print("\n🛑 Сервер останавливается...")
    sys.exit(0)

def check_memory_usage():
    """Мониторинг использования памяти (если доступно)"""
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemAvailable:' in line:
                    available = int(line.split()[1])
                    if available < 10000:  # Меньше 10MB
                        print(f"⚠️  Предупреждение: мало свободной памяти ({available/1024:.1f}MB)")
                    break
    except:
        pass  # Не критично, если не удается получить информацию

def get_local_ip():
    """Получение локального IP адреса"""
    import socket
    try:
        # Подключаемся к удаленному адресу для определения локального IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def main():
    parser = argparse.ArgumentParser(description='Сервер домашнего меню для роутера')
    parser.add_argument('-p', '--port', type=int, default=8080, 
                       help='Порт для запуска сервера (по умолчанию: 8080)')
    parser.add_argument('-H', '--host', default='0.0.0.0',
                       help='IP адрес для привязки (по умолчанию: 0.0.0.0)')
    parser.add_argument('--monitor', action='store_true',
                       help='Включить мониторинг памяти')
    
    args = parser.parse_args()
    
    # Проверяем наличие файла index.html
    if not os.path.exists('index.html'):
        print("❌ Файл index.html не найден!")
        print("Убедитесь, что вы запускаете сервер из папки router-deployment")
        sys.exit(1)
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Создаем сервер
        with ThreadedTCPServer((args.host, args.port), MenuHTTPRequestHandler) as httpd:
            local_ip = get_local_ip()
            
            print("🍽️  Сервер домашнего меню запущен!")
            print(f"📍 Локальный адрес: http://{local_ip}:{args.port}")
            print(f"🌐 Сетевой адрес: http://{args.host}:{args.port}")
            print("⚡ Оптимизировано для роутеров")
            print("🔄 Нажмите Ctrl+C для остановки")
            print("-" * 50)
            
            # Запускаем мониторинг памяти в отдельном потоке
            if args.monitor:
                def memory_monitor():
                    while True:
                        time.sleep(60)  # Проверяем каждую минуту
                        check_memory_usage()
                
                monitor_thread = threading.Thread(target=memory_monitor, daemon=True)
                monitor_thread.start()
            
            # Запускаем сервер
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print(f"❌ Порт {args.port} уже используется!")
            print("Попробуйте другой порт: python3 server.py -p 8081")
        else:
            print(f"❌ Ошибка запуска сервера: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
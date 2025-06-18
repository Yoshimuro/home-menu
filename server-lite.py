#!/usr/bin/env python3
"""
Упрощенный сервер домашнего меню для python3-light
Совместим с минимальными установками Python в OpenWrt
"""

import http.server
import socketserver
import os
import sys
import signal
import time

# Простая конфигурация без argparse
HOST = "0.0.0.0"
PORT = 8080

class SimpleMenuHandler(http.server.SimpleHTTPRequestHandler):
    """Упрощенный обработчик для меню"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(os.path.abspath(__file__)), **kwargs)
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/' or self.path == '/index.html' or self.path == '':
            self.path = '/index.html'
        
        # Простое кеширование для статических файлов
        if self.path.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
            self.send_response(200)
            self.send_header('Cache-Control', 'max-age=3600')
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
        """Упрощенное логирование"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """Многопоточный сервер"""
    allow_reuse_address = True
    daemon_threads = True

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    print("\n🛑 Сервер останавливается...")
    sys.exit(0)

def get_local_ip():
    """Простое получение IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def parse_args():
    """Простой парсер аргументов без argparse"""
    global HOST, PORT
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-p', '--port']:
            if i + 1 < len(sys.argv):
                try:
                    PORT = int(sys.argv[i + 1])
                    i += 1
                except ValueError:
                    print("❌ Неверный порт!")
                    sys.exit(1)
        elif arg in ['-H', '--host']:
            if i + 1 < len(sys.argv):
                HOST = sys.argv[i + 1]
                i += 1
        elif arg in ['-h', '--help']:
            print("Использование: python3 server-lite.py [-p PORT] [-H HOST]")
            print("  -p, --port    Порт (по умолчанию: 8080)")
            print("  -H, --host    IP адрес (по умолчанию: 0.0.0.0)")
            sys.exit(0)
        i += 1

def main():
    # Парсим аргументы
    parse_args()
    
    # Проверяем наличие файла
    if not os.path.exists('index.html'):
        print("❌ Файл index.html не найден!")
        print("Запустите сервер из папки с файлами")
        sys.exit(1)
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Создаем сервер
        with ThreadedServer((HOST, PORT), SimpleMenuHandler) as httpd:
            local_ip = get_local_ip()
            
            print("🍽️  Сервер домашнего меню запущен!")
            print(f"📍 Локальный адрес: http://{local_ip}:{PORT}")
            print(f"🌐 Сетевой адрес: http://{HOST}:{PORT}")
            print("⚡ Lite версия для OpenWrt")
            print("🔄 Нажмите Ctrl+C для остановки")
            print("-" * 40)
            
            # Запускаем сервер
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 98:
            print(f"❌ Порт {PORT} уже используется!")
            print(f"Попробуйте: python3 server-lite.py -p {PORT + 1}")
        else:
            print(f"❌ Ошибка запуска: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
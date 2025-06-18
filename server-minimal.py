#!/usr/bin/env python3
"""
Минимальный HTTP сервер на чистых сокетах
Для python3-light без зависимостей
"""

import socket
import os
import sys
import signal
import threading
import time

# Конфигурация
HOST = "0.0.0.0"
PORT = 8080
MAX_CONNECTIONS = 10

def simple_url_decode(url):
    """Простое URL декодирование без urllib"""
    # Заменяем основные URL-кодированные символы
    url = url.replace('%20', ' ')
    url = url.replace('%21', '!')
    url = url.replace('%22', '"')
    url = url.replace('%23', '#')
    url = url.replace('%24', '$')
    url = url.replace('%25', '%')
    url = url.replace('%26', '&')
    url = url.replace('%27', "'")
    url = url.replace('%28', '(')
    url = url.replace('%29', ')')
    url = url.replace('%2A', '*')
    url = url.replace('%2B', '+')
    url = url.replace('%2C', ',')
    url = url.replace('%2D', '-')
    url = url.replace('%2E', '.')
    url = url.replace('%2F', '/')
    return url

class MinimalHTTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = True
        
    def start(self):
        """Запуск сервера"""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(MAX_CONNECTIONS)
            print(f"🍽️  Минимальный сервер запущен на {self.host}:{self.port}")
            print("🔄 Нажмите Ctrl+C для остановки")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client, 
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                except OSError:
                    if self.running:
                        print("❌ Ошибка принятия подключения")
                    break
                    
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
        finally:
            self.socket.close()
    
    def stop(self):
        """Остановка сервера"""
        self.running = False
        self.socket.close()
    
    def handle_client(self, client_socket, address):
        """Обработка клиентского подключения"""
        try:
            request = client_socket.recv(1024).decode('utf-8')
            if not request:
                return
            
            # Парсим HTTP запрос
            lines = request.split('\n')
            if not lines:
                return
                
            request_line = lines[0].strip()
            parts = request_line.split()
            if len(parts) < 2:
                return
                
            method = parts[0]
            path = simple_url_decode(parts[1])
             
            print(f"[{time.strftime('%H:%M:%S')}] {method} {path}")
            
            if method == 'GET':
                self.handle_get(client_socket, path)
            else:
                self.send_error(client_socket, 405, "Method Not Allowed")
                
        except Exception as e:
            print(f"❌ Ошибка обработки клиента: {e}")
        finally:
            client_socket.close()
    
    def handle_get(self, client_socket, path):
        """Обработка GET запроса"""
        # Нормализация пути
        if path == '/' or path == '':
            path = '/index.html'
        
        # Убираем начальный слеш
        if path.startswith('/'):
            path = path[1:]
        
        # Проверка безопасности
        if '..' in path or path.startswith('/'):
            self.send_error(client_socket, 403, "Forbidden")
            return
        
        # Попытка найти файл
        if not os.path.exists(path):
            self.send_error(client_socket, 404, "Not Found")
            return
        
        try:
            # Определяем Content-Type
            content_type = self.get_content_type(path)
            
            # Читаем файл
            with open(path, 'rb') as f:
                content = f.read()
            
            # Отправляем ответ
            response = f"HTTP/1.1 200 OK\r\n"
            response += f"Content-Type: {content_type}\r\n"
            response += f"Content-Length: {len(content)}\r\n"
            response += f"Cache-Control: max-age=3600\r\n"
            response += f"Connection: close\r\n"
            response += f"\r\n"
            
            client_socket.send(response.encode('utf-8'))
            client_socket.send(content)
            
        except Exception as e:
            print(f"❌ Ошибка отправки файла {path}: {e}")
            self.send_error(client_socket, 500, "Internal Server Error")
    
    def send_error(self, client_socket, code, message):
        """Отправка HTTP ошибки"""
        try:
            response = f"HTTP/1.1 {code} {message}\r\n"
            response += f"Content-Type: text/html; charset=utf-8\r\n"
            response += f"Connection: close\r\n"
            response += f"\r\n"
            response += f"<h1>{code} {message}</h1>"
            
            client_socket.send(response.encode('utf-8'))
        except:
            pass
    
    def get_content_type(self, path):
        """Определение MIME типа"""
        if path.endswith('.html'):
            return 'text/html; charset=utf-8'
        elif path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.json'):
            return 'application/json'
        elif path.endswith('.png'):
            return 'image/png'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            return 'image/jpeg'
        elif path.endswith('.ico'):
            return 'image/x-icon'
        else:
            return 'application/octet-stream'

def signal_handler(signum, frame):
    """Обработчик сигналов"""
    print("\n🛑 Остановка сервера...")
    if 'server' in globals():
        server.stop()
    sys.exit(0)

def parse_simple_args():
    """Простейший парсер аргументов"""
    global HOST, PORT
    
    for i, arg in enumerate(sys.argv):
        if arg == '-p' and i + 1 < len(sys.argv):
            try:
                PORT = int(sys.argv[i + 1])
            except ValueError:
                print("❌ Неверный порт!")
                sys.exit(1)
        elif arg == '-H' and i + 1 < len(sys.argv):
            HOST = sys.argv[i + 1]
        elif arg in ['-h', '--help']:
            print("Использование: python3 server-minimal.py [-p PORT] [-H HOST]")
            print("  -p     Порт (по умолчанию: 8080)")
            print("  -H     IP адрес (по умолчанию: 0.0.0.0)")
            sys.exit(0)

def main():
    global server
    
    # Простой парсинг аргументов
    parse_simple_args()
    
    # Проверяем файл
    if not os.path.exists('index.html'):
        print("❌ Файл index.html не найден!")
        sys.exit(1)
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем сервер
    server = MinimalHTTPServer(HOST, PORT)
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n🛑 Остановка по Ctrl+C")
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    main()
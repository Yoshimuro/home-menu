# 🍽️ Домашнее меню для роутера

[![Tests](https://github.com/username/home-menu-router/actions/workflows/test.yml/badge.svg)](https://github.com/username/home-menu-router/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![OpenWrt](https://img.shields.io/badge/OpenWrt-18.06+-orange.svg)](https://openwrt.org/)

Легкое веб-приложение для управления домашним меню, оптимизированное для развертывания на роутерах с ограниченными ресурсами.

## 🌟 Особенности

- 🏠 **Локальная сеть**: Работает в пределах домашней сети
- ⚡ **Минимальные требования**: Всего 20MB RAM и 5MB диска
- 🚀 **Быстрая установка**: Автоматический установщик для OpenWrt
- 📱 **Адаптивный интерфейс**: Работает на всех устройствах
- 💾 **Локальное хранилище**: Данные сохраняются в браузере
- 🔒 **Безопасность**: Только LAN доступ

## 📋 Системные требования

### Минимальные требования:
- **RAM**: 20+ МБ свободной памяти
- **Хранилище**: 5+ МБ свободного места
- **Python**: Python 3.6+
- **Сеть**: Локальная сеть (LAN)

### Поддерживаемые системы:
- ✅ OpenWrt (18.06+)
- ✅ DD-WRT
- ✅ Linux-роутеры (Debian, Ubuntu на ARM)
- ✅ Raspberry Pi
- ✅ Обычные Linux серверы

## 🚀 Быстрая установка

### Автоматическая установка
```bash
# 1. Скопируйте файлы на роутер
scp -r router-deployment/ root@192.168.1.1:/tmp/

# 2. Подключитесь к роутеру
ssh root@192.168.1.1

# 3. Перейдите в папку и запустите установку
cd /tmp/router-deployment
chmod +x install.sh
./install.sh
```

### Ручная установка

#### Для OpenWrt:
```bash
# 1. Установка Python (если не установлен)
opkg update
opkg install python3-light

# 2. Создание директории
mkdir -p /opt/home-menu

# 3. Копирование файлов
cp index.html server.py /opt/home-menu/

# 4. Создание init скрипта
cat > /etc/init.d/home-menu << 'EOF'
#!/bin/sh /etc/rc.common

START=99
STOP=10

start() {
    echo "Запуск Home Menu Server..."
    start-stop-daemon -S -b -m -p "/var/run/home-menu.pid" \
        -x /usr/bin/python3 -- /opt/home-menu/server.py -p 8080
}

stop() {
    echo "Остановка Home Menu Server..."
    start-stop-daemon -K -p "/var/run/home-menu.pid"
}
EOF

# 5. Запуск сервиса
chmod +x /etc/init.d/home-menu
/etc/init.d/home-menu enable
/etc/init.d/home-menu start
```

#### Для обычного Linux:
```bash
# 1. Создание systemd сервиса
sudo tee /etc/systemd/system/home-menu.service << 'EOF'
[Unit]
Description=Home Menu Server
After=network.target

[Service]
Type=simple
User=nobody
WorkingDirectory=/opt/home-menu
ExecStart=/usr/bin/python3 /opt/home-menu/server.py -p 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 2. Запуск сервиса
sudo systemctl daemon-reload
sudo systemctl enable home-menu
sudo systemctl start home-menu
```

## 🔧 Настройка

### Изменение порта
По умолчанию используется порт 8080. Для изменения:

```bash
# Отредактируйте файл сервиса или запустите напрямую:
python3 server.py -p 9000  # Порт 9000
```

### Настройка брандмауэра

#### OpenWrt:
```bash
uci add firewall rule
uci set firewall.@rule[-1].name='Home Menu'
uci set firewall.@rule[-1].src='lan'
uci set firewall.@rule[-1].dest_port='8080'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall reload
```

#### Linux (iptables):
```bash
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

## 🌐 Доступ

После установки сайт будет доступен по адресу:
- **Локальный доступ**: http://192.168.1.1:8080
- **С других устройств**: http://[IP_РОУТЕРА]:8080

## 💾 Особенности хранения данных

Приложение использует два механизма хранения данных:
1. **IndexedDB** (основной) - для современных браузеров
2. **localStorage** (резервный) - fallback для старых браузеров

Данные сохраняются локально в браузере каждого устройства.

### Экспорт/Импорт данных
- **Экспорт**: Кнопка "💾 Экспорт данных" сохранит JSON файл
- **Импорт**: Кнопка "📁 Импорт данных" загрузит JSON файл

## 🛠️ Управление сервисом

### Systemd (обычный Linux):
```bash
# Статус
sudo systemctl status home-menu

# Остановка
sudo systemctl stop home-menu

# Перезапуск
sudo systemctl restart home-menu

# Логи
sudo journalctl -u home-menu -f
```

### OpenWrt init.d:
```bash
# Статус
ps | grep server.py

# Остановка
/etc/init.d/home-menu stop

# Перезапуск
/etc/init.d/home-menu restart
```

## 📊 Мониторинг

Запуск с мониторингом памяти:
```bash
python3 server.py -p 8080 --monitor
```

Сервер будет проверять использование памяти каждую минуту и выводить предупреждения при нехватке ресурсов.

## 🔍 Диагностика

### Проверка доступности
```bash
# Проверка статуса сервера
curl http://localhost:8080

# Проверка из сети
curl http://192.168.1.1:8080
```

### Частые проблемы

#### Сервер не запускается:
1. Проверьте, установлен ли Python 3:
   ```bash
   python3 --version
   ```

2. Проверьте, свободен ли порт:
   ```bash
   netstat -ln | grep 8080
   ```

3. Проверьте права доступа:
   ```bash
   ls -la /opt/home-menu/
   ```

#### Сайт недоступен из сети:
1. Проверьте брандмауэр
2. Убедитесь, что сервер слушает на 0.0.0.0, а не только на localhost

#### Мало памяти:
1. Используйте более легкую версию Python:
   ```bash
   opkg install python3-light  # Вместо python3
   ```

2. Закройте ненужные процессы:
   ```bash
   ps | grep -v kernel  # Посмотреть процессы
   ```

## 🔄 Обновление

Для обновления приложения:
```bash
# 1. Остановите сервис
/etc/init.d/home-menu stop  # или systemctl stop home-menu

# 2. Замените файлы
cp новый_index.html /opt/home-menu/index.html
cp новый_server.py /opt/home-menu/server.py

# 3. Запустите сервис
/etc/init.d/home-menu start  # или systemctl start home-menu
```

## 🗑️ Удаление

```bash
# 1. Остановка и отключение сервиса
/etc/init.d/home-menu stop
/etc/init.d/home-menu disable
# или
sudo systemctl stop home-menu
sudo systemctl disable home-menu

# 2. Удаление файлов
rm -rf /opt/home-menu
rm /etc/init.d/home-menu
# или
rm /etc/systemd/system/home-menu.service

# 3. Удаление правила брандмауэра (OpenWrt)
uci delete firewall.@rule[-1]  # Если это последнее правило
uci commit firewall
```

## 📈 Производительность

### Использование ресурсов:
- **RAM**: ~5-15 МБ во время работы
- **CPU**: Минимальное (только при обращениях)
- **Хранилище**: ~2 МБ для файлов приложения

### Оптимизация:
- Кеширование статических файлов (1 час)
- Сжатый код без лишних зависимостей
- Эффективная обработка запросов

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи сервиса
2. Убедитесь в соответствии системным требованиям
3. Попробуйте перезапустить сервис
4. Проверьте сетевые настройки

## 🤝 Участие в проекте

Мы приветствуем участие в развитии проекта! 

### Как внести свой вклад:

1. **Fork** репозитория
2. Создайте **feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit** ваши изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. Откройте **Pull Request**

### Правила участия:

- Код должен быть совместим с Python 3.6+
- Тестируйте на OpenWrt (или симуляции)
- Добавляйте комментарии на русском языке
- Соблюдайте минимальные требования к ресурсам

## 🐛 Баг-репорты

Если нашли ошибку:
1. Проверьте [issues](https://github.com/username/home-menu-router/issues)
2. Создайте новый issue с описанием:
   - Версия OpenWrt
   - Версия Python
   - Шаги воспроизведения
   - Ожидаемое поведение
   - Логи ошибок

## 📝 Лицензия

Этот проект распространяется под лицензией [MIT](LICENSE).

## 🙏 Благодарности

- OpenWrt сообществу за отличную прошивку
- Python сообществу за простой язык
- Всем, кто тестирует и улучшает проект

## 📊 Статистика проекта

![GitHub repo size](https://img.shields.io/github/repo-size/username/home-menu-router)
![GitHub issues](https://img.shields.io/github/issues/username/home-menu-router)
![GitHub stars](https://img.shields.io/github/stars/username/home-menu-router)

---

**Приятного использования! 🍽️** 
# 🚀 Быстрая установка на роутер

## Проблема с SFTP-сервером
Если получаете ошибку `sftp-server: not found`, используйте один из способов ниже:

## 📦 Вариант 1: Через архив (рекомендуется)
```bash
# 1. Создан архив home-menu-router.tar.gz (57KB)
# 2. Передайте его одним из способов:

# SCP с принудительным старым протоколом:
scp -O ../home-menu-router.tar.gz root@192.168.1.1:/tmp/

# Или через rsync (если доступен):
rsync ../home-menu-router.tar.gz root@192.168.1.1:/tmp/
```

```bash
# 3. На роутере распакуйте и установите:
ssh root@192.168.1.1
cd /tmp
tar -xzf home-menu-router.tar.gz
cd router-deployment
chmod +x *.sh *.py
./install.sh
```

## 🌐 Вариант 2: Через HTTP-сервер
```bash
# 1. На вашем компьютере запустите веб-сервер:
cd /path/to/sco-for-conf
python3 -m http.server 8000

# 2. Узнайте ваш IP:
hostname -I  # Linux
ipconfig getifaddr en0  # macOS

# 3. На роутере скачайте:
ssh root@192.168.1.1
wget http://[ВАШ_IP]:8000/home-menu-router.tar.gz -O /tmp/home-menu-router.tar.gz
cd /tmp && tar -xzf home-menu-router.tar.gz
cd router-deployment && ./install.sh
```

## 📂 Вариант 3: Копирование по файлам
```bash
# Копируйте каждый файл отдельно через scp -O:
scp -O index.html root@192.168.1.1:/tmp/
scp -O server.py root@192.168.1.1:/tmp/
scp -O install.sh root@192.168.1.1:/tmp/

# На роутере:
ssh root@192.168.1.1
mkdir -p /tmp/router-deployment
mv /tmp/*.html /tmp/*.py /tmp/*.sh /tmp/router-deployment/
cd /tmp/router-deployment
chmod +x *.sh *.py
./install.sh
```

## ⚡ Вариант 4: Ручная установка
```bash
# Если автоматическая установка не работает, установите вручную:
ssh root@192.168.1.1

# Установите Python (если нужно):
opkg update && opkg install python3-light

# Создайте структуру:
mkdir -p /opt/home-menu

# Скопируйте файлы (передайте любым способом):
# index.html и server.py должны быть в /opt/home-menu/

# Создайте init скрипт:
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

# Запустите:
chmod +x /etc/init.d/home-menu
/etc/init.d/home-menu enable
/etc/init.d/home-menu start
```

## 🔧 Проверка установки
```bash
# Проверьте статус:
ps | grep server.py

# Проверьте доступность:
curl http://localhost:8080

# Откройте в браузере:
# http://[IP_РОУТЕРА]:8080
```

## 🆘 Решение проблем

### Ошибка "python3: not found"
```bash
opkg update
opkg install python3-light
```

### Ошибка "Permission denied"
```bash
chmod +x /opt/home-menu/server.py
chmod +x /etc/init.d/home-menu
```

### Порт занят
```bash
# Используйте другой порт:
python3 server.py -p 9000
# Или найдите процесс:
netstat -ln | grep 8080
```

### Нет доступа из сети
```bash
# Добавьте правило брандмауэра (OpenWrt):
uci add firewall rule
uci set firewall.@rule[-1].name='Home Menu'
uci set firewall.@rule[-1].src='lan'
uci set firewall.@rule[-1].dest_port='8080'
uci set firewall.@rule[-1].proto='tcp'
uci set firewall.@rule[-1].target='ACCEPT'
uci commit firewall
/etc/init.d/firewall reload
```

## ✅ Готово!
После успешной установки домашнее меню будет доступно по адресу:
**http://[IP_РОУТЕРА]:8080** 
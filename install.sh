#!/bin/bash

# Скрипт установки домашнего меню на роутер
# Поддерживает OpenWrt и большинство Linux-роутеров

set -e

# Конфигурация
SERVICE_NAME="home-menu"
INSTALL_DIR="/opt/home-menu"
SERVICE_PORT=8080
SERVICE_USER="nobody"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_requirements() {
    print_info "Проверка системных требований..."
    
    # Проверяем Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 не найден!"
        print_info "Для OpenWrt: opkg update && opkg install python3-light"
        exit 1
    fi
    
    # Проверяем доступную память
    if [ -f /proc/meminfo ]; then
        available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
        if [ "$available" -lt 20000 ]; then
            print_warning "Мало свободной памяти ($(($available/1024))MB)"
            print_warning "Рекомендуется минимум 20MB для стабильной работы"
        fi
    fi
    
    # Проверяем свободное место
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 1000 ]; then
        print_warning "Мало свободного места ($(($available_space/1024))MB)"
    fi
    
    print_success "Системные требования проверены"
}

create_directories() {
    print_info "Создание директорий..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "/etc/systemd/system" 2>/dev/null || true
    mkdir -p "/etc/init.d" 2>/dev/null || true
    
    print_success "Директории созданы"
}

install_files() {
    print_info "Установка файлов..."
    
    # Копируем основные файлы
    cp index.html "$INSTALL_DIR/"
    
    # Проверяем, какой сервер использовать
    if [ -f "server-minimal.py" ]; then
        print_info "Используем минимальный сервер для python3-light"
        cp server-minimal.py "$INSTALL_DIR/server.py"
    elif [ -f "server-lite.py" ]; then
        print_info "Используем lite версию сервера"
        cp server-lite.py "$INSTALL_DIR/server.py"
    else
        cp server.py "$INSTALL_DIR/"
    fi
    
    chmod +x "$INSTALL_DIR/server.py"
    
    # Устанавливаем права (только если пользователь существует)
    if id "$SERVICE_USER" >/dev/null 2>&1; then
        chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR" 2>/dev/null || \
        chown -R "$SERVICE_USER" "$INSTALL_DIR" 2>/dev/null || true
    else
        print_warning "Пользователь $SERVICE_USER не найден, оставляем права root"
    fi
    
    print_success "Файлы установлены в $INSTALL_DIR"
}

create_systemd_service() {
    print_info "Создание systemd сервиса..."
    
    cat << EOF > /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=Home Menu Server
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/server.py -p $SERVICE_PORT --monitor
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload 2>/dev/null || true
    print_success "Systemd сервис создан"
}

create_openwrt_service() {
    print_info "Создание OpenWrt init скрипта..."
    
    cat << EOF > /etc/init.d/${SERVICE_NAME}
#!/bin/sh /etc/rc.common

START=99
STOP=10

SERVICE_NAME="$SERVICE_NAME"
SERVICE_PID_FILE="/var/run/\${SERVICE_NAME}.pid"

start() {
    echo "Запуск Home Menu Server..."
    start-stop-daemon -S -b -m -p "\$SERVICE_PID_FILE" \\
        -x /usr/bin/python3 -- $INSTALL_DIR/server.py -p $SERVICE_PORT --monitor
    echo "Home Menu Server запущен на порту $SERVICE_PORT"
}

stop() {
    echo "Остановка Home Menu Server..."
    start-stop-daemon -K -p "\$SERVICE_PID_FILE"
    rm -f "\$SERVICE_PID_FILE"
    echo "Home Menu Server остановлен"
}

restart() {
    stop
    sleep 2
    start
}
EOF

    chmod +x /etc/init.d/${SERVICE_NAME}
    print_success "OpenWrt init скрипт создан"
}

configure_firewall() {
    print_info "Настройка брандмауэра..."
    
    # Для OpenWrt
    if command -v uci &> /dev/null; then
        print_info "Настройка для OpenWrt..."
        uci add firewall rule
        uci set firewall.@rule[-1].name='Home Menu'
        uci set firewall.@rule[-1].src='lan'
        uci set firewall.@rule[-1].dest_port="$SERVICE_PORT"
        uci set firewall.@rule[-1].proto='tcp'
        uci set firewall.@rule[-1].target='ACCEPT'
        uci commit firewall
        /etc/init.d/firewall reload
        print_success "Правило брандмауэра добавлено"
    # Для обычного Linux
    elif command -v iptables &> /dev/null; then
        iptables -A INPUT -p tcp --dport "$SERVICE_PORT" -j ACCEPT 2>/dev/null || true
        print_warning "Добавлено временное правило iptables"
        print_warning "Не забудьте сохранить правила: iptables-save > /etc/iptables/rules.v4"
    fi
}

start_service() {
    print_info "Запуск сервиса..."
    
    # Systemd
    if command -v systemctl &> /dev/null; then
        systemctl enable ${SERVICE_NAME} 2>/dev/null || true
        systemctl start ${SERVICE_NAME} 2>/dev/null || true
        sleep 2
        if systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
            print_success "Сервис запущен через systemd"
        else
            print_error "Ошибка запуска через systemd"
            systemctl status ${SERVICE_NAME} 2>/dev/null || true
        fi
    # OpenWrt
    elif [ -f /etc/init.d/${SERVICE_NAME} ]; then
        /etc/init.d/${SERVICE_NAME} enable
        /etc/init.d/${SERVICE_NAME} start
        print_success "Сервис запущен через init.d"
    fi
}

show_completion_info() {
    local_ip=$(ip route get 1 | awk '{print $NF;exit}' 2>/dev/null || echo "192.168.1.1")
    
    echo
    print_success "🎉 Установка завершена!"
    echo
    print_info "📋 Информация о сервисе:"
    print_info "   • Порт: $SERVICE_PORT"
    print_info "   • Локальный адрес: http://$local_ip:$SERVICE_PORT"
    print_info "   • Директория: $INSTALL_DIR"
    echo
    print_info "🔧 Управление сервисом:"
    if command -v systemctl &> /dev/null; then
        print_info "   • Статус: sudo systemctl status $SERVICE_NAME"
        print_info "   • Остановка: sudo systemctl stop $SERVICE_NAME"
        print_info "   • Перезапуск: sudo systemctl restart $SERVICE_NAME"
        print_info "   • Логи: sudo journalctl -u $SERVICE_NAME -f"
    else
        print_info "   • Статус: ps | grep server.py"
        print_info "   • Остановка: sudo /etc/init.d/$SERVICE_NAME stop"
        print_info "   • Перезапуск: sudo /etc/init.d/$SERVICE_NAME restart"
    fi
    echo
    print_info "🌐 Доступ из локальной сети:"
    print_info "   Откройте в браузере: http://$local_ip:$SERVICE_PORT"
}

main() {
    echo "🍽️  Установка домашнего меню на роутер"
    echo "========================================"
    echo
    
    # Проверяем, что мы в правильной директории
    if [ ! -f "index.html" ] || [ ! -f "server.py" ]; then
        print_error "Файлы index.html или server.py не найдены!"
        print_error "Запустите скрипт из папки router-deployment"
        exit 1
    fi
    
    check_requirements
    create_directories
    install_files
    
    # Создаем соответствующий сервис
    if command -v systemctl &> /dev/null; then
        create_systemd_service
    else
        create_openwrt_service
    fi
    
    configure_firewall
    start_service
    show_completion_info
}

# Проверяем права root для установки
if [ "$EUID" = 0 ] || [ "$(id -u)" = 0 ] || [ "$(whoami)" = "root" ]; then
    print_warning "Запуск от root. Пользователь сервиса будет: $SERVICE_USER"
    main
else
    print_error "Необходимы права root для установки"
    print_info "Текущий пользователь: $(whoami), UID: $(id -u)"
    print_info "Запустите скрипт от пользователя root"
    exit 1
fi 
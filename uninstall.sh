#!/bin/bash

# Скрипт удаления домашнего меню с роутера

set -e

# Конфигурация
SERVICE_NAME="home-menu"
INSTALL_DIR="/opt/home-menu"

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

confirm_removal() {
    echo "🗑️  Удаление домашнего меню"
    echo "============================="
    echo
    print_warning "Это действие удалит:"
    print_warning "• Сервис $SERVICE_NAME"
    print_warning "• Директорию $INSTALL_DIR"
    print_warning "• Правила брандмауэра"
    echo
    read -p "Продолжить? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Отменено пользователем"
        exit 0
    fi
}

stop_service() {
    print_info "Остановка сервиса..."
    
    # Systemd
    if command -v systemctl &> /dev/null && systemctl is-active --quiet ${SERVICE_NAME} 2>/dev/null; then
        sudo systemctl stop ${SERVICE_NAME}
        sudo systemctl disable ${SERVICE_NAME}
        print_success "Сервис остановлен (systemd)"
    fi
    
    # OpenWrt init.d
    if [ -f /etc/init.d/${SERVICE_NAME} ]; then
        sudo /etc/init.d/${SERVICE_NAME} stop 2>/dev/null || true
        sudo /etc/init.d/${SERVICE_NAME} disable 2>/dev/null || true
        print_success "Сервис остановлен (init.d)"
    fi
    
    # Принудительная остановка процесса
    pkill -f "server.py" 2>/dev/null || true
}

remove_service_files() {
    print_info "Удаление файлов сервиса..."
    
    # Systemd
    if [ -f /etc/systemd/system/${SERVICE_NAME}.service ]; then
        sudo rm /etc/systemd/system/${SERVICE_NAME}.service
        sudo systemctl daemon-reload
        print_success "Удален systemd сервис"
    fi
    
    # OpenWrt init.d
    if [ -f /etc/init.d/${SERVICE_NAME} ]; then
        sudo rm /etc/init.d/${SERVICE_NAME}
        print_success "Удален init.d скрипт"
    fi
}

remove_application_files() {
    print_info "Удаление файлов приложения..."
    
    if [ -d "$INSTALL_DIR" ]; then
        sudo rm -rf "$INSTALL_DIR"
        print_success "Удалена директория $INSTALL_DIR"
    else
        print_warning "Директория $INSTALL_DIR не найдена"
    fi
}

remove_firewall_rules() {
    print_info "Удаление правил брандмауэра..."
    
    # OpenWrt
    if command -v uci &> /dev/null; then
        print_info "Поиск правил для порта 8080..."
        
        # Ищем и удаляем правила для Home Menu
        rule_count=0
        for section in $(uci show firewall | grep "rule\[" | grep "dest_port='8080'" | cut -d'.' -f2 | cut -d'[' -f1 | sort -u); do
            rule_name=$(uci get firewall.${section}.name 2>/dev/null || echo "")
            if [[ "$rule_name" == *"Home Menu"* ]] || [[ "$rule_name" == *"home-menu"* ]]; then
                uci delete firewall.${section}
                ((rule_count++))
            fi
        done
        
        if [ $rule_count -gt 0 ]; then
            uci commit firewall
            /etc/init.d/firewall reload
            print_success "Удалено $rule_count правило(а) брандмауэра"
        else
            print_warning "Правила брандмауэра не найдены"
        fi
    else
        print_warning "UCI не найден, правила брандмауэра не удалены"
        print_info "Удалите правила iptables вручную, если они были созданы"
    fi
}

cleanup_temp_files() {
    print_info "Очистка временных файлов..."
    
    # Удаляем PID файлы
    sudo rm -f /var/run/${SERVICE_NAME}.pid
    
    # Удаляем логи (если есть)
    sudo rm -f /var/log/${SERVICE_NAME}.log
    
    # Удаляем временные файлы установки
    rm -f /tmp/router-deployment -rf 2>/dev/null || true
    
    print_success "Временные файлы очищены"
}

check_removal_success() {
    print_info "Проверка результатов удаления..."
    
    issues=0
    
    # Проверяем процессы
    if pgrep -f "server.py" >/dev/null 2>&1; then
        print_warning "Процесс server.py все еще запущен"
        ((issues++))
    fi
    
    # Проверяем файлы
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Директория $INSTALL_DIR все еще существует"
        ((issues++))
    fi
    
    # Проверяем сервисы
    if [ -f /etc/systemd/system/${SERVICE_NAME}.service ] || [ -f /etc/init.d/${SERVICE_NAME} ]; then
        print_warning "Файлы сервиса все еще существуют"
        ((issues++))
    fi
    
    # Проверяем порт
    if netstat -ln 2>/dev/null | grep ":8080" >/dev/null; then
        print_warning "Порт 8080 все еще используется"
        ((issues++))
    fi
    
    if [ $issues -eq 0 ]; then
        print_success "Удаление завершено успешно!"
    else
        print_warning "Обнаружено $issues проблем(ы). Возможно, потребуется ручная очистка."
    fi
}

show_completion_info() {
    echo
    print_success "🎉 Удаление завершено!"
    echo
    print_info "📋 Что было удалено:"
    print_info "   • Сервис $SERVICE_NAME"
    print_info "   • Файлы приложения ($INSTALL_DIR)"
    print_info "   • Правила брандмауэра"
    print_info "   • Временные файлы"
    echo
    print_info "💡 Дополнительная очистка:"
    print_info "   • Данные в браузере сохраняются локально"
    print_info "   • Резервные копии (если есть) не удалены"
    echo
    print_success "Домашнее меню полностью удалено с роутера"
}

main() {
    confirm_removal
    stop_service
    remove_service_files
    remove_application_files
    remove_firewall_rules
    cleanup_temp_files
    check_removal_success
    show_completion_info
}

# Проверяем права для удаления
if [ "$EUID" = 0 ]; then
    print_warning "Запуск от root"
    main
elif command -v sudo &> /dev/null; then
    print_info "Будет использоваться sudo для удаления"
    main
else
    print_error "Необходимы права root или sudo для удаления"
    exit 1
fi 
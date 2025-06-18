# 🐙 Настройка GitHub репозитория

Пошаговая инструкция для размещения проекта на GitHub.

## 🚀 Быстрый старт

### 1. Создание репозитория на GitHub

1. Перейдите на [github.com](https://github.com)
2. Нажмите **"New repository"**
3. Заполните данные:
   - **Repository name**: `home-menu-router`
   - **Description**: `🍽️ Домашнее меню для OpenWrt роутера - легкое веб-приложение для управления рецептами`
   - **Visibility**: Public (для открытого проекта)
   - ❌ НЕ создавайте README, .gitignore или LICENSE (уже есть)

### 2. Инициализация локального репозитория

```bash
# Перейдите в папку проекта
cd router-deployment

# Инициализируйте Git
git init

# Добавьте все файлы
git add .

# Создайте первый коммит
git commit -m "🎉 Initial commit: Home Menu for OpenWrt routers

- ✨ Added web interface for home menu management
- 🚀 Support for OpenWrt 18.06+ routers  
- ⚡ Minimal resource requirements (20MB RAM, 5MB storage)
- 🛠️ Automatic installer and uninstaller scripts
- 📱 Responsive design for all devices
- 🔒 Security headers and local network access only
- 📚 Comprehensive documentation and quick start guide"

# Переименуйте ветку в main (если нужно)
git branch -M main

# Добавьте удаленный репозиторий
git remote add origin https://github.com/ВАШЕ_ИМЯ/home-menu-router.git

# Отправьте код на GitHub
git push -u origin main
```

### 3. Настройка защищенных веток

После загрузки кода:

1. Перейдите в **Settings** → **Branches**
2. Добавьте правило для ветки `main`:
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### 4. Настройка секций GitHub

#### 📋 Issues
1. **Settings** → **General** → **Features**
2. ✅ Включите Issues
3. Шаблоны уже настроены в `.github/ISSUE_TEMPLATE/`

#### 🚀 Actions  
1. **Settings** → **Actions** → **General**
2. ✅ Allow all actions and reusable workflows
3. CI/CD уже настроен в `.github/workflows/test.yml`

#### 📊 Insights
1. **Insights** → **Community Standards**
2. Проверьте зеленые галочки (должны быть все)

## 🏷️ Тэги и релизы

### Создание первого релиза

```bash
# Создайте тэг
git tag -a v1.0.0 -m "🎉 First stable release

✨ Features:
- Complete web interface for home menu
- OpenWrt router support (18.06+)
- Three server variants (full, lite, minimal)  
- Auto installer and uninstaller
- Resource monitoring
- Responsive design
- Data export/import

🔒 Security:
- Local network access only
- Security headers
- Path traversal protection

📚 Documentation:
- Complete setup guide
- Troubleshooting section
- Quick install instructions"

# Отправьте тэг
git push origin v1.0.0
```

Затем на GitHub:
1. **Releases** → **Create a new release**
2. Выберите тэг `v1.0.0`
3. **Release title**: `🍽️ Home Menu v1.0.0 - First Stable Release`
4. Опишите релиз (используйте описание из CHANGELOG.md)
5. Прикрепите архив `home-menu-router.tar.gz`

## 📈 Настройка Insights

### Topics (теги репозитория)
Добавьте теги в **Settings** → **General**:
```
openwrt router home-menu python web-app lightweight minimal-resources
домашнее-меню роутер рецепты веб-приложение
```

### Социальные ссылки
Добавьте в **Settings** → **General** → **Social preview**:
- Загрузите скриншот веб-интерфейса

## 🤝 Community

### Обновление README badges

После создания репозитория обновите бейджи в README.md:

```markdown
[![Tests](https://github.com/ВАШЕ_ИМЯ/home-menu-router/actions/workflows/test.yml/badge.svg)](https://github.com/ВАШЕ_ИМЯ/home-menu-router/actions/workflows/test.yml)
[![GitHub release](https://img.shields.io/github/release/ВАШЕ_ИМЯ/home-menu-router.svg)](https://github.com/ВАШЕ_ИМЯ/home-menu-router/releases)
[![GitHub issues](https://img.shields.io/github/issues/ВАШЕ_ИМЯ/home-menu-router.svg)](https://github.com/ВАШЕ_ИМЯ/home-menu-router/issues)
[![GitHub stars](https://img.shields.io/github/stars/ВАШЕ_ИМЯ/home-menu-router.svg)](https://github.com/ВАШЕ_ИМЯ/home-menu-router/stargazers)
```

## 📚 Дополнительные настройки

### GitHub Pages (опционально)
Для демо-сайта:
1. **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main, / (root)
4. Добавьте ссылку на демо в README

### Автоматическое обновление архива
Можно добавить GitHub Action для автоматического создания архива при каждом релизе.

## ✅ Чеклист готовности

После выполнения всех шагов проверьте:

- [ ] 📝 README.md с бейджами и описанием
- [ ] 📋 Issues templates работают
- [ ] 🚀 Pull request template настроен  
- [ ] ⚙️ GitHub Actions проходят тесты
- [ ] 🏷️ Первый релиз создан
- [ ] 📊 Community Standards: 100%
- [ ] 🔒 Защищенная main ветка
- [ ] 📈 Topics и social preview настроены

**Готово! Ваш проект готов к сообществу! 🎉** 
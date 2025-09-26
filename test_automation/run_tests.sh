#!/bin/bash
cd "$(dirname "$0")"

echo "🐳 Запуск тестирования Dockerfile для Java, Go, JavaScript"

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt

# Создаем тестовые проекты
python test_projects/generator.py

# Запускаем тесты
python test_runner.py

# Открываем отчет
if command -v xdg-open > /dev/null; then
    xdg-open results/report.html
elif command -v open > /dev/null; then
    open results/report.html
fi
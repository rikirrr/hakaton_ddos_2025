#!/bin/bash
set -e

# Проверяем наличие go.mod (типовая точка входа для Go проектов)
if [ ! -f go.mod ]; then
    echo "Ошибка: go.mod не найден! Убедитесь, что вы запускаете скрипт внутри Go проекта."
    exit 1
fi

echo "Обнаружены файлы для сборки:"

# Проверка и выполнение сборки через Mage
if [ -f Magefile.go ]; then
    echo "Обнаружен Magefile.go — запуск mage build"
    # Установка mage, если не установлен
    if ! command -v mage &> /dev/null; then
        echo "Mage не найден, устанавливаем..."
        go install github.com/magefile/mage@latest
        export PATH="$PATH:$(go env GOPATH)/bin"
    fi
    mage build
    echo "Запуск приложения..."
    exec ./app

# Проверка и выполнение сборки через Makefile
elif [ -f Makefile ]; then
    echo "Обнаружен Makefile — запуск make build"
    make build
    echo "Запуск приложения..."
    exec ./app

# Проверка и выполнение сборки через Taskfile
elif [ -f Taskfile.yml ]; then
    echo "Обнаружен Taskfile.yml — запуск task build"
    # Установка task, если не установлен
    if ! command -v task &> /dev/null; then
        echo "Task не найден, устанавливаем..."
        curl -sL https://taskfile.dev/install.sh | sh
        export PATH="$PATH:$(pwd)/bin"
    fi
    task build
    echo "Запуск приложения..."
    exec ./app

# Если нет специальных билд-файлов, используем стандартный go build
else
    echo "Специальные скрипты не найдены — используем go build"
    go build -o app ./...
    echo "Запуск приложения..."
    exec ./app
fi
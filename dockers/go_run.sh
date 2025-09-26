#!/bin/bash
set -e

# --- Переменные окружения ---
GO_DEFAULT_VERSION="1.22.5" # Используем стабильную версию Go по умолчанию
GO_ROOT="/usr/local/go"

# Функция для извлечения версии Go из go.mod
get_go_version() {
    local version=""
    local go_mod_file="go.mod"

    if [ -f "$go_mod_file" ]; then
        echo "Анализирую Go-файл: $go_mod_file" >&2
        # Ищем строку "go X.Y" и извлекаем версию (например, 1.21, 1.22)
        version=$(grep -E '^\s*go\s+[0-9]+\.[0-9]+(\.[0-9]+)?' "$go_mod_file" | head -n 1 | awk '{print $2}')
    fi

    # Добавляем патч-версию, если указана только мажорная/минорная (для корректной загрузки)
    if [[ "$version" =~ ^[0-9]+\.[0-9]+$ ]]; then
        # Используем .0 для загрузки, если точная патч-версия неизвестна
        # В большинстве случаев Go-загрузчик сам перенаправляет на последнюю патч-версию
        version="${version}.0"
    fi

    # Удаляем лишние символы
    version=$(echo "$version" | tr -d '[:space:]')

    echo "Найденная версия Go в go.mod: $version" >&2
    echo "$version"
}

# Функция для установки Go SDK указанной версии
install_go() {
    local version=$1
    local go_archive="go${version}.linux-amd64.tar.gz"
    local GOLANG_URL="https://go.dev/dl/${go_archive}"

    echo "Установка Go $version..." >&2

    # Установка необходимых утилит
    apt-get update && apt-get install -y wget curl tar

    # Удаляем старую версию Go, если есть
    if [ -d "$GO_ROOT" ]; then
        echo "Обнаружена существующая установка Go, удаляю..." >&2
        rm -rf "$GO_ROOT"
    fi

    echo "Скачивание Go SDK с $GOLANG_URL..." >&2

    # Скачивание с обработкой ошибок и прогрессом
    if ! wget -q --show-progress "$GOLANG_URL" -O "/tmp/$go_archive"; then
        echo "Ошибка: Не удалось скачать Go SDK версии $version." >&2
        echo "Попробую установить версию по умолчанию: $GO_DEFAULT_VERSION." >&2
        version=$GO_DEFAULT_VERSION
        go_archive="go${version}.linux-amd64.tar.gz"
        GOLANG_URL="https://go.dev/dl/${go_archive}"

        if ! wget -q --show-progress "$GOLANG_URL" -O "/tmp/$go_archive"; then
            echo "Критическая ошибка: Не удалось скачать даже версию по умолчанию. Проверьте подключение или версию." >&2
            exit 1
        fi
    fi

    echo "Распаковка в /usr/local..." >&2
    tar -C /usr/local -xzf "/tmp/$go_archive"
    rm -f "/tmp/$go_archive"

    # Установка переменных окружения для текущего сеанса
    export GOROOT="$GO_ROOT"
    export PATH="$PATH:$GOROOT/bin"
    export GOPATH="$HOME/go"

    echo "Go $version успешно установлен." >&2
}

# Функция для установки необходимых инструментов сборки
install_build_tool() {
    local tool=$1
    echo "Установка инструмента сборки: $tool"

    case "$tool" in
        "make")
            echo "Установка 'make' через apt..."
            apt-get install -y make
            ;;
        "task")
            # Установка go-task (taskfile)
            echo "Установка 'go-task'..."
            # Используем curl и go install для установки task
            GO_BIN=$(command -v go)
            if [ -z "$GO_BIN" ]; then
                echo "Ошибка: Go SDK не найден для установки 'task'. Сборка может завершиться неудачей." >&2
            else
                $GO_BIN install github.com/go-task/task/v3/cmd/task@latest
                export PATH="$PATH:$(go env GOPATH)/bin"
            fi
            ;;
        "mage")
            # Установка Mage
            echo "Установка 'mage'..."
            GO_BIN=$(command -v go)
            if [ -z "$GO_BIN" ]; then
                echo "Ошибка: Go SDK не найден для установки 'mage'. Сборка может завершиться неудачей." >&2
            else
                $GO_BIN install github.com/magefile/mage@latest
                export PATH="$PATH:$(go env GOPATH)/bin"
            fi
            ;;
        "go-build")
            echo "Используется стандартный 'go build'. Дополнительные инструменты не требуются."
            ;;
        *)
            echo "Неизвестный инструмент сборки: $tool. Пропускаю установку." >&2
            ;;
    esac
}

# --- Начало основного сценария ---

# 1. Проверяем наличие файла go.mod
if [ ! -f go.mod ]; then
    echo "Ошибка: Не найден обязательный файл 'go.mod'. Это должен быть Go-проект."
    exit 1
fi

# 2. Определяем и устанавливаем версию Go
GO_VERSION=$(get_go_version)

# Если версия не найдена или не является числом, используем $GO_DEFAULT_VERSION по умолчанию
if ! [[ "$GO_VERSION" =~ ^[0-9]+\.[0-9]+(\.[0-9]+)?$ ]]; then
    echo "Версия Go не найдена в go.mod или имеет неверный формат. Использую $GO_DEFAULT_VERSION по умолчанию."
    GO_VERSION="$GO_DEFAULT_VERSION"
else
    echo "Найдена версия Go: $GO_VERSION."
fi

install_go "$GO_VERSION"

# Проверяем, что Go установлен
echo "Проверяем установку Go..."
go version

# 3. Определяем инструмент сборки
BUILD_TOOL="go-build"
BUILD_COMMAND=""
BINARY_NAME="" # Имя исполняемого файла

# Приоритет: mage > task > make > go-build (чистый Go)
if [ -f magefile.go ]; then
    BUILD_TOOL="mage"
    BUILD_COMMAND="mage Build" # Предполагаем, что есть цель 'Build'
    echo "Обнаружен проект Mage."
elif [ -f Taskfile.yml ] || [ -f Taskfile.yaml ]; then
    BUILD_TOOL="task"
    BUILD_COMMAND="task build" # Предполагаем, что есть задача 'build'
    echo "Обнаружен проект Taskfile."
elif [ -f Makefile ]; then
    BUILD_TOOL="make"
    BUILD_COMMAND="make build" # Предполагаем, что есть цель 'build'
    echo "Обнаружен проект Makefile."
else
    echo "Используется стандартный 'go build'."
    # Для go-build мы соберем файл в текущем каталоге
    PROJECT_NAME=$(basename "$(pwd)")
    # Убираем все символы, кроме букв, цифр и тире
    BINARY_NAME=$(echo "$PROJECT_NAME" | sed 's/[^a-zA-Z0-9_-]//g')
    # Компиляция чистого Go-проекта:
    BUILD_COMMAND="go build -o $BINARY_NAME ./..."
    echo "Будет создан исполняемый файл: $BINARY_NAME"
fi

# 4. Устанавливаем инструмент сборки
install_build_tool "$BUILD_TOOL"

# 5. Сборка и запуск проекта
echo "➡ Запуск сборки проекта с помощью $BUILD_TOOL..."

# Выполняем команду сборки
$BUILD_COMMAND

# Если использовались Mage, Task или Make, нужно определить имя бинарника,
# так как они могут собирать его в sub-каталог (например, 'bin/')
if [ "$BUILD_TOOL" != "go-build" ]; then
    # Ищем бинарник, который был изменен в последнюю очередь,
    # игнорируя файлы в .git, .vscode и т.п.
    # Если сборщик не определил имя явно, ищем его в текущем или подкаталогах 'bin', 'build'
    # Имя будет соответствовать имени текущей папки, если иное не указано
    BINARY_NAME=$(find . -type f -executable -not -path "./.git/*" -not -path "./vendor/*" -not -path "./.vscode/*" -mmin -5 | grep -v "\.sh$" | head -n 1)

    if [ -z "$BINARY_NAME" ]; then
        echo "Предупреждение: Не удалось автоматически найти исполняемый файл после сборки $BUILD_TOOL." >&2
        # Последняя попытка: ищем файл в текущей директории с именем папки
        FOLDER_NAME=$(basename "$(pwd)")
        if [ -f "$FOLDER_NAME" ]; then
             BINARY_NAME="./$FOLDER_NAME"
        else
             echo "Критическая ошибка: Исполняемый файл не найден после сборки!"
             exit 1
        fi
    fi

    # Делаем файл исполняемым (на всякий случай)
    chmod +x "$BINARY_NAME"
fi

echo "Запуск исполняемого файла: $BINARY_NAME"

# 'exec' заменяет текущий процесс оболочки на процесс приложения
exec "$BINARY_NAME"

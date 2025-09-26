#!/bin/bash
set -e

# Функция для извлечения версии Java из Maven pom.xml
get_java_version_maven() {
    local java_version=""

    echo "Анализирую Maven-файл: pom.xml" >&2

    # Ищем версию Java в различных тегах
    if command -v xmllint >/dev/null 2>&1; then
        # Используем более надёжный xmllint для парсинга XML
        java_version=$(xmllint --xpath "string(//properties/maven.compiler.source)" pom.xml 2>/dev/null || echo "")
        if [ -z "$java_version" ]; then
            java_version=$(xmllint --xpath "string(//properties/maven.compiler.target)" pom.xml 2>/dev/null || echo "")
        fi
        if [ -z "$java_version" ]; then
            java_version=$(xmllint --xpath "string(//properties/java.version)" pom.xml 2>/dev/null || echo "")
        fi
        if [ -z "$java_version" ]; then
            java_version=$(xmllint --xpath "string(//properties/kotlin.jvm.target)" pom.xml 2>/dev/null || echo "")
        fi
        if [ -z "$java_version" ]; then
            java_version=$(xmllint --xpath "string(//properties/maven.compiler.release)" pom.xml 2>/dev/null || echo "")
        fi
    else
        # Резервный вариант, если xmllint недоступен. Менее надёжен.
        java_version=$(grep -E "<(maven\.compiler\.source|maven\.compiler\.target|java\.version|kotlin\.jvm\.target|maven\.compiler\.release)>" pom.xml | head -n 1 | sed -n 's/.*>\([0-9][0-9]*\)<.*/\1/p')
    fi

    # Удаляем лишние символы, если они есть
    java_version=$(echo "$java_version" | tr -d '[:space:]')

    echo "Найденная версия Java в Maven: $java_version" >&2
    echo "$java_version"
}

# Функция для извлечения версии Java из Gradle build.gradle
get_java_version_gradle() {
    local java_version=""
    local gradle_file=""

    if [ -f build.gradle ]; then
        gradle_file="build.gradle"
        echo "Анализирую Gradle-файл: $gradle_file" >&2
    elif [ -f build.gradle.kts ]; then
        gradle_file="build.gradle.kts"
        echo "Анализирую Kotlin Gradle-файл: $gradle_file" >&2
    fi

    if [ -n "$gradle_file" ]; then
        # Ищем версию Java в различных синтаксисах Gradle
        if [[ "$gradle_file" == *.kts ]]; then
            # Синтаксис Kotlin DSL
            # Ищем jvmToolchain(XX)
            java_version=$(grep -oP 'jvmToolchain\((\d+)\)' "$gradle_file" | tail -n 1 | grep -oP '\d+')
            if [ -z "$java_version" ]; then
                # Ищем JavaVersion.VERSION_XX
                java_version=$(grep -oP 'JavaVersion\.VERSION_(\d+)' "$gradle_file" | tail -n 1 | grep -oP '\d+')
            fi
            if [ -z "$java_version" ]; then
                # Ищем of(XX)
                java_version=$(grep -oP 'of\((\d+)\)' "$gradle_file" | tail -n 1 | grep -oP '\d+')
            fi
            if [ -z "$java_version" ]; then
                # Ищем jvmTarget = "XX"
                java_version=$(grep -oP 'jvmTarget\s*=\s*"\s*(\d+)\s*"' "$gradle_file" | tail -n 1 | grep -oP '\d+')
            fi
        else
            # Синтаксис Groovy DSL
            java_version=$(grep -oP '(sourceCompatibility|targetCompatibility)\s*=\s*\s*("?\d+\.?\d*"?|\s*JavaVersion.VERSION_(\d+))' "$gradle_file" | tail -n 1 | grep -oP '\d+')
            if [ -z "$java_version" ]; then
                java_version=$(grep -oP 'jvmTarget\s*=\s*"\s*(\d+)\s*"' "$gradle_file" | tail -n 1 | grep -oP '\d+')
            fi
        fi
    fi

    # Проверяем gradle.properties
    if [ -z "$java_version" ] && [ -f gradle.properties ]; then
        echo "Проверяю gradle.properties:" >&2
        java_version=$(grep -oP '(org\.gradle\.java\.home|java\.version|kotlin\.jvm\.target)\s*=\s*(\d+)' gradle.properties | tail -n 1 | grep -oP '\d+')
    fi

    # Удаляем лишние символы, если есть
    java_version=$(echo "$java_version" | tr -d '[:space:]')

    echo "Найденная версия Java в Gradle: $java_version" >&2
    echo "$java_version"
}

# Функция для установки JDK указанной версии
install_java() {
    local version=$1
    echo "Установка OpenJDK $version..."

    # Обновляем списки пакетов и устанавливаем необходимые утилиты
    # Примечание: Этот скрипт предполагает использование пакетного менеджера 'apt',
    # типичного для систем на базе Debian (например, Ubuntu).
    echo "Обновление списка пакетов и установка необходимых утилит..."
    apt-get update && apt-get install -y wget curl unzip gnupg software-properties-common libxml2-utils

    case $version in
        8|11|17|18|19|20|21)
            echo "Установка openjdk-${version}-jdk..."
            apt-get update && apt-get install -y openjdk-${version}-jdk
            ;;
        *)
            echo "Неподдерживаемая версия Java: $version. Устанавливаю JDK 17 по умолчанию."
            echo "Установка openjdk-17-jdk..."
            apt-get update && apt-get install -y openjdk-17-jdk
            ;;
    esac

    # Устанавливаем переменные окружения
    export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:/bin/java::")
    echo "JAVA_HOME установлен в: $JAVA_HOME"
}

# --- Начало основного сценария ---

# Проверяем наличие билд-файлов
if [ -f pom.xml ]; then
    BUILD_TOOL="maven"
    echo "Обнаружен Maven-проект."
elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
    BUILD_TOOL="gradle"
    echo "Обнаружен Gradle-проект."
else
    echo "Ошибка: Не найден ни pom.xml, ни build.gradle."
    exit 1
fi

# Определяем версию Java
JAVA_VERSION=""
if [ "$BUILD_TOOL" = "maven" ]; then
    JAVA_VERSION=$(get_java_version_maven)
elif [ "$BUILD_TOOL" = "gradle" ]; then
    JAVA_VERSION=$(get_java_version_gradle)
fi

# Если версия не найдена или не является числом, используем 17 по умолчанию
if ! [[ "$JAVA_VERSION" =~ ^[0-9]+$ ]]; then
    echo "Версия Java не найдена в файлах сборки. Использую JDK 17 по умолчанию."
    JAVA_VERSION="17"
else
    echo "Найдена версия Java: $JAVA_VERSION."
fi

# Устанавливаем Java
install_java "$JAVA_VERSION"

# Проверяем, что Java установлена
echo "Проверяем установку Java..."
java -version
javac -version

# Сборка и запуск проекта
if [ "$BUILD_TOOL" = "maven" ]; then
    echo "Установка Maven..."
    apt-get update && apt-get install -y maven
    mvn -v

    echo "➡ Запуск сборки Maven-проекта..."
    mvn clean package -DskipTests

    # Ищем JAR-файл в папке 'target'
    JAR_FILE=$(find target -maxdepth 1 -type f -name "*.jar" | head -n 1)
    if [ -z "$JAR_FILE" ]; then
        echo "Ошибка: Не найден JAR-файл после сборки!"
        exit 1
    fi

    echo "Запуск $JAR_FILE"
    # 'exec' заменяет текущий процесс оболочки на процесс Java
    exec java -jar "$JAR_FILE"

elif [ "$BUILD_TOOL" = "gradle" ]; then
    echo "➡ Запуск сборки Gradle-проекта..."
    BUILD_SUCCESS=false

    # Проверяем наличие Gradle Wrapper и пытаемся его использовать
    if [ -f gradlew ]; then
        echo "Использую Gradle Wrapper (./gradlew)..."
        # Устанавливаем +e, чтобы скрипт продолжал работать в случае ошибки
        set +e
        ./gradlew build -x test
        # Проверяем код возврата, чтобы понять, была ли ошибка
        if [ $? -eq 0 ]; then
            BUILD_SUCCESS=true
        else
            echo "Ошибка при выполнении Gradle Wrapper. Возвращаюсь к ручной установке Gradle."
        fi
        set -e
    fi

    # Если сборка с помощью Gradle Wrapper не удалась, скачиваем Gradle вручную
    if [ "$BUILD_SUCCESS" = false ]; then
        echo "Gradle Wrapper не найден или не работает. Скачиваю и устанавливаю последнюю версию Gradle..."
        GRADLE_VERSION="8.8"
        GRADLE_URL="https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip"
        GRADLE_DIR="/tmp/gradle-latest"

        rm -rf "$GRADLE_DIR"
        mkdir -p "$GRADLE_DIR"

        echo "Скачивание Gradle с $GRADLE_URL..."
        curl -Ls "$GRADLE_URL" -o "${GRADLE_DIR}/gradle.zip"

        echo "Распаковка..."
        unzip -q "${GRADLE_DIR}/gradle.zip" -d "$GRADLE_DIR"
        export PATH="${GRADLE_DIR}/gradle-${GRADLE_VERSION}/bin:$PATH"

        echo "Проверяем установку Gradle..."
        gradle -v

        # Запускаем сборку
        gradle build -x test
    fi

    # Ищем JAR-файл в папке 'build/libs'
    JAR_FILE=$(find build/libs -maxdepth 1 -type f -name "*.jar" | head -n 1)
    if [ -z "$JAR_FILE" ]; then
        echo "Ошибка: Не найден JAR-файл после сборки!"
        exit 1
    fi

    echo "Запуск $JAR_FILE"
    # 'exec' заменяет текущий процесс оболочки на процесс Java
    exec java -jar "$JAR_FILE"
fi

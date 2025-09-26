#!/bin/bash
set -e

# Проверяем наличие билд-файлов
if [ -f pom.xml ]; then
  BUILD_TOOL="maven"
elif [ -f build.gradle ] || [ -f build.gradle.kts ]; then
  BUILD_TOOL="gradle"
else
  echo "Не найден ни pom.xml, ни build.gradle"
  exit 1
fi

# Установка Java (по умолчанию JDK 17)
apt-get update && apt-get install -y wget curl unzip gnupg && rm -rf /var/lib/apt/lists/*
apt-get install -y openjdk-17-jdk
java -version
javac -version

if [ "$BUILD_TOOL" = "maven" ]; then
  echo "Установка Maven"
  apt-get install -y maven
  mvn -v

  echo "➡Сборка Maven-проекта"
  mvn clean package -DskipTests

  JAR_FILE=$(find target -maxdepth 1 -type f -name "*.jar" | head -n 1)
  if [ -z "$JAR_FILE" ]; then
    echo "Не найден JAR-файл после сборки!"
    exit 1
  fi

  echo "Запуск $JAR_FILE"
  exec java -jar "$JAR_FILE"

elif [ "$BUILD_TOOL" = "gradle" ]; then
  echo "Установка Gradle"
  apt-get install -y gradle
  gradle -v

  echo "Сборка Gradle-проекта"
  gradle build -x test

  JAR_FILE=$(find build/libs -maxdepth 1 -type f -name "*.jar" | head -n 1)
  if [ -z "$JAR_FILE" ]; then
    echo "Не найден JAR-файл после сборки!"
    exit 1
  fi

  echo "Запуск $JAR_FILE"
  exec java -jar "$JAR_FILE"
fi

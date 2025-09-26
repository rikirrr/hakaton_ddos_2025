#!/bin/bash
set -e

# Проверяем наличие package.json
if [ ! -f package.json ]; then
  echo "package.json не найден!"
  exit 1
fi

# Определяем версию Node.js из package.json (если есть)
NODE_VERSION=$(grep '"node"' package.json | sed -E 's/.*"node": *"([^"]+)".*/\1/' || true)

# Устанавливаем Node.js и npm
apt-get update && apt-get install -y curl ca-certificates gnupg && rm -rf /var/lib/apt/lists/*

# Если версия указана в package.json — используем её, иначе ставим LTS (18.x)
if [ -n "$NODE_VERSION" ]; then
  echo "Установка Node.js версии $NODE_VERSION"
  curl -fsSL https://deb.nodesource.com/setup_"$NODE_VERSION".x | bash -
else
  echo "Установка Node.js LTS (18)"
  curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
fi

apt-get install -y nodejs
node -v
npm -v

# Устанавливаем зависимости
npm install

# Определяем тип проекта и запускаем
if grep -q '"next"' package.json; then
  echo "➡Next.js проект"
  npm run build
  exec npm run start

elif grep -q '"nuxt"' package.json; then
  echo "Nuxt.js проект"
  npm run build
  exec npm run start

elif grep -q '"@angular/core"' package.json; then
  echo "Angular проект"
  exec npm run start

elif grep -q '"vue"' package.json; then
  echo "Vue.js проект"
  npm run build
  exec npm run preview || npm run serve

elif grep -q '"react"' package.json; then
  echo "React проект"
  npm run build
  exec npm run start || npx serve -s build

else
  echo "Неизвестный проект, запускаю npm start"
  exec npm start
fi

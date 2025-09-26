#!/bin/bash

set -e
if [ ! -f package.json ]; then
  echo "ackage.json не найден!"
  exit 1
fi

npm install

if grep -q '"next"' package.json; then
  echo "➡️ Next.js проект"
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
  echo "Неизвестный проект, просто запускаю npm start"
  exec npm start
fi

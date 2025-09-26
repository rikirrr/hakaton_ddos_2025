FROM ubuntu:22.04

ARG LANG_NAME
RUN apt-get update

WORKDIR /app
COPY . .

# Скопировать скрипт в имя на основе LANG_NAME
COPY ${LANG_NAME}_run.sh /usr/local/bin/${LANG_NAME}_run.sh
RUN chmod +x /usr/local/bin/${LANG_NAME}_run.sh

ENTRYPOINT ["/usr/local/bin/${LANG_NAME}_run.sh"]

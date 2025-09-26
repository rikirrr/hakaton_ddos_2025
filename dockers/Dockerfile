FROM ubuntu:22.04

ARG LANG_NAME
RUN apt-get update

WORKDIR /app
COPY . .

COPY dockers/${LANG_NAME}_run.sh /usr/local/bin/${LANG_NAME}_run.sh
RUN chmod +x /usr/local/bin/${LANG_NAME}_run.sh

RUN ln -s /usr/local/bin/${LANG_NAME}_run.sh /usr/local/bin/run.sh

ENTRYPOINT ["/usr/local/bin/run.sh"]

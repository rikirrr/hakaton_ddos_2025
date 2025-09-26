#!/bin/bash
set -e

apt-get update && apt-get install -y software-properties-common curl \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip

if [ -f requirements.txt ]; then
    echo "Установка через pip requirements.txt"
    pip install --no-cache-dir -r requirements.txt

elif [ -f pyproject.toml ]; then
    echo "Установка через poetry"
    pip install --no-cache-dir poetry
    python -m venv .venv
    source .venv/bin/activate
    poetry install --no-root

elif [ -f environment.yml ]; then
    echo "Установка через conda environment.yml"
    curl -sSL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
    bash miniconda.sh -b -p /opt/conda
    rm miniconda.sh
    export PATH="/opt/conda/bin:$PATH"
    conda env update -f environment.yml
    source /opt/conda/etc/profile.d/conda.sh
    ENV_NAME=$(head -1 environment.yml | awk '{print $2}')
    conda activate "$ENV_NAME"
fi

exec python main.py

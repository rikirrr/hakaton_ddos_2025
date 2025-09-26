#!/bin/bash
set -e

if [ -f requirements.txt ]; then
    echo ">>> Installing via pip requirements.txt"
    pip install -r requirements.txt

elif [ -f pyproject.toml ]; then
    echo ">>> Installing via poetry"
    pip install poetry
    poetry install --no-root

elif [ -f environment.yml ]; then
    echo ">>> Installing via conda environment.yml"
    apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
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

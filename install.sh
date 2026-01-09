#!/bin/bash

if ! command -v conda &> /dev/null; then
    echo "Conda não encontrado. Instalando Miniconda..."
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    MINICONDA_PATH="$HOME/.miniconda3"

    wget "$MINICONDA_URL" -O miniconda.sh

    bash miniconda.sh -b -p "$MINICONDA_PATH"
    rm miniconda.sh

    "$MINICONDA_PATH/bin/conda" init bash

    . ~/.bashrc
    echo "Miniconda instalado em $MINICONDA_PATH"
fi

eval "$(conda shell.bash hook 2> /dev/null)"

conda env create -f environment.yml
conda activate MobMetrics

echo "Executando makemigrations e migrate..."
python MobMetrics/manage.py makemigrations metrics
python MobMetrics/manage.py migrate

echo "Instalação concluída! Ative o ambiente com: conda activate MobMetrics."

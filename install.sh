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

# Verifica e instala JDK no ambiente ativo
if ! command -v java &> /dev/null; then
    echo "JDK não encontrado. Instalando OpenJDK mais recente no ambiente MobMetrics..."
    conda install -y -c conda-forge openjdk
    echo "JDK instalado e disponível em $(command -v java)"
else
    echo "JDK já disponível: $(java -version 2>&1 | head -n1)"
fi

# NOVA SEÇÃO: Baixa e instala BonnMotion no diretório atual
echo "Baixando BonnMotion v3.0.1..."
BONNMOTION_URL="https://bonnmotion.sys.cs.uos.de/src/bonnmotion-3.0.1.zip"
BONNMOTION_DIR="bonnmotion-3.0.1"

wget "$BONNMOTION_URL" -O bonnmotion.zip
unzip -o bonnmotion.zip  # -o sobrescreve se existir
rm bonnmotion.zip

if [ -d "$BONNMOTION_DIR" ]; then
    cd "$BONNMOTION_DIR"
    echo "Instalando BonnMotion..."
    ./install  # Requer JDK; compila ferramentas de mobilidade
    echo "BonnMotion instalado em ./$BONNMOTION_DIR. Use ./bin/bm para rodar."
    cd ..
else
    echo "Erro: Diretório $BONNMOTION_DIR não encontrado após extração."
    exit 1
fi

echo "Executando makemigrations e migrate..."
python MobMetrics/manage.py makemigrations metrics
python MobMetrics/manage.py migrate

echo "Instalação concluída! Ative o ambiente com: conda activate MobMetrics."
echo "BonnMotion pronto em ./bonnmotion-3.0.1/bin/bm."

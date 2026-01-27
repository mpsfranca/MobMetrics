#!/bin/bash

if ! command -v conda &> /dev/null; then
    echo "Conda not found. Installing Miniconda..."
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    MINICONDA_PATH="$HOME/.miniconda3"

    wget "$MINICONDA_URL" -O miniconda.sh

    bash miniconda.sh -b -p "$MINICONDA_PATH"
    rm miniconda.sh

    "$MINICONDA_PATH/bin/conda" init bash

    . ~/.bashrc
    echo "Miniconda installed at $MINICONDA_PATH"
fi

eval "$(conda shell.bash hook 2> /dev/null)"

conda env create -f environment.yml
conda activate MobMetrics

# Check and install JDK in the active environment
if ! command -v java &> /dev/null; then
    echo "JDK not found. Installing the latest OpenJDK in the MobMetrics environment..."
    conda install -y -c conda-forge openjdk
    echo "JDK installed and available at $(command -v java)"
else
    echo "JDK already available: $(java -version 2>&1 | head -n1)"
fi

# Download and install BonnMotion in the current directory
echo "Downloading BonnMotion v3.0.1..."
BONNMOTION_URL="https://bonnmotion.sys.cs.uos.de/src/bonnmotion-3.0.1.zip"
BONNMOTION_DIR="bonnmotion-3.0.1"

wget "$BONNMOTION_URL" -O bonnmotion.zip
unzip -o bonnmotion.zip  # -o overwrites if it already exists
rm bonnmotion.zip

if [ -d "$BONNMOTION_DIR" ]; then
    cd "$BONNMOTION_DIR"
    echo "Installing BonnMotion..."
    ./install  # Requires JDK; compiles mobility tools
    echo "BonnMotion installed in ./$BONNMOTION_DIR. Use ./bin/bm to run."
    cd ..
else
    echo "Error: Directory $BONNMOTION_DIR not found after extraction."
    exit 1
fi

echo "Running makemigrations and migrate..."
python MobMetrics/manage.py makemigrations metrics
python MobMetrics/manage.py migrate

echo "Installation complete! Activate the environment with: conda activate MobMetrics."
echo "BonnMotion ready at ./bonnmotion-3.0.1/bin/bm."

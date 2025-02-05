#!/bin/bash

# Check if Python and pip are installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install Python3 and try again."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip3 could not be found. Please install pip3 and try again."
    exit 1
fi

# Create a virtual environment
VENV_NAME="venv"
python3 -m venv $VENV_NAME

source $VENV_NAME/bin/activate

if [ ! -f requirements.txt ]; then
    echo "requirements.txt not found. Please ensure the file is in the current directory."
    deactivate
    exit 1
fi

pip3 install -r requirements.txt

OS=$(uname)

# Install python-tk based on the operating system
# nota Windows (using Git Bash or similar)
if [ "$OS" == "Darwin" ]; then
    echo "Installing python-tk for macOS..."
    brew install python-tk
elif [ "$OS" == "Linux" ]; then
    echo "Installing python-tk for Linux..."
    sudo apt-get update
    sudo apt-get install -y python3-tk
elif [ "$OS" == "MINGW32_NT-10.0" ] || [ "$OS" == "MSYS_NT-10.0" ]; then
    echo "Installing python-tk for Windows..."
    pip3 install python-tk
else
    echo "Unsupported operating system: $OS"
    deactivate
    exit 1
fi


echo "Virtual environment '$VENV_NAME' created and requirements installed successfully."


PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium


PLAYWRIGHT_BROWSERS_PATH=0 python3 pnt/sipot/gui.py

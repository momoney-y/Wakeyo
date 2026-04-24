@echo off
if not exist "venv\Scripts\activate.bat" (
    python -m venv venv
)

call "venv\Scripts\activate.bat"

python -m pip install --upgrade pip
pip install tk

python main.py

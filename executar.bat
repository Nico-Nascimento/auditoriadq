@echo off
REM Roda o programa direto pelo Python (para testar sem gerar o .exe)
cd /d "%~dp0"
python -m pip install -r requirements.txt --quiet
python main.py
if errorlevel 1 pause

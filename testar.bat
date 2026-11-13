@echo off
REM Roda o teste automatico (sem abrir janela)
cd /d "%~dp0"
python -m pip install -r requirements.txt --quiet
python testes\teste_rapido.py
pause

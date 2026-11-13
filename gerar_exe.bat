@echo off
REM Gera o arquivo dist\AuditoriaDQ.exe (um arquivo unico, nao precisa de Python para rodar)
cd /d "%~dp0"
python -m pip install -r requirements.txt pyinstaller --quiet
python -m PyInstaller --noconfirm --clean --onefile --windowed ^
  --name AuditoriaDQ ^
  --add-data "app\snippets_padrao.json;app" ^
  main.py
echo.
echo Pronto! O programa esta em: %~dp0dist\AuditoriaDQ.exe
pause

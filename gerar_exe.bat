@echo off
REM Gera a pasta dist\AuditoriaDQ com o programa (nao precisa de Python para rodar)
cd /d "%~dp0"
python -m pip install -r requirements.txt pyinstaller --quiet
python -m PyInstaller --noconfirm --clean --onedir --windowed ^
  --name AuditoriaDQ ^
  --icon "app\assets\icone.ico" ^
  --add-data "app\snippets_padrao.json;app" ^
  --add-data "app\assets;app\assets" ^
  main.py
echo.
copy /y "distribuicao\COMO INSTALAR.txt" "dist\AuditoriaDQ\" >nul
echo Pronto! O programa esta em: %~dp0dist\AuditoriaDQ\AuditoriaDQ.exe
pause

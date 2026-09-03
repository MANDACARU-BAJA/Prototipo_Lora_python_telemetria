@echo off
setlocal
title Mandacaru Baja - Telemetria
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Preparando o ambiente pela primeira vez...
    python -m venv .venv
    if errorlevel 1 goto :erro_ambiente
)

".venv\Scripts\python.exe" -c "import streamlit, pandas, plotly, serial" >nul 2>&1
if errorlevel 1 (
    echo Instalando as bibliotecas necessarias...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :erro_dependencias
)

echo.
echo Iniciando a telemetria Mandacaru Baja...
echo Para encerrar, pressione Ctrl+C nesta janela.
echo.
".venv\Scripts\python.exe" -m streamlit run app.py --browser.gatherUsageStats false
goto :fim

:erro_ambiente
echo.
echo Nao foi possivel criar o ambiente Python.
echo Verifique se o Python esta instalado no computador.
pause
goto :fim

:erro_dependencias
echo.
echo Nao foi possivel instalar as bibliotecas do projeto.
echo Verifique a conexao com a internet e tente novamente.
pause

:fim
endlocal

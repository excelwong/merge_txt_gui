@echo off
chcp 65001 >nul 2>nul
setlocal
set "PY=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not exist "%PY%" set "PY=python.exe"
start "" "%PY%" "%~dp0merge_txt_gui.py"
endlocal

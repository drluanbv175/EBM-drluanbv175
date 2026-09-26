@echo off
rem Nhap KENH CANH BAO (Gmail/SMTP/webhook) - dong kiem ESD10. CHI BAC SI TU BAM.
chcp 65001 >nul
cd /d "%~dp0"
set "PY=%USERPROFILE%\.ebm-venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" tools\nhap_kenh_canh_bao.py
echo.
pause

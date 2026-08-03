@echo off
REM Bam dup file nay tren Windows de tro ~\workspace\medsci-skills ve ban medsci dang cai
REM (junction, khong can admin). Chay lai sau moi lan plugin medsci cap nhat.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix-medsci-root.ps1"
echo.
pause

@echo off
REM Bam dup file nay tren Windows de chep bo lenh tieng Viet
REM tu hub OneDrive -> %USERPROFILE%\.claude\commands\
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0copy-commands-vi.ps1"
echo.
pause

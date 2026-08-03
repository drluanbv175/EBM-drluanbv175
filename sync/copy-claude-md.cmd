@echo off
REM Bam dup file nay tren Windows de chep chi thi ngon ngu toan cuc
REM tu hub OneDrive -> %USERPROFILE%\.claude\CLAUDE.md
REM Chay lai bao nhieu lan cung an toan.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0copy-claude-md.ps1"
echo.
pause

@echo off
REM Bam dup file nay tren Windows de tro thu muc memory -> hub OneDrive (junction, khong can admin).
REM Chay lai bao nhieu lan cung an toan.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0link-memory.ps1"
echo.
pause

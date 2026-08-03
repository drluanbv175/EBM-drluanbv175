@echo off
REM Bam dup file nay tren Windows de tro tung skill EBM -> ~\.claude\skills (junction, khong can admin).
REM Chay lai bao nhieu lan cung an toan.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0link-skills.ps1"
echo.
pause

@echo off
REM Bam dup de tro skill EBM vao ~\.claude\skills (junction, khong can admin). Runtime ~\.codex da go 19/11/2026.
REM Chay lai bao nhieu lan cung an toan.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0link-skills.ps1"
echo.
pause

@echo off
REM Bam dup de tro skill EBM vao ca ~\.claude\skills va ~\.codex\skills (junction, khong can admin).
REM Chay lai bao nhieu lan cung an toan.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0link-skills.ps1"
echo.
pause

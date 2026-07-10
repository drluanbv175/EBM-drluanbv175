@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "LOG=%~dp0_run_real_result.txt"
> "%LOG%" echo === REAL INGEST EBM_MASTER %DATE% %TIME% ===
cd /d "%~dp0rag"
echo --- ingest.py --source EBM_MASTER.json (so chung cu that, 172 the) --- >> "%LOG%"
python ingest.py --source "..\..\EBM_MASTER\EBM_MASTER.json" >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo --- query demo (khong dau de tranh loi codepage) --- >> "%LOG%"
python query.py "SGLT2i suy tim dai thao duong nhap vien" --k 5 >> "%LOG%" 2>&1
echo === DONE === >> "%LOG%"

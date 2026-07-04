@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "LOG=%~dp0_run_result.txt"
> "%LOG%" echo === RUN ON MACHINE (UTF-8) %DATE% %TIME% ===
echo --- pip install scikit-learn pyyaml (user site) --- >> "%LOG%"
python -m pip install --user scikit-learn pyyaml >> "%LOG%" 2>&1
echo install exit=%ERRORLEVEL% >> "%LOG%"
echo. >> "%LOG%"
echo ====================== RAG ====================== >> "%LOG%"
cd /d "%~dp0rag"
echo --- ingest.py (de-id + embed synthetic) --- >> "%LOG%"
python ingest.py >> "%LOG%" 2>&1
echo --- compare_backends.py (TF-IDF vs hashing) --- >> "%LOG%"
python compare_backends.py >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo ===================== EVAL ====================== >> "%LOG%"
cd /d "%~dp0eval"
echo --- good_output --- >> "%LOG%"
python run_eval.py sample_outputs/good_output.md --gold gold/template.yaml >> "%LOG%" 2>&1
echo --- bad_output --- >> "%LOG%"
python run_eval.py sample_outputs/bad_output.md --gold gold/template.yaml >> "%LOG%" 2>&1
echo --- good_antibiotic --- >> "%LOG%"
python run_eval.py sample_outputs/good_antibiotic.md --gold gold/template.yaml >> "%LOG%" 2>&1
echo --- bad_causal_cross_sectional --- >> "%LOG%"
python run_eval.py sample_outputs/bad_causal_cross_sectional.md --gold gold/template.yaml >> "%LOG%" 2>&1
echo === DONE === >> "%LOG%"

@echo off
> "%~dp0_probe_result.txt" echo === ENV PROBE %DATE% %TIME% ===
echo --- where python --- >> "%~dp0_probe_result.txt"
where python >> "%~dp0_probe_result.txt" 2>&1
echo --- python --version --- >> "%~dp0_probe_result.txt"
python --version >> "%~dp0_probe_result.txt" 2>&1
echo --- py -3 --version --- >> "%~dp0_probe_result.txt"
py -3 --version >> "%~dp0_probe_result.txt" 2>&1
echo --- where pip --- >> "%~dp0_probe_result.txt"
where pip >> "%~dp0_probe_result.txt" 2>&1
echo --- import sklearn --- >> "%~dp0_probe_result.txt"
python -c "import sklearn,sys; print('sklearn', sklearn.__version__)" >> "%~dp0_probe_result.txt" 2>&1
echo === DONE === >> "%~dp0_probe_result.txt"

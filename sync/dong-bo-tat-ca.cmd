@echo off
REM DONG BO TAT CA (Windows) - bam dup file nay.
REM Chay tools\dong_bo_tat_ca.py --ap-dung theo dung thu tu phu thuoc:
REM   an toan -> git -> skill -> agent -> plugin -> hook -> bo nho -> kho cong cu
REM Cong cu luon SAO LUU truoc khi ghi, KHONG cai/go plugin qua mang, va KHONG
REM dung toi noi dung y khoa. Chot an toan do (do) se DUNG toan bo.
setlocal
cd /d "%~dp0.."
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
chcp 65001 >nul

REM Windows khong co lenh "python3". Uu tien launcher "py", roi "python".
set "PYEXE="
where py >nul 2>&1 && set "PYEXE=py -3"
if not defined PYEXE (
  where python >nul 2>&1 && set "PYEXE=python"
)

if not defined PYEXE (
  echo Khong tim thay Python tren may nay. Cai Python 3.12+ roi chay lai.
  pause
  exit /b 2
)

%PYEXE% tools\dong_bo_tat_ca.py --ap-dung
set MA=%ERRORLEVEL%
echo.
echo (ma thoat %MA% - 0 khop . 1 con viec . 2 phai dung)
pause
exit /b %MA%

@echo off
REM XUAT MIRROR CHUNG CU CHO CLOUD (Windows) - bam dup file nay.
REM Chay tools\xuat_trang_thai_cloud.py: doc lai 3 bo dem da co san (do tuoi .
REM quyet dinh da duyet . viec-con-lai) + 2 so quyet dinh, ghi MOT JSON nho vao
REM cloud-mirror\ - de phien Claude Code tren Cloud thay duoc trang thai moi
REM nhat cua EBM-Dashboards\ (thu nam ngoai git, Cloud khong co).
REM CHI ghi file - KHONG tu commit/push (cung nguyen tac dong-bo-tat-ca.cmd:
REM day ho la quyet dinh thay bac si ve thu duoc cong bo). Buoc git o cuoi la TAY.
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

%PYEXE% tools\xuat_trang_thai_cloud.py
set MA=%ERRORLEVEL%
echo.
if %MA%==0 (
  echo Xong. Muon Cloud thay trang thai nay, chay 3 lenh (bac si tu soat truoc khi day):
  echo   git add cloud-mirror/
  echo   git commit -m "chore(cloud): cap nhat mirror trang thai chung cu"
  echo   git push
)
echo (ma thoat %MA%)
pause
exit /b %MA%

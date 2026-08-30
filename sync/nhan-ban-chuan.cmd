@echo off
REM NHAN BAN CHUAN (Windows) - bam dup file nay sau khi master co ban moi.
REM Chay TRON chuoi nhan ban: keo master -> an toan dong bo (do la DUNG) ->
REM dong bo 8 lan -> do + bat tram web hoi -> chot bai hoc lan cuoi lam moc dat.
REM Dung 30/08/2026 theo yeu cau "chay luon" cua bac si - chuoi 6 lenh phai nho
REM la chuoi se bi bo sot buoc (cung bai hoc da sinh ra dong_bo_tat_ca/BH71).
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
  echo Khong tim thay Python. Cai Python 3.11+ roi chay lai.
  pause
  exit /b 2
)

echo == 1. Keo ban chuan master ==
git pull origin master
if errorlevel 1 goto loi_git

echo == 2. An toan dong bo (do la DUNG toan bo) ==
%PYEXE% tools\sync_safety_check.py
if errorlevel 2 goto loi_antoan

echo == 3. Dong bo 8 lan (tu sao luu truoc khi ghi) ==
%PYEXE% tools\dong_bo_tat_ca.py --ap-dung

echo == 4. Do tram web hoi (chi do, khong ghi) ==
%PYEXE% tools\giam_sat_to_chuc.py --kiem-tra
echo == 5. Bat tram do dat (not-covered thanh active, tu sao luu so) ==
%PYEXE% tools\giam_sat_to_chuc.py --bat-neu-ok

echo == 6. MOC DAT: bo chot bai hoc voi day du nguyen lieu ==
%PYEXE% tools\chot_hoi_quy_bai_hoc.py
set MA=%errorlevel%

echo.
echo Xong. Moc dat cua hai he: 0 bai hoc tai phat voi 0 muc trang tren CA HAI may.
echo Can bac si kiem chung.
pause
exit /b %MA%

:loi_git
echo git pull hong - DUNG. Kiem mang/xung dot roi chay lai.
pause
exit /b 2

:loi_antoan
echo An toan dong bo bao DO - DUNG. Dong bo khi cay dang hong la nhan ban cai hong.
pause
exit /b 2

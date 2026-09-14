@echo off
title Epilepsi Karar Agaci ve Hasta Veri Ambari Portali
cd /d "%~dp0"

echo ========================================================
echo   Epilepsi Karar Agaci ve Hasta Veri Ambari Portali
echo   Sistem Baslatiliyor, lutfen bekleyiniz...
echo ========================================================
echo.

REM Varsa eski port 8501 takilmasini temizle
for /f "tokens=5" %%a in ('netstat -a -n -o ^| findstr :8501 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)

REM Tarayiciyi otomatik ac
start http://localhost:8501

echo.
echo Tarayiciniz acildi: http://localhost:8501
echo Portali acik tutmak icin BU PENCEREYI KAPATMAYINIZ.
echo Kapatmak istediginizde bu siyah pencereyi kapatmaniz yeterlidir.
echo ========================================================
echo.

.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501 --server.headless false

pause

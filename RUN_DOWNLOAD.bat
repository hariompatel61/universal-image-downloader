@echo off
title Study Break - Google Product Image Downloader
echo.
echo ================================================
echo   STUDY BREAK - PRODUCT IMAGE DOWNLOADER
echo ================================================
echo.
echo Installing required packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Python/pip installation failed.
    pause
    exit /b 1
)
echo.
echo Starting Google Images downloader...
python universal_google_image_bulk_downloader.py
pause

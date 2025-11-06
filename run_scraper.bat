@echo off
echo Starting Chartink Scraper...
echo.

REM Activate virtual environment if it exists
if exist "myvenv\Scripts\activate.bat" (
    call myvenv\Scripts\activate.bat
)

REM Run the scraper
python chartink_scraper.py

pause

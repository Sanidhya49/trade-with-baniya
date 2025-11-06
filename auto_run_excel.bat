@echo off
REM Automatic Excel Generator for Nifty 100 Gainers & Losers
REM This script runs the Python script to generate Excel files automatically

cd /d "%~dp0"
echo ========================================
echo Auto Excel Generator - Nifty 100
echo ========================================
echo.
echo [%date% %time%] Starting automatic Excel generation...
echo.

REM Activate virtual environment
call myvenv\Scripts\activate.bat

REM Run the Python script
python main_gainers_losers.py

REM Check if Excel file was created
if exist "nifty100_gainers_losers.xlsx" (
    echo.
    echo [SUCCESS] Excel file generated: nifty100_gainers_losers.xlsx
    echo [INFO] File location: %CD%\nifty100_gainers_losers.xlsx
) else (
    echo.
    echo [WARNING] Excel file not found. Check for errors above.
)

echo.
echo [%date% %time%] Process completed.
echo ========================================
echo.

REM Keep window open for 3 seconds to see results
timeout /t 3 /nobreak >nul


@echo off
REM Quick helper script to backup and update the CSV file
REM This script helps you safely update ind_nifty100list.csv

cd /d "%~dp0"
echo ========================================
echo Nifty 100 CSV Update Helper
echo ========================================
echo.

if not exist "ind_nifty100list.csv" (
    echo [ERROR] ind_nifty100list.csv not found in current folder!
    echo.
    echo Please ensure:
    echo   1. You're running this from the project folder
    echo   2. The CSV file exists
    pause
    exit /b 1
)

echo Current CSV file found: ind_nifty100list.csv
echo.

REM Create backup
set "backup_name=ind_nifty100list_backup_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.csv"
set "backup_name=%backup_name: =0%"

echo Creating backup...
copy "ind_nifty100list.csv" "%backup_name%" >nul
if %errorlevel% equ 0 (
    echo [OK] Backup created: %backup_name%
) else (
    echo [WARNING] Could not create backup
)
echo.

echo ========================================
echo Instructions:
echo ========================================
echo.
echo 1. Place your NEW CSV file in this folder
echo 2. Name it: ind_nifty100list.csv
echo 3. Replace the old file when prompted
echo.
echo The script will automatically use the new CSV
echo on the next run (manual or scheduled).
echo.
echo ========================================
echo.

REM Open the folder in Explorer
echo Opening folder in Explorer...
start explorer .

echo.
echo Press any key to exit...
pause >nul


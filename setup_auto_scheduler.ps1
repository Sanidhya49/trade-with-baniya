# PowerShell script to set up Windows Task Scheduler for automatic Excel generation
# Run this script as Administrator to set up automatic execution

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Auto Excel Generator - Task Scheduler Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$batFile = Join-Path $scriptPath "auto_run_excel.bat"

# Check if batch file exists
if (-not (Test-Path $batFile)) {
    Write-Host "[ERROR] auto_run_excel.bat not found!" -ForegroundColor Red
    Write-Host "Please ensure auto_run_excel.bat is in the same directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Batch file found: $batFile" -ForegroundColor Green
Write-Host ""

# Task name
$taskName = "Nifty100_Auto_Excel_Generator"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "[WARNING] Task '$taskName' already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to delete and recreate it? (Y/N)"
    if ($response -eq "Y" -or $response -eq "y") {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "[INFO] Existing task deleted." -ForegroundColor Green
    } else {
        Write-Host "[INFO] Keeping existing task. Exiting." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Select schedule frequency:" -ForegroundColor Cyan
Write-Host "1. Every 3 minutes (for testing)"
Write-Host "2. Every 15 minutes (recommended)"
Write-Host "3. Every 30 minutes"
Write-Host "4. Every hour"
Write-Host "5. Every day at 9:00 AM (market open)"
Write-Host "6. Custom (you'll configure manually)"
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

# Define trigger based on choice
$trigger = $null
$description = ""

switch ($choice) {
    "1" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 3) -RepetitionDuration (New-TimeSpan -Days 365)
        $description = "Runs every 3 minutes"
    }
    "2" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
        $description = "Runs every 15 minutes"
    }
    "3" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 30) -RepetitionDuration (New-TimeSpan -Days 365)
        $description = "Runs every 30 minutes"
    }
    "4" {
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Days 365)
        $description = "Runs every hour"
    }
    "5" {
        $trigger = New-ScheduledTaskTrigger -Daily -At "9:00AM"
        $description = "Runs daily at 9:00 AM"
    }
    "6" {
        Write-Host "[INFO] Please configure the task manually in Task Scheduler after creation." -ForegroundColor Yellow
        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date)
        $description = "Custom schedule (configure manually)"
    }
    default {
        Write-Host "[ERROR] Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Create action (run the batch file)
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$batFile`"" -WorkingDirectory $scriptPath

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Automatically generates Nifty 100 Gainers & Losers Excel file. $description" | Out-Null
    
    Write-Host ""
    Write-Host "[SUCCESS] Task scheduled successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  Name: $taskName" -ForegroundColor White
    Write-Host "  Schedule: $description" -ForegroundColor White
    Write-Host "  Script: $batFile" -ForegroundColor White
    Write-Host ""
    Write-Host "To manage the task:" -ForegroundColor Yellow
    Write-Host "  1. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
    Write-Host "  2. Find task: '$taskName'" -ForegroundColor White
    Write-Host "  3. Right-click to Run, Edit, or Delete" -ForegroundColor White
    Write-Host ""
    Write-Host "To test immediately, run:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to create scheduled task!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure you're running PowerShell as Administrator!" -ForegroundColor Yellow
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


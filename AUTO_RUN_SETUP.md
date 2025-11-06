# Automatic Excel Generator Setup Guide

This guide will help you set up automatic execution of the Excel generator script.

## 📋 What This Does

- Automatically runs the script at scheduled intervals
- Generates `nifty100_gainers_losers.xlsx` automatically
- Updates the Excel file with latest data from Chartink
- No manual intervention needed!

## 🚀 Quick Setup (Recommended)

### Method 1: Using PowerShell Script (Easiest)

1. **Right-click** on `setup_auto_scheduler.ps1`
2. Select **"Run with PowerShell"** (or "Run as Administrator" if needed)
3. Follow the prompts to select your schedule:
   - Every 3 minutes (for testing)
   - Every 15 minutes (recommended)
   - Every 30 minutes
   - Every hour
   - Daily at 9:00 AM
   - Custom

4. The task will be created automatically!

### Method 2: Manual Windows Task Scheduler Setup

1. Press `Win + R`, type `taskschd.msc`, press Enter
2. Click **"Create Basic Task"** in the right panel
3. Name it: `Nifty100_Auto_Excel_Generator`
4. Choose trigger: **Daily** or **When I log on**
5. Set time: **9:00 AM** (or your preferred time)
6. Action: **Start a program**
7. Program/script: Browse to `auto_run_excel.bat`
8. Start in: Browse to your project folder
9. Click **Finish**

### Method 3: Run Every X Minutes (Advanced)

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task (as above)
3. After creating, **right-click** the task → **Properties**
4. Go to **Triggers** tab → **Edit**
5. Check **"Repeat task every"** → Select interval (e.g., 15 minutes)
6. Duration: **Indefinitely**
7. Click **OK**

## 📁 Files Created

- `nifty100_gainers_losers.xlsx` - The automatically generated Excel file
- Location: Same folder as the script

## ⚙️ Schedule Options

### For Active Trading Hours (9:30 AM - 3:30 PM IST)
- **Every 15 minutes** - Good balance of freshness and API load
- **Every 30 minutes** - Less frequent, still timely

### For Testing
- **Every 3 minutes** - Quick testing, but uses more resources

### For Daily Updates
- **Daily at 9:00 AM** - Once per day before market opens

## 🔍 Verify It's Working

1. Open Task Scheduler (`taskschd.msc`)
2. Find task: `Nifty100_Auto_Excel_Generator`
3. Check **Last Run Result** - Should show "0x0" (success)
4. Check your folder for `nifty100_gainers_losers.xlsx`
5. Check file's **Modified Date** - Should update automatically

## 🛠️ Troubleshooting

### Task Not Running?
1. Check Task Scheduler → Task status (should be "Ready")
2. Right-click task → **Run** to test manually
3. Check **History** tab for errors
4. Ensure `auto_run_excel.bat` path is correct

### Excel File Not Updating?
1. Make sure Excel file is **closed** when script runs
2. Check if `main_gainers_losers.py` has errors
3. Run `auto_run_excel.bat` manually to see errors

### Permission Issues?
1. Run PowerShell **as Administrator**
2. Ensure your user has permission to create scheduled tasks
3. Check if antivirus is blocking the script

## 📝 Manual Test

To test the script manually:
1. Double-click `auto_run_excel.bat`
2. Check if `nifty100_gainers_losers.xlsx` is created/updated
3. Verify the data is correct

## 🎯 Best Practices

1. **Schedule during market hours** (9:30 AM - 3:30 PM IST) for live data
2. **Don't open Excel file** while script is running
3. **Check logs** in Task Scheduler History if issues occur
4. **Start with 15-minute intervals** and adjust as needed

## 📞 Need Help?

- Check Task Scheduler → History tab for error messages
- Run `auto_run_excel.bat` manually to see console output
- Verify Python virtual environment is activated correctly

---

**Note:** The script will automatically clean up old Excel files and generate fresh ones each time it runs.


# How to Update Nifty 100 CSV File

## 📋 Quick Answer

**Simply replace the old `ind_nifty100list.csv` file with the new one, keeping the same filename.**

## 🔄 Step-by-Step Update Process

### Method 1: Direct Replacement (Easiest)

1. **Download the latest Nifty 100 list** from:
   - NSE website: https://www.nseindia.com/market-data/indices-watch
   - Or your data provider

2. **Save it as `ind_nifty100list.csv`** in the project folder:
   ```
   D:\trade with baniya\ind_nifty100list.csv
   ```

3. **Replace the old file** - Just overwrite it when prompted

4. **That's it!** The script will automatically use the new list on the next run.

### Method 2: Using File Explorer

1. Open the project folder: `D:\trade with baniya`
2. Find the old `ind_nifty100list.csv` file
3. Delete it (or rename to `ind_nifty100list_old.csv` as backup)
4. Copy your new CSV file into the folder
5. Rename it to `ind_nifty100list.csv` (exact name, case-sensitive)

## 📝 CSV File Requirements

Your CSV file **MUST** have these columns:
- `Symbol` - The stock symbol (e.g., RELIANCE, TCS, HDFCBANK)
- Other columns are optional but recommended:
  - `Company Name`
  - `Industry`
  - `Series`
  - `ISIN Code`

### Example CSV Format:
```csv
Company Name,Industry,Symbol,Series,ISIN Code
Reliance Industries Ltd.,Oil & Gas,RELIANCE,EQ,INE002A01018
Tata Consultancy Services Ltd.,Information Technology,TCS,EQ,INE467B01029
```

## ✅ Verification

After updating the CSV:

1. **Check the file exists**: `D:\trade with baniya\ind_nifty100list.csv`
2. **Run the script manually** to test:
   ```
   Double-click: auto_run_excel.bat
   ```
3. **Check the output** - It should show:
   ```
   [INFO] Loaded XXX Nifty 100 stocks from CSV
   ```
   (XXX will be the new count, typically 100)

4. **Check Excel file** - The timestamp row will show the CSV version info

## 🔍 Where CSV is Used

The CSV file is used in:
- ✅ `main_gainers_losers.py` - Main Excel generator
- ✅ `streamlit_app.py` - Web interface (default option)
- ✅ `main.py` - Standalone script

All scripts look for: `ind_nifty100list.csv` in the project root folder.

## 📅 When to Update

Update the CSV when:
- ✅ NSE announces changes to Nifty 100 composition
- ✅ Quarterly rebalancing (typically March, June, September, December)
- ✅ New stocks are added or removed from the index
- ✅ You want to ensure you're using the latest official list

## 🛡️ Backup Recommendation

Before replacing, consider backing up the old file:
```
ind_nifty100list.csv → ind_nifty100list_backup_20250107.csv
```

## 🚨 Important Notes

1. **Filename must be exact**: `ind_nifty100list.csv` (case-sensitive)
2. **Location must be correct**: Same folder as `main_gainers_losers.py`
3. **Format must match**: Must have `Symbol` column
4. **No need to restart**: Script will pick up changes automatically on next run
5. **Automatic scheduler**: If you have auto-scheduler running, it will use the new CSV automatically

## 📊 Tracking CSV Version

The Excel file will automatically show:
- Number of stocks loaded from CSV
- Last update timestamp
- This helps you verify the correct CSV is being used

## ❓ Troubleshooting

### Script shows old stock count?
- Make sure you saved the new CSV file
- Check the filename is exactly `ind_nifty100list.csv`
- Verify the file is in the correct folder

### Script can't find CSV?
- Check file location: `D:\trade with baniya\ind_nifty100list.csv`
- Verify filename spelling (case-sensitive)
- Make sure file isn't open in Excel

### Wrong stocks appearing?
- Verify CSV has `Symbol` column
- Check CSV format matches the example above
- Ensure symbols are in uppercase (script normalizes them)

---

**Remember**: Just replace the file with the same name - that's all you need to do! 🎯


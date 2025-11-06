# Streamlit Stock Screener App

A web-based application to view Nifty stock gainers and losers with CSV upload support.

## Features

✅ **Two Tables Side by Side**
- Top Gainers (Open = High) on the left
- Top Losers (Open = Low) on the right

✅ **CSV Upload Support**
- Upload any index CSV file (Nifty 100, 200, 500, etc.)
- CSV must contain a 'Symbol' column with stock symbols
- Default: Uses `ind_nifty100list.csv` automatically

✅ **Real-time Data**
- Fetches fresh data from Chartink API
- Data cached for 5 minutes (click Refresh to update)

✅ **Download Options**
- Download Gainers CSV
- Download Losers CSV
- Download Combined CSV

## Installation

1. Install Streamlit (if not already installed):
```bash
pip install streamlit
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## How to Run

### Option 1: Using Batch File (Windows)
Double-click `run_streamlit.bat`

### Option 2: Using Command Line
```bash
# Activate virtual environment
myvenv\Scripts\activate

# Run Streamlit
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

## CSV File Format

Your CSV file should have a 'Symbol' column (case-insensitive), like:

```csv
Company Name,Industry,Symbol,Series,ISIN Code
Reliance Industries Ltd.,Oil Gas & Consumable Fuels,RELIANCE,EQ,INE002A01018
Tata Consultancy Services Ltd.,Information Technology,TCS,EQ,INE467B01029
...
```

## Usage

1. **Default Mode**: 
   - Check "Use Default (Nifty 100)" in sidebar
   - Uses `ind_nifty100list.csv` automatically

2. **Custom Index**:
   - Uncheck "Use Default"
   - Upload your CSV file
   - App will filter stocks based on symbols in your CSV

3. **Refresh Data**:
   - Click "🔄 Refresh Data" button to get latest results

4. **Download**:
   - Use download buttons below each table to save CSV files

## Notes

- Data is fetched from Chartink's API
- Results are filtered to stocks in your uploaded/index CSV
- Tables are sorted by percentage change
- Gainers: Best to Worst
- Losers: Highest to Lowest (like Chartink)


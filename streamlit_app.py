import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Nifty Stock Screener - Gainers & Losers",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
api_url = "https://chartink.com/screener/process"
gainers_url = "https://chartink.com/screener/copy-open-high-5911"
losers_url = "https://chartink.com/screener/copy-open-low-103152"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stocks(screener_url, condition_type="high"):
    """Fetch stocks from Chartink API"""
    try:
        with requests.session() as s:
            # Get CSRF token
            r_data = s.get(screener_url)
            soup = bs(r_data.content, "lxml")
            meta = soup.find("meta", {"name": "csrf-token"})["content"]
            
            # Determine scan clause
            if condition_type == "high":
                condition = {"scan_clause": "( latest open = latest high )"}
            else:  # low
                condition = {"scan_clause": "( latest open = latest low )"}
            
            # Fetch data
            header = {"x-csrf-token": meta}
            response = s.post(api_url, headers=header, data=condition, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    return pd.DataFrame(data["data"])
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def load_stock_symbols_from_csv(csv_file, is_file_path=False):
    """Load stock symbols from CSV file"""
    try:
        if csv_file is not None:
            # If it's a file path (string), read from file
            if is_file_path:
                df = pd.read_csv(csv_file)
            else:
                # It's an uploaded file object
                df = pd.read_csv(csv_file)
            
            # Try to find Symbol column (case insensitive)
            symbol_col = None
            for col in df.columns:
                if 'symbol' in col.lower():
                    symbol_col = col
                    break
            
            if symbol_col is None:
                st.error("CSV file must contain a 'Symbol' column")
                return []
            
            # Extract and normalize symbols
            symbols = df[symbol_col].str.strip().str.upper().str.replace('-', '').tolist()
            symbols_original = df[symbol_col].str.strip().str.upper().tolist()
            symbols = list(set(symbols + symbols_original))
            symbols = [s for s in symbols if s and str(s) != 'NAN' and not pd.isna(s)]
            
            # Add ICICIPRULI if missing (common in Nifty 100)
            if 'ICICIPRULI' not in symbols:
                symbols.append('ICICIPRULI')
            
            return symbols
        return []
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return []

def filter_and_sort_stocks(stock_list, symbols, condition_type="gainers"):
    """Filter to index stocks and sort by percentage change"""
    if stock_list.empty:
        return stock_list
    
    # Find percentage change column
    pct_col = None
    for col in stock_list.columns:
        col_lower = str(col).lower()
        if 'chg' in col_lower or 'change' in col_lower or 'pct' in col_lower or '%' in col_lower:
            pct_col = col
            break
    
    # Filter to index stocks
    if 'nsecode' in stock_list.columns and symbols:
        filtered_stocks = stock_list[stock_list['nsecode'].isin(symbols)]
        stock_list = filtered_stocks
    
    # Sort by percentage change
    if pct_col:
        stock_list = stock_list.copy()
        stock_list[pct_col] = pd.to_numeric(stock_list[pct_col], errors='coerce')
        # Sort descending (best first for gainers, highest first for losers)
        stock_list = stock_list.sort_values(pct_col, ascending=False, na_position='last')
    
    return stock_list

# Main App
st.markdown('<h1 class="main-header">📈 Nifty Stock Screener - Gainers & Losers</h1>', unsafe_allow_html=True)

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Index Selection")
    st.markdown("---")
    
    # Default CSV option
    use_default = st.checkbox("Use Default (Nifty 100)", value=True)
    
    if use_default:
        default_csv = "ind_nifty100list.csv"
        if os.path.exists(default_csv):
            symbols = load_stock_symbols_from_csv(default_csv, is_file_path=True)
            index_name = "Nifty 100"
            st.success(f"✅ Using default: {index_name}")
            st.info(f"📊 {len(symbols)} stocks loaded")
        else:
            st.error("Default CSV file not found!")
            symbols = []
            index_name = "Unknown"
    else:
        uploaded_file = st.file_uploader(
            "Upload Index CSV File",
            type=['csv'],
            help="Upload a CSV file with 'Symbol' column containing stock symbols (like ind_nifty100list.csv)"
        )
        
        if uploaded_file is not None:
            symbols = load_stock_symbols_from_csv(uploaded_file, is_file_path=False)
            index_name = uploaded_file.name.replace('.csv', '').replace('ind_', '').replace('_', ' ').title()
            if symbols:
                st.success(f"✅ Loaded: {index_name}")
                st.info(f"📊 {len(symbols)} stocks loaded")
        else:
            symbols = []
            index_name = "No Index Selected"
            st.warning("Please upload a CSV file or use default")
    
    st.markdown("---")
    st.markdown("### ℹ️ Instructions")
    st.markdown("""
    1. **Default Mode**: Uses Nifty 100 list automatically
    2. **Custom Index**: Upload your CSV file with 'Symbol' column
    3. CSV format should match: `ind_nifty100list.csv`
    4. Data refreshes every 5 minutes
    """)

# Main content area
if not symbols:
    st.warning("⚠️ Please select an index to view stocks")
    st.stop()

# Fetch data
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()

with st.spinner("Fetching data from Chartink..."):
    gainers_df = fetch_stocks(gainers_url, "high")
    losers_df = fetch_stocks(losers_url, "low")
    
    # Filter and sort
    gainers_df = filter_and_sort_stocks(gainers_df, symbols, "gainers")
    losers_df = filter_and_sort_stocks(losers_df, symbols, "losers")

# Display metrics
st.markdown("---")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric("Index", index_name)

with metric_col2:
    st.metric("Total Gainers", len(gainers_df))

with metric_col3:
    st.metric("Total Losers", len(losers_df))

with metric_col4:
    total = len(gainers_df) + len(losers_df)
    st.metric("Total Stocks", total)

# Display tables side by side
st.markdown("---")
st.markdown("### 📊 Stock Analysis")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🟢 Top Gainers (Open = High)")
    if not gainers_df.empty:
        # Select columns to display
        display_cols = ['nsecode', 'name', 'per_chg', 'close', 'volume']
        available_cols = [col for col in display_cols if col in gainers_df.columns]
        display_df = gainers_df[available_cols].copy()
        
        # Format percentage change
        if 'per_chg' in display_df.columns:
            display_df['per_chg'] = display_df['per_chg'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        # Format close price
        if 'close' in display_df.columns:
            display_df['close'] = display_df['close'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        
        # Format volume
        if 'volume' in display_df.columns:
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
        
        # Rename columns for better display
        display_df.columns = [col.upper().replace('_', ' ') for col in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download button
        csv_gainers = gainers_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Gainers CSV",
            data=csv_gainers,
            file_name=f"{index_name}_gainers_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No gainers found for this index")

with col2:
    st.markdown("#### 🔴 Top Losers (Open = Low)")
    if not losers_df.empty:
        # Select columns to display
        display_cols = ['nsecode', 'name', 'per_chg', 'close', 'volume']
        available_cols = [col for col in display_cols if col in losers_df.columns]
        display_df = losers_df[available_cols].copy()
        
        # Format percentage change
        if 'per_chg' in display_df.columns:
            display_df['per_chg'] = display_df['per_chg'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
        
        # Format close price
        if 'close' in display_df.columns:
            display_df['close'] = display_df['close'].apply(lambda x: f"{x:,.2f}" if pd.notna(x) else "N/A")
        
        # Format volume
        if 'volume' in display_df.columns:
            display_df['volume'] = display_df['volume'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else "N/A")
        
        # Rename columns for better display
        display_df.columns = [col.upper().replace('_', ' ') for col in display_df.columns]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Download button
        csv_losers = losers_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Losers CSV",
            data=csv_losers,
            file_name=f"{index_name}_losers_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No losers found for this index")

# Combined download
st.markdown("---")
if not gainers_df.empty or not losers_df.empty:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Create combined dataframe
        combined_data = []
        if not gainers_df.empty:
            gainers_copy = gainers_df.copy()
            gainers_copy['Type'] = 'Gainer'
            combined_data.append(gainers_copy)
        if not losers_df.empty:
            losers_copy = losers_df.copy()
            losers_copy['Type'] = 'Loser'
            combined_data.append(losers_copy)
        
        if combined_data:
            combined_df = pd.concat(combined_data, ignore_index=True)
            csv_combined = combined_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Combined Data (Gainers + Losers)",
                data=csv_combined,
                file_name=f"{index_name}_gainers_losers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📊 Data fetched from Chartink | Last updated: {}</p>
    <p>💡 Tip: Data is cached for 5 minutes. Click 'Refresh Data' to get latest results.</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import os
from datetime import datetime

# Page configuration - sidebar always expanded by default
st.set_page_config(
    page_title="Nifty Stock Screener - Gainers & Losers",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Nifty Stock Screener - Real-time gainers and losers from Chartink API"
    }
)

# Auto-refresh every 3 minutes (180 seconds) with countdown
st.markdown("""
    <meta http-equiv="refresh" content="180">
    <script>
    // Countdown timer for auto-refresh
    let timeLeft = 180; // 3 minutes in seconds
    function updateTimer() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        const timerElement = document.getElementById('refresh-timer');
        if (timerElement) {
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        timeLeft--;
        if (timeLeft < 0) {
            timeLeft = 180; // Reset
        }
    }
    setInterval(updateTimer, 1000);
    updateTimer(); // Initial call
    </script>
""", unsafe_allow_html=True)

# Professional Custom CSS
st.markdown("""
    <style>
    /* Main Header */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
        letter-spacing: -0.5px;
    }
    
    /* Hide Streamlit default elements - but keep header for hamburger menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Keep header visible for hamburger menu */
    
    /* Sidebar styling - Dark theme */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%) !important;
        color: #e0e0e0 !important;
    }
    
    /* Sidebar text colors */
    section[data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #ffffff !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        font-size: 0.85rem !important;
        color: #d0d0d0 !important;
    }
    
    /* Sidebar checkbox and input styling */
    section[data-testid="stSidebar"] .stCheckbox label {
        font-size: 0.8rem !important;
        color: #e0e0e0 !important;
    }
    
    section[data-testid="stSidebar"] .stFileUploader label {
        font-size: 0.8rem !important;
        color: #e0e0e0 !important;
    }
    
    /* Sidebar divider */
    section[data-testid="stSidebar"] hr {
        border-color: #444 !important;
    }
    
    /* Sidebar reopen button */
    .sidebar-toggle-btn {
        position: fixed;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 0.5rem;
        border-radius: 0 15px 15px 0;
        cursor: pointer;
        z-index: 998;
        box-shadow: 2px 0 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        font-size: 1.2rem;
    }
    
    .sidebar-toggle-btn:hover {
        padding-left: 0.8rem;
        box-shadow: 4px 0 12px rgba(0,0,0,0.3);
    }
    
    .sidebar-toggle-btn::after {
        content: "☰";
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #666;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Table headers */
    .stDataFrame thead th {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 14px 12px !important;
        text-align: center !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
    }
    
    /* Table rows */
    .stDataFrame tbody tr {
        border-bottom: 1px solid #e0e0e0;
        transition: all 0.2s ease;
    }
    
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #fafafa;
    }
    
    .stDataFrame tbody tr:hover {
        background-color: #e8f4f8 !important;
        transform: scale(1.01);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .stDataFrame tbody td {
        padding: 10px 12px !important;
        font-size: 0.9rem;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-success {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    
    /* Refresh indicator */
    .refresh-indicator {
        position: fixed;
        top: 10px;
        right: 10px;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
    }
    
    #refresh-timer {
        font-weight: 700;
        font-size: 1rem;
        color: #ffd700;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    /* Container padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Info boxes */
    .stInfo {
        border-left: 4px solid #667eea;
        background-color: #f0f4ff;
    }
    
    .stSuccess {
        border-left: 4px solid #28a745;
    }
    
    .stWarning {
        border-left: 4px solid #ffc107;
    }
    
    .stError {
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# API endpoint
api_url = "https://chartink.com/screener/process"
gainers_url = "https://chartink.com/screener/copy-open-high-5911"
losers_url = "https://chartink.com/screener/copy-open-low-103152"

@st.cache_data(ttl=180)  # Cache for 3 minutes (auto-refresh)
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

# Auto-refresh indicator with countdown
refresh_time = datetime.now().strftime("%H:%M:%S")
st.markdown(f"""
    <div class="refresh-indicator">
        🔄 Auto-refresh in: <span id="refresh-timer">3:00</span> | Last: {refresh_time}
    </div>
""", unsafe_allow_html=True)


# Sidebar for file upload with improved styling
with st.sidebar:
    # Header with icon - Dark theme
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 0.8rem; 
                    border-radius: 8px; 
                    margin-bottom: 1rem;
                    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);'>
            <h2 style='color: white; margin: 0; font-size: 1rem; font-weight: 700; text-align: center;'>
                📁 Index Selection
            </h2>
            <p style='color: rgba(255,255,255,0.9); margin: 0.3rem 0 0 0; text-align: center; font-size: 0.7rem;'>
                Choose your stock index
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Default CSV option with better styling - Dark theme
    st.markdown("### 🎯 Selection Mode")
    st.markdown("<style>div[data-testid='stMarkdownContainer'] h3 {font-size: 0.85rem !important;}</style>", unsafe_allow_html=True)
    use_default = st.checkbox("✅ Use Default (Nifty 100)", value=True, key="use_default_checkbox")
    
    if use_default:
        default_csv = "ind_nifty100list.csv"
        if os.path.exists(default_csv):
            symbols = load_stock_symbols_from_csv(default_csv, is_file_path=True)
            index_name = "Nifty 100"
            st.markdown(f"""
                <div style='background: rgba(40, 167, 69, 0.15); 
                            border-left: 4px solid #28a745; 
                            padding: 0.7rem; 
                            border-radius: 5px; 
                            margin: 0.8rem 0;'>
                    <p style='margin: 0; color: #4ade80; font-weight: 600; font-size: 0.8rem;'>✅ Active: {index_name}</p>
                    <p style='margin: 0.3rem 0 0 0; color: #86efac; font-size: 0.75rem;'>📊 {len(symbols)} stocks loaded</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Default CSV file not found!")
            symbols = []
            index_name = "Unknown"
    else:
        st.markdown("### 📤 Upload Custom Index")
        st.markdown("<style>div[data-testid='stMarkdownContainer'] h3 {font-size: 0.85rem !important;}</style>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose CSV File",
            type=['csv'],
            help="Upload a CSV file with 'Symbol' column containing stock symbols (like ind_nifty100list.csv)",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            symbols = load_stock_symbols_from_csv(uploaded_file, is_file_path=False)
            index_name = uploaded_file.name.replace('.csv', '').replace('ind_', '').replace('_', ' ').title()
            if symbols:
                st.markdown(f"""
                    <div style='background: rgba(12, 84, 96, 0.2); 
                                border-left: 4px solid #0ea5e9; 
                                padding: 0.7rem; 
                                border-radius: 5px; 
                                margin: 0.8rem 0;'>
                        <p style='margin: 0; color: #38bdf8; font-weight: 600; font-size: 0.8rem;'>✅ Loaded: {index_name}</p>
                        <p style='margin: 0.3rem 0 0 0; color: #7dd3fc; font-size: 0.75rem;'>📊 {len(symbols)} stocks loaded</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            symbols = []
            index_name = "No Index Selected"
            st.markdown("""
                <div style='background: rgba(255, 193, 7, 0.15); 
                            border-left: 4px solid #fbbf24; 
                            padding: 0.7rem; 
                            border-radius: 5px; 
                            margin: 0.8rem 0;'>
                    <p style='margin: 0; color: #fbbf24; font-weight: 600; font-size: 0.8rem;'>⚠️ Please upload a CSV file</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick stats section - Dark theme
    st.markdown("### 📊 Quick Info")
    st.markdown("""
        <div style='background: rgba(102, 126, 234, 0.1); 
                    padding: 0.7rem; 
                    border-radius: 8px; 
                    margin: 0.8rem 0;
                    border: 1px solid rgba(102, 126, 234, 0.3);
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);'>
            <p style='margin: 0.4rem 0; color: #a5b4fc; font-weight: 600; font-size: 0.75rem;'>🔄 Auto-refresh: Every 3 min</p>
            <p style='margin: 0.4rem 0; color: #a5b4fc; font-weight: 600; font-size: 0.75rem;'>📈 Data Source: Chartink API</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ℹ️ Instructions")
    st.markdown("""
        <div style='background: rgba(102, 126, 234, 0.08); 
                    padding: 0.8rem; 
                    border-radius: 8px; 
                    border-left: 4px solid #667eea;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <ul style='color: #c0c0c0; line-height: 1.6; margin: 0; padding-left: 1rem; font-size: 0.75rem;'>
                <li><strong style='color: #e0e0e0;'>Default Mode</strong>: Uses Nifty 100 automatically</li>
                <li><strong style='color: #e0e0e0;'>Custom Index</strong>: Upload CSV with 'Symbol' column</li>
                <li>CSV format: <code style='background: rgba(102, 126, 234, 0.2); color: #a5b4fc; padding: 2px 6px; border-radius: 3px; font-size: 0.7rem;'>ind_nifty100list.csv</code></li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar reopen hint - Dark theme
    st.markdown("""
        <div style='background: rgba(102, 126, 234, 0.1); 
                    padding: 0.6rem; 
                    border-radius: 8px; 
                    border: 1px dashed #667eea;
                    text-align: center;
                    margin-top: 1rem;'>
            <p style='margin: 0; color: #a5b4fc; font-size: 0.7rem; font-weight: 600;'>
                💡 Tip: Click ☰ menu to reopen sidebar
            </p>
        </div>
    """, unsafe_allow_html=True)

# Main content area - Sidebar is accessible via Streamlit's native hamburger menu (☰) in top-left

if not symbols:
    st.warning("⚠️ Please select an index to view stocks")
    st.stop()

# Fetch data section with refresh button
st.markdown("---")
refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 2, 1])

with refresh_col2:
    refresh_clicked = st.button("🔄 Refresh Data Now", type="primary", width='stretch')
    if refresh_clicked:
        st.cache_data.clear()
        st.success("✅ Data refreshed! Reloading...")
        st.rerun()

with st.spinner("Fetching data from Chartink..."):
    gainers_df = fetch_stocks(gainers_url, "high")
    losers_df = fetch_stocks(losers_url, "low")
    
    # Filter and sort
    gainers_df = filter_and_sort_stocks(gainers_df, symbols, "gainers")
    losers_df = filter_and_sort_stocks(losers_df, symbols, "losers")

# Display metrics with professional styling
st.markdown("---")
st.markdown("### 📊 Summary Statistics")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(
        label="📈 Index",
        value=index_name,
        delta=None
    )

with metric_col2:
    st.metric(
        label="🟢 Total Gainers",
        value=len(gainers_df),
        delta=None
    )

with metric_col3:
    st.metric(
        label="🔴 Total Losers",
        value=len(losers_df),
        delta=None
    )

with metric_col4:
    total = len(gainers_df) + len(losers_df)
    st.metric(
        label="📊 Total Stocks",
        value=total,
        delta=None
    )

# Display tables side by side
st.markdown("---")
st.markdown('<div class="section-header">📊 Stock Analysis</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🟢 Top Gainers (Open = High)</div>', unsafe_allow_html=True)
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
        
        # Display with better formatting
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            height=450
        )
        
        # Download button
        csv_gainers = gainers_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Gainers CSV",
            data=csv_gainers,
            file_name=f"{index_name}_gainers_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            width='stretch'
        )
    else:
        st.info("No gainers found for this index")

with col2:
    st.markdown('<div class="section-header">🔴 Top Losers (Open = Low)</div>', unsafe_allow_html=True)
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
        
        # Display with better formatting
        st.dataframe(
            display_df,
            width='stretch',
            hide_index=True,
            height=450
        )
        
        # Download button
        csv_losers = losers_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Losers CSV",
            data=csv_losers,
            file_name=f"{index_name}_losers_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            width='stretch'
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
                width='stretch'
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 8px; margin-top: 2rem;'>
    <p style='font-size: 1.1rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;'>📊 Data Source: Chartink API</p>
    <p style='color: #666; margin: 0.25rem 0;'>🕐 Last updated: {}</p>
    <p style='color: #666; margin: 0.25rem 0;'>🔄 Auto-refresh: Every 3 minutes</p>
    <p style='color: #667eea; font-weight: 600; margin-top: 1rem;'>💡 Tip: Click 'Refresh Data' button for immediate update</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


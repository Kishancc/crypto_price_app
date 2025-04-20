import streamlit as st
from datetime import datetime
from utils import format_large_number, format_percent, get_percent_color
import pandas as pd

def render_sidebar():
    """Render the sidebar with logo and about information"""
    with st.sidebar:
        # Logo and title
        st.image("https://raw.githubusercontent.com/plotly/dash-sample-apps/main/apps/dash-financial-report/assets/stock-icon.png", width=80)
        st.title("Crypto Dashboard")
        
        # Last updated time
        st.write(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.divider()
        
        # About section
        st.subheader("About")
        st.write("""
        This dashboard provides real-time cryptocurrency market data powered by CoinMarketCap API.
        
        Features:
        - Live market data for top 500 cryptocurrencies
        - Interactive charts and visualizations
        - Historical price data
        - Market performance metrics
        - Data export functionality
        """)
        
        st.divider()
        
        # Footer
        st.caption("© 2025 Crypto Dashboard")
        st.caption("Data provided by CoinMarketCap")

def render_header():
    """Render the main header with market overview"""
    st.title("📊 Cryptocurrency Market Dashboard")
    
    # Get current date and time
    current_time = datetime.now().strftime("%B %d, %Y %H:%M:%S")
    st.subheader(f"Market Overview | {current_time}")
    
    # Add description
    st.markdown("""
    This dashboard displays real-time cryptocurrency market data from CoinMarketCap API. 
    Select cryptocurrencies from the dropdown to compare their performance metrics and view detailed charts.
    """)

def render_metrics(df):
    """
    Render key metrics for selected cryptocurrencies
    
    Args:
        df (pandas.DataFrame): DataFrame with selected cryptocurrency data
    """
    st.subheader("Selected Cryptocurrency Metrics")
    
    # Create metrics in a grid
    cols = st.columns(len(df))
    
    for i, (_, row) in enumerate(df.iterrows()):
        with cols[i]:
            # Icon and name
            col1, col2 = st.columns([1, 3])
            with col1:
                # Use the 'image' field from the DataFrame if available, else fallback to get_coin_icon
                if 'image' in row and row['image']:
                    st.image(row['image'], width=40)
                else:
                    from utils import get_coin_icon
                    st.image(get_coin_icon(row['symbol']), width=40)
            with col2:
                st.markdown(f"### {row['name']} ({row['symbol']})")
            
            # Price
            st.metric(
                "Price (USD)", 
                f"${row['price']:.4f}",
                delta=f"{row['percent_change_24h']:.2f}%" if row['percent_change_24h'] else None
            )
            
            # Market Cap
            st.metric(
                "Market Cap", 
                format_large_number(row['market_cap'])
            )
            
            # 24h Volume
            st.metric(
                "24h Volume", 
                format_large_number(row['volume_24h'])
            )
            
            # Percent changes
            st.markdown("**Percent Changes**")
            
            # Create a mini-table for percent changes
            percent_data = {
                "Period": ["1h", "24h", "7d", "30d"],
                "Change": [
                    row['percent_change_1h'],
                    row['percent_change_24h'],
                    row['percent_change_7d'],
                    row['percent_change_30d']
                ]
            }
            
            percent_df = pd.DataFrame(percent_data)
            
            # Apply color formatting
            def color_percent(val):
                if pd.isna(val):
                    return 'color: gray'
                    
                color = get_percent_color(val)
                return f'color: {color}'
            
            # Display styled dataframe
            st.dataframe(
                percent_df.style.format({
                    'Change': '{:.2f}%'
                }).applymap(color_percent, subset=['Change']),
                hide_index=True,
                height=150
            )

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json

from api import fetch_latest_listings, fetch_historical_data
from charts import (
    create_price_chart, 
    create_market_cap_chart, 
    create_gainers_losers_chart,
    create_market_share_chart
)
from data_processing import (
    prepare_listings_data, 
    prepare_historical_data,
    get_top_gainers_losers,
    calculate_market_share
)
from utils import format_large_number, format_percent, download_csv
from ui_components import render_sidebar, render_header, render_metrics

# Page configuration
st.set_page_config(
    page_title="Crypto Market Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Render sidebar
render_sidebar()

# Render header
render_header()

# Main container
main_container = st.container()

with main_container:
    try:
        # Fetch and prepare data
        with st.spinner("Fetching latest cryptocurrency data..."):
            crypto_data = fetch_latest_listings()
            
            if crypto_data:
                df = prepare_listings_data(crypto_data)
                
                # Store the data in session state for reuse
                st.session_state['crypto_data'] = df
                
                # Get list of all cryptocurrencies for selection
                all_cryptos = df['name'].tolist()
                
                # Default selections
                default_selections = ['Bitcoin', 'Ethereum', 'Solana', 'Ripple', 'Cardano']
                default_selections = [coin for coin in default_selections if coin in all_cryptos]
                
                # Multi-select for cryptocurrencies
                selected_cryptos = st.multiselect(
                    "Select cryptocurrencies to compare:",
                    all_cryptos,
                    default=default_selections
                )
                
                if selected_cryptos:
                    # Filter dataframe for selected cryptocurrencies
                    selected_df = df[df['name'].isin(selected_cryptos)]
                    
                    # Render metrics
                    render_metrics(selected_df)
                    
                    # Create tabs for different visualizations
                    tab1, tab2, tab3 = st.tabs(["Market Overview", "Price Analysis", "Market Share"])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Top gainers and losers
                            gainers_df, losers_df = get_top_gainers_losers(df)
                            fig_gainers_losers = create_gainers_losers_chart(gainers_df, losers_df)
                            st.plotly_chart(fig_gainers_losers, use_container_width=True)
                        
                        with col2:
                            # Market cap comparison of selected coins
                            fig_market_cap = create_market_cap_chart(selected_df)
                            st.plotly_chart(fig_market_cap, use_container_width=True)
                    
                    with tab2:
                        # Historical price data
                        if len(selected_cryptos) > 0:
                            # Timeframe selection
                            timeframe = st.selectbox(
                                "Select timeframe:",
                                ["7d", "30d", "90d", "180d", "365d"],
                                index=1
                            )
                            
                            timeframe_days = int(timeframe.replace('d', ''))
                            start_date = (datetime.now() - timedelta(days=timeframe_days)).strftime('%Y-%m-%d')
                            
                            # Fetch historical data for the first selected cryptocurrency
                            selected_symbol = selected_df.iloc[0]['symbol']
                            
                            with st.spinner(f"Fetching historical data for {selected_symbol}..."):
                                historical_data = fetch_historical_data(selected_symbol, start_date)
                                
                                if historical_data:
                                    hist_df = prepare_historical_data(historical_data)
                                    
                                    # Create price chart
                                    fig_price = create_price_chart(hist_df, selected_symbol, timeframe)
                                    st.plotly_chart(fig_price, use_container_width=True)
                                else:
                                    st.error("Failed to fetch historical data. Please try again later.")
                    
                    with tab3:
                        # Market share visualization
                        market_share_data = calculate_market_share(df)
                        fig_market_share = create_market_share_chart(market_share_data)
                        st.plotly_chart(fig_market_share, use_container_width=True)
                    
                    # Download data option
                    st.subheader("Download Data")
                    if st.button("Download Selected Cryptocurrency Data"):
                        csv_data = download_csv(selected_df)
                        st.download_button(
                            label="Click to Download CSV",
                            data=csv_data,
                            file_name=f"crypto_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("Please select at least one cryptocurrency to view data.")
            else:
                st.error("Failed to fetch cryptocurrency data. Please check your API key and try again.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.warning("Please check your internet connection and try refreshing the page.")
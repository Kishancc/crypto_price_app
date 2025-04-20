import pandas as pd
import streamlit as st
import io

def format_large_number(num, precision=2):
    """
    Format large numbers with K, M, B, T suffixes
    
    Args:
        num (float): Number to format
        precision (int): Decimal precision
        
    Returns:
        str: Formatted number string
    """
    if num is None:
        return "N/A"
        
    if num == 0:
        return "0"
        
    suffixes = ["", "K", "M", "B", "T"]
    magnitude = 0
    
    while abs(num) >= 1000 and magnitude < len(suffixes) - 1:
        magnitude += 1
        num /= 1000.0
        
    return f"${num:.{precision}f}{suffixes[magnitude]}"

def format_percent(percent, include_sign=True):
    """
    Format percentage values
    
    Args:
        percent (float): Percentage value
        include_sign (bool): Whether to include + sign for positive values
        
    Returns:
        str: Formatted percentage string
    """
    if percent is None:
        return "N/A"
        
    sign = "+" if percent > 0 and include_sign else ""
    return f"{sign}{percent:.2f}%"

def get_percent_color(percent):
    """
    Return color code based on percentage value
    
    Args:
        percent (float): Percentage value
        
    Returns:
        str: Color code
    """
    if percent is None:
        return "gray"
        
    if percent > 0:
        return "#10B981"  # Green for positive
    elif percent < 0:
        return "#EF4444"  # Red for negative
    else:
        return "#94A3B8"  # Neutral for zero

def download_csv(df):
    """
    Convert DataFrame to CSV for download
    
    Args:
        df (pandas.DataFrame): Data to convert
        
    Returns:
        str: CSV data as string
    """
    # Create a copy of the dataframe with formatted columns for better readability
    download_df = df.copy()
    
    # Format price and market cap columns
    download_df['formatted_price'] = download_df['price'].apply(lambda x: f"${x:.4f}")
    download_df['formatted_market_cap'] = download_df['market_cap'].apply(lambda x: f"${x:,.0f}")
    download_df['formatted_volume'] = download_df['volume_24h'].apply(lambda x: f"${x:,.0f}")
    
    # Format percentage columns
    for col in ['percent_change_1h', 'percent_change_24h', 'percent_change_7d', 'percent_change_30d']:
        download_df[f'formatted_{col}'] = download_df[col].apply(lambda x: f"{x:.2f}%")
    
    # Create a buffer
    csv_buffer = io.StringIO()
    
    # Write DataFrame to CSV
    download_df.to_csv(csv_buffer, index=False)
    
    # Get CSV data as string
    csv_data = csv_buffer.getvalue()
    
    return csv_data

def get_coin_icon(symbol, size=32):
    """
    Get cryptocurrency icon URL from CoinIcons
    
    Args:
        symbol (str): Cryptocurrency symbol
        size (int): Icon size in pixels
        
    Returns:
        str: Icon URL
    """
    return f"https://s2.coinmarketcap.com/static/img/coins/{size}x{size}/{symbol.lower()}.png"
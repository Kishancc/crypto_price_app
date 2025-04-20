import pandas as pd
import numpy as np
from datetime import datetime

def prepare_listings_data(api_data):
    """
    Process the API response and extract relevant cryptocurrency data
    
    Args:
        api_data (dict): Response from CoinMarketCap API
        
    Returns:
        pandas.DataFrame: Processed cryptocurrency data
    """
    crypto_list = []
    
    for coin in api_data['data']:
        crypto_list.append({
            'id': coin['id'],
            'name': coin['name'],
            'symbol': coin['symbol'],
            'slug': coin['slug'],
            'cmc_rank': coin['cmc_rank'],
            'price': coin['quote']['USD']['price'],
            'market_cap': coin['quote']['USD']['market_cap'],
            'volume_24h': coin['quote']['USD']['volume_24h'],
            'percent_change_1h': coin['quote']['USD']['percent_change_1h'],
            'percent_change_24h': coin['quote']['USD']['percent_change_24h'],
            'percent_change_7d': coin['quote']['USD']['percent_change_7d'],
            'percent_change_30d': coin['quote']['USD'].get('percent_change_30d', 0),
            'last_updated': coin['quote']['USD']['last_updated']
        })
    
    df = pd.DataFrame(crypto_list)
    
    # Convert last_updated to datetime
    df['last_updated'] = pd.to_datetime(df['last_updated'])
    
    # Sort by market cap (descending)
    df = df.sort_values('market_cap', ascending=False).reset_index(drop=True)
    
    return df

def prepare_historical_data(api_data):
    """
    Process historical price data from API response
    
    Args:
        api_data (dict): Response from CoinMarketCap historical API
        
    Returns:
        pandas.DataFrame: Processed historical data
    """
    if not api_data or 'data' not in api_data:
        return pd.DataFrame()
    
    # Get the first (and only) symbol from the data
    symbol = list(api_data['data'].keys())[0]
    quotes = api_data['data'][symbol]['quotes']
    
    hist_data = []
    
    for timestamp, quote_data in quotes.items():
        hist_data.append({
            'timestamp': datetime.fromtimestamp(int(timestamp)),
            'price': quote_data['USD']['price'],
            'volume_24h': quote_data['USD']['volume_24h'],
            'market_cap': quote_data['USD']['market_cap']
        })
    
    df = pd.DataFrame(hist_data)
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    return df

def get_top_gainers_losers(df, n=5, timeframe='percent_change_24h'):
    """
    Get top n gainers and losers based on specified timeframe
    
    Args:
        df (pandas.DataFrame): Cryptocurrency data
        n (int): Number of top coins to return
        timeframe (str): Column name for the percent change to use
        
    Returns:
        tuple: (gainers_df, losers_df)
    """
    # Ensure we have at least n valid entries
    valid_df = df[df[timeframe].notna()].copy()
    
    if len(valid_df) < n*2:
        n = len(valid_df) // 2  # Adjust n if we don't have enough data
    
    # Get top gainers (highest percent change)
    gainers = valid_df.nlargest(n, timeframe)[['name', 'symbol', timeframe, 'price']]
    
    # Get top losers (lowest percent change)
    losers = valid_df.nsmallest(n, timeframe)[['name', 'symbol', timeframe, 'price']]
    
    return gainers, losers

def calculate_market_share(df):
    """
    Calculate market share of BTC, ETH, and altcoins
    
    Args:
        df (pandas.DataFrame): Cryptocurrency data
        
    Returns:
        dict: Market share data
    """
    total_market_cap = df['market_cap'].sum()
    
    # Get Bitcoin market cap
    btc_market_cap = df[df['symbol'] == 'BTC']['market_cap'].sum()
    
    # Get Ethereum market cap
    eth_market_cap = df[df['symbol'] == 'ETH']['market_cap'].sum()
    
    # Calculate altcoins market cap (everything else)
    altcoins_market_cap = total_market_cap - btc_market_cap - eth_market_cap
    
    # Return as percentages
    return {
        'Bitcoin': btc_market_cap / total_market_cap * 100,
        'Ethereum': eth_market_cap / total_market_cap * 100,
        'Altcoins': altcoins_market_cap / total_market_cap * 100
    }
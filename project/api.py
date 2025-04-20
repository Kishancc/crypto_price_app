import requests
import streamlit as st
import json
from datetime import datetime, timedelta
import time

# CoinGecko API base URL (free API, no API key required)
BASE_URL = "https://api.coingecko.com/api/v3"

# Cache for coin symbol to coin ID mapping
_coin_symbol_to_id_map = None

# Simple in-memory cache for API responses
_cache = {
    'latest_listings': {'data': None, 'timestamp': None},
    'historical_data': {}
}

CACHE_EXPIRATION_SECONDS = 60  # 1 minute cache expiration

def get_coin_symbol_to_id_map():
    global _coin_symbol_to_id_map
    if _coin_symbol_to_id_map is None:
        try:
            response = requests.get(f"{BASE_URL}/coins/list")
            if response.status_code == 200:
                coins = response.json()
                # Map symbols (uppercase) to coin IDs
                _coin_symbol_to_id_map = {coin['symbol'].upper(): coin['id'] for coin in coins}
            else:
                st.error(f"Failed to fetch coin list with status code: {response.status_code}")
                _coin_symbol_to_id_map = {}
        except Exception as e:
            st.error(f"Error fetching coin list: {e}")
            _coin_symbol_to_id_map = {}
    return _coin_symbol_to_id_map

def fetch_latest_listings(vs_currency='usd', per_page=100, page=1):
    """
    Fetch the latest cryptocurrency listings from CoinGecko API with caching
    
    Args:
        vs_currency (str): The target currency of market data (usd, eur, etc.)
        per_page (int): Number of results per page (max 250)
        page (int): Page number
        
    Returns:
        dict: JSON response from the API or None if request failed
    """
    now = time.time()
    cache_entry = _cache['latest_listings']
    if cache_entry['data'] is not None and cache_entry['timestamp'] is not None:
        if now - cache_entry['timestamp'] < CACHE_EXPIRATION_SECONDS:
            return cache_entry['data']
    
    url = f"{BASE_URL}/coins/markets"
    
    parameters = {
        'vs_currency': vs_currency,
        'order': 'market_cap_desc',
        'per_page': per_page,
        'page': page,
        'sparkline': 'false',
        'price_change_percentage': '1h,24h,7d,30d'
    }
    
    try:
        response = requests.get(url, params=parameters)
        
        if response.status_code == 200:
            coins = response.json()
            # Transform to expected structure with 'data' key and nested 'quote' with 'USD'
            data = []
            for coin in coins:
                coin_dict = {
                    'id': coin.get('id'),
                    'name': coin.get('name'),
                    'symbol': coin.get('symbol').upper() if coin.get('symbol') else None,
                    'slug': coin.get('id'),
                    'cmc_rank': coin.get('market_cap_rank'),
                    'image': coin.get('image'),
                    'quote': {
                        'USD': {
                            'price': coin.get('current_price'),
                            'market_cap': coin.get('market_cap'),
                            'volume_24h': coin.get('total_volume'),
                            'percent_change_1h': coin.get('price_change_percentage_1h_in_currency'),
                            'percent_change_24h': coin.get('price_change_percentage_24h_in_currency'),
                            'percent_change_7d': coin.get('price_change_percentage_7d_in_currency'),
                            'percent_change_30d': coin.get('price_change_percentage_30d_in_currency'),
                            'last_updated': coin.get('last_updated')
                        }
                    }
                }
                data.append(coin_dict)
            result = {'data': data}
            _cache['latest_listings']['data'] = result
            _cache['latest_listings']['timestamp'] = now
            return result
        else:
            st.error(f"API request failed with status code: {response.status_code}")
            st.error(f"Error message: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def fetch_historical_data(symbol, days=30):
    """
    Fetch historical price data for a specific cryptocurrency from CoinGecko with caching
    
    Args:
        symbol (str): Cryptocurrency symbol (e.g., 'BTC', 'ETH')
        days (int): Number of days to fetch historical data for (max 365)
        
    Returns:
        dict: JSON response from the API or None if request failed
    """
    symbol = symbol.upper()
    try:
        days = int(days)
    except ValueError:
        st.warning("Invalid value for days parameter. Defaulting to 30 days.")
        days = 30

    if days > 365:
        st.warning("Public API users are limited to querying historical data within the past 365 days. Limiting to 365 days.")
        days = 365

    cache_key = f"{symbol}_{days}"
    now = time.time()
    cache_entry = _cache['historical_data'].get(cache_key)
    if cache_entry is not None:
        if now - cache_entry['timestamp'] < CACHE_EXPIRATION_SECONDS:
            return cache_entry['data']

    symbol_to_id = get_coin_symbol_to_id_map()
    coin_id = symbol_to_id.get(symbol)
    if not coin_id:
        st.error(f"Coin ID not found for symbol: {symbol}")
        return None
    
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    
    parameters = {
        'vs_currency': 'usd',
        'days': days,
        'interval': 'daily'
    }
    
    try:
        response = requests.get(url, params=parameters)
        
        if response.status_code == 200:
            data = response.json()
            # Transform to expected structure with 'data' key and nested 'quotes' dictionary
            quotes = {}
            prices = data.get('prices', [])
            volumes = data.get('total_volumes', [])
            market_caps = data.get('market_caps', [])
            
            for i in range(len(prices)):
                timestamp_ms = prices[i][0]
                timestamp = int(timestamp_ms / 1000)
                price = prices[i][1]
                volume = volumes[i][1] if i < len(volumes) else None
                market_cap = market_caps[i][1] if i < len(market_caps) else None
                
                quotes[timestamp] = {
                    'USD': {
                        'price': price,
                        'volume_24h': volume,
                        'market_cap': market_cap,
                        'timestamp': datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    }
                }
            
            result = {
                'data': {
                    symbol: {
                        'quotes': quotes
                    }
                },
                'status': {
                    'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    'error_code': 0,
                    'error_message': None,
                    'credit_count': 0
                }
            }
            _cache['historical_data'][cache_key] = {'data': result, 'timestamp': now}
            return result
        else:
            st.error(f"Historical data API request failed with status code: {response.status_code}")
            st.error(f"Error message: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Request error: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_coingecko_attribution():
    """
    Returns the required CoinGecko attribution text for display in the UI.
    """
    return (
        "Data provided by CoinGecko\n"
        "Price data by CoinGecko\n"
        "Source: CoinGecko\n"
        "Powered by CoinGecko API"
    )

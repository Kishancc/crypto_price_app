import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Color definitions
COLORS = {
    'primary': '#3B82F6',
    'secondary': '#64748B',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#94A3B8',
    'background': '#0F172A',
    'card': '#1E293B',
    'text': '#F1F5F9',
    'bitcoin': '#F7931A',
    'ethereum': '#627EEA',
    'altcoins': '#8A2BE2'
}

# Theme settings for all charts
CHART_THEME = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {
        'color': COLORS['text'],
        'family': 'Inter, sans-serif'
    },
    'margin': {'t': 40, 'b': 40, 'l': 40, 'r': 40}
}

def create_price_chart(df, symbol, timeframe):
    """
    Create an interactive price chart with volume bars
    
    Args:
        df (pandas.DataFrame): Historical price data
        symbol (str): Cryptocurrency symbol
        timeframe (str): Selected timeframe
        
    Returns:
        plotly.graph_objects.Figure: Price chart
    """
    # Create subplots: 1 row, 1 column, shared x-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                       vertical_spacing=0.03, 
                       row_width=[0.2, 0.8])
    
    # Add price line
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['price'],
            mode='lines',
            name=f'{symbol} Price',
            line=dict(color=COLORS['primary'], width=2),
            hovertemplate='%{y:.2f} USD<br>%{x}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add volume bars
    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['volume_24h'],
            name='Volume',
            marker_color=COLORS['neutral'],
            opacity=0.5,
            hovertemplate='%{y:,.0f} USD<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Calculate price change for title
    first_price = df.iloc[0]['price'] if not df.empty else 0
    last_price = df.iloc[-1]['price'] if not df.empty else 0
    price_change = ((last_price - first_price) / first_price) * 100
    change_color = COLORS['success'] if price_change >= 0 else COLORS['danger']
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Price Chart ({timeframe}) | {price_change:.2f}%",
        height=600,
        showlegend=False,
        **CHART_THEME
    )
    
    # Update axes
    fig.update_yaxes(title_text="Price (USD)", row=1, col=1, showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="Volume (USD)", row=2, col=1, showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def create_market_cap_chart(df):
    """
    Create a bar chart comparing market caps of selected cryptocurrencies
    
    Args:
        df (pandas.DataFrame): Cryptocurrency data for selected coins
        
    Returns:
        plotly.graph_objects.Figure: Market cap comparison chart
    """
    # Sort by market cap (descending)
    df_sorted = df.sort_values('market_cap', ascending=True)
    
    # Create figure
    fig = go.Figure()
    
    # Add horizontal bars
    fig.add_trace(
        go.Bar(
            y=df_sorted['name'],
            x=df_sorted['market_cap'],
            orientation='h',
            marker_color=COLORS['primary'],
            text=[f"${x/1e9:.2f}B" for x in df_sorted['market_cap']],
            textposition='outside',
            hovertemplate='%{y}: $%{x:,.0f}<extra></extra>'
        )
    )
    
    # Update layout
    fig.update_layout(
        title="Market Capitalization Comparison",
        xaxis_title="Market Cap (USD)",
        height=max(300, len(df) * 50),  # Dynamic height based on number of coins
        **CHART_THEME
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def create_gainers_losers_chart(gainers_df, losers_df):
    """
    Create a dual bar chart showing top gainers and losers
    
    Args:
        gainers_df (pandas.DataFrame): Top gainers data
        losers_df (pandas.DataFrame): Top losers data
        
    Returns:
        plotly.graph_objects.Figure: Gainers and losers chart
    """
    # Create figure with two subplots side by side
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Top Gainers (24h)", "Top Losers (24h)"),
        horizontal_spacing=0.1
    )
    
    # Add top gainers bars
    fig.add_trace(
        go.Bar(
            x=gainers_df['symbol'],
            y=gainers_df['percent_change_24h'],
            marker_color=COLORS['success'],
            text=[f"{x:.1f}%" for x in gainers_df['percent_change_24h']],
            textposition='outside',
            hovertemplate='%{x}: %{y:.2f}%<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add top losers bars
    fig.add_trace(
        go.Bar(
            x=losers_df['symbol'],
            y=losers_df['percent_change_24h'],
            marker_color=COLORS['danger'],
            text=[f"{x:.1f}%" for x in losers_df['percent_change_24h']],
            textposition='outside',
            hovertemplate='%{x}: %{y:.2f}%<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="Market Movers (24h)",
        height=400,
        showlegend=False,
        **CHART_THEME
    )
    
    # Update y-axes
    fig.update_yaxes(title_text="% Change", row=1, col=1, showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    fig.update_yaxes(title_text="% Change", row=1, col=2, showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    
    return fig

def create_market_share_chart(market_share_data):
    """
    Create a pie chart showing market share distribution
    
    Args:
        market_share_data (dict): Market share percentages
        
    Returns:
        plotly.graph_objects.Figure: Market share pie chart
    """
    labels = list(market_share_data.keys())
    values = list(market_share_data.values())
    
    colors = [COLORS['bitcoin'], COLORS['ethereum'], COLORS['altcoins']]
    
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker_colors=colors,
                textinfo='label+percent',
                hoverinfo='label+percent+value',
                textfont_size=14,
                pull=[0.05, 0.05, 0]
            )
        ]
    )
    
    fig.update_layout(
        title="Market Share Distribution",
        annotations=[{
            'text': 'Market<br>Dominance',
            'x': 0.5, 'y': 0.5,
            'font_size': 20,
            'showarrow': False
        }],
        height=500,
        **CHART_THEME
    )
    
    return fig
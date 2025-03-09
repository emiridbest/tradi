import pandas as pd
import numpy as np
import yfinance as yf

def fetch_stock_data(symbol: str, timeframe: str) -> pd.DataFrame:
    """Fetch historical stock data with timeframe selection."""
    try:
        end_date = pd.Timestamp.now()
        timeframe_dict = {
            '1M': '30d',
            '3M': '90d',
            '6M': '180d',
            '1Y': '365d',
            '2Y': '730d',
            '5Y': '1825d'
        }
        
        # Handle cryptocurrency symbols
        if symbol.upper() in ['BTC', 'ETH', 'DOGE']:
            symbol = f"{symbol}-USD"
            
        data = yf.download(
            symbol,
            start=(end_date - pd.Timedelta(days=int(timeframe_dict[timeframe][:-1]))).strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )
        
        if data.empty:
            raise Exception(f"No data found for symbol {symbol}")
            
        return data
    except Exception as e:
        raise Exception(f"Error fetching data: {str(e)}")

def momentum_trading_strategy(data, short_window=5, long_window=20):
    """Generate trading signals based on moving average crossover strategy."""
    # Create a copy to avoid modifying original
    signals = pd.DataFrame(index=data.index)
    
    # Create price and moving average columns
    signals['price'] = data['Close']
    signals['short_mavg'] = data['Close'].rolling(window=short_window).mean()
    signals['long_mavg'] = data['Close'].rolling(window=long_window).mean()
    
    # Create signals
    signals['signal'] = 0.0
    signals['signal'][short_window:] = np.where(
        signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)
    
    # Generate positions
    signals['positions'] = signals['signal'].diff()
    
    return signals
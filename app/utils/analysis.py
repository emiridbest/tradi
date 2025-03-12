import pandas as pd
import os
import numpy as np
from app.utils.trading_strategy import momentum_trading_strategy
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def generate_chart_analysis(symbol: str, signals: pd.DataFrame) -> str:
    """Generate analysis of trading signals using OpenAI."""
    try:
        # Calculate metrics
        total_trades = len(signals[signals['positions'] != 0])
        buy_signals = len(signals[signals['positions'] == 1.0])
        sell_signals = len(signals[signals['positions'] == -1.0])
        price_change = ((signals['price'].iloc[-1] - signals['price'].iloc[0]) / 
                      signals['price'].iloc[0] * 100)

        prompt = f"""
        Analyze this trading data for {symbol}:
        - Total number of trades: {total_trades}
        - Buy signals: {buy_signals}
        - Sell signals: {sell_signals}
        - Price change: {price_change:.2f}%
        - Current price trend relative to moving averages: 
          Last price: {signals['price'].iloc[-1]:.2f}
          Short MA: {signals['short_mavg'].iloc[-1]:.2f}
          Long MA: {signals['long_mavg'].iloc[-1]:.2f}

        Provide a brief trading analysis and recommendation.
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a professional stock market analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not generate analysis: {str(e)}"

def save_results(signals: pd.DataFrame, short_window: int, long_window: int):
    """Save strategy results to CSV."""
    os.makedirs('results', exist_ok=True)
    csv_filename = f'results/trading_strategy_{short_window}_{long_window}.csv'
    signals.to_csv(csv_filename)
    return csv_filename

def apply_trading_strategies(data: pd.DataFrame) -> dict:
    """Apply different moving average pairs trading strategies."""
    ma_pairs = [(5, 20), (10, 50), (20, 100), (50, 200)]
    results = {}
    
    for short_window, long_window in ma_pairs:
        signals = momentum_trading_strategy(data, short_window, long_window)
        results[f'{short_window}_{long_window}'] = signals
        
        # Save results
        save_results(signals, short_window, long_window)
    
    return results
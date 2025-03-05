import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from momentum_trading_strategy import momentum_trading_strategy
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)
def generate_chart_analysis(symbol: str, signals: pd.DataFrame) -> str:
    """Generate analysis of trading signals using OpenAI."""
    try:
        # Calculate metrics (same as before)
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

def save_results(signals: pd.DataFrame, short_window: int, long_window: int):
    """Save strategy results to CSV."""
    os.makedirs('results', exist_ok=True)
    csv_filename = f'results/trading_strategy_{short_window}_{long_window}.csv'
    signals.to_csv(csv_filename)

def plot_strategy(signals: pd.DataFrame, symbol: str):
    """Plot trading strategy results."""
    plt.figure(figsize=(12, 6))
    
    # Plot price and moving averages
    plt.plot(signals['price'], label='Price', alpha=0.7)
    plt.plot(signals['short_mavg'], label='Short MA', alpha=0.7)
    plt.plot(signals['long_mavg'], label='Long MA', alpha=0.7)
    
    # Plot buy/sell signals
    plt.plot(signals.loc[signals.positions == 1.0].index, 
             signals.short_mavg[signals.positions == 1.0],
             '^', markersize=10, color='g', label='Buy Signal')
    plt.plot(signals.loc[signals.positions == -1.0].index,
             signals.short_mavg[signals.positions == -1.0],
             'v', markersize=10, color='r', label='Sell Signal')
    
    plt.title(f'{symbol} Trading Strategy')
    plt.legend(loc='best')
    return plt

def run_analysis(symbol: str, timeframe: str):
    """Main analysis function with timeframe parameter."""
    try:
        # Fetch data with timeframe
        data = fetch_stock_data(symbol, timeframe)
        
        # Apply strategies
        results = apply_trading_strategies(data)
        
        # Plot default strategy (5, 20)
        fig = plot_strategy(results['5_20'], symbol)
        return fig, results
        
    except Exception as e:
        raise Exception(f"Analysis failed: {str(e)}")

def main():
    st.title("Stock Trading Strategy Analysis")
    
    # Create two columns for input fields
    col1, col2 = st.columns(2)
    
    # Input for stock symbol
    with col1:
        symbol = st.text_input("Enter Stock Symbol (e.g., NVDA):", "NVDA")
    
    # Timeframe selector
    with col2:
        timeframe = st.selectbox(
            "Select Timeframe:",
            options=['1M', '3M', '6M', '1Y', '2Y', '5Y'],
            index=3  # Default to 1Y
        )
    
    if st.button("Analyze"):
        if not symbol.strip():
            st.error("Please enter a stock symbol")
            return
        
        try:
            with st.spinner("Analyzing..."):
                fig, results = run_analysis(symbol, timeframe)
                
                # Display chart
                st.pyplot(fig)
                
                # Display AI analysis
                st.subheader("AI Analysis")
                analysis = generate_chart_analysis(symbol, results['5_20'])
                st.write(analysis)
                
                # Display statistics
                st.subheader("Strategy Results")
                for key, signals in results.items():
                    short_window, long_window = key.split('_')
                    st.write(f"Moving Average Pair ({short_window}, {long_window}):")
                    st.write(f"Number of trades: {len(signals[signals['positions'] != 0])}")
                
        except Exception as e:
            st.error(str(e))
if __name__ == "__main__":
    main()
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from momentum_trading_strategy import momentum_trading_strategy

def main():
    # Fetch NVIDIA historical data
    nvidia = yf.download('NVDA', start='2024-01-01', end='2024-11-10')
    
    # Define pairs of moving averages
    ma_pairs = [(5, 20), (10, 50), (20, 100), (50, 200)]
    
    # Apply and process each moving average pair
    for short_window, long_window in ma_pairs:
        # Apply the trading strategy
        signals = momentum_trading_strategy(nvidia, short_window, long_window)
        
        # Save results, plot strategy, and compute returns
        csv_filename = f'results/nvidia_trading_strategy_{short_window}_{long_window}.csv'
        signals.to_csv(csv_filename)
        
        # Add plotting and return computation code here
    plt.figure(figsize=(10, 6))
    plt.plot(signals['price'], label='Price')
    plt.plot(signals['short_mavg'], label='5-day SMA')
    plt.plot(signals['long_mavg'], label='20-day SMA')
    plt.plot(signals.loc[signals.positions == 1.0].index, 
             signals.short_mavg[signals.positions == 1.0],
             '^', markersize=10, color='g', lw=0, label='buy')
    plt.plot(signals.loc[signals.positions == -1.0].index,
                signals.short_mavg[signals.positions == -1.0],
                'v', markersize=10, color='r', lw=0, label='sell')
    plt.title('NVIDIA Trading Strategy')
    plt.legend(loc='best')
    plt.show()
if __name__ == '__main__':
    main()
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

def plot_to_base64(signals, symbol):
    """Convert plot to base64 string for embedding in HTML."""
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
    
    # Convert plot to base64 string
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()  # Close to prevent memory leaks
    
    return img_str
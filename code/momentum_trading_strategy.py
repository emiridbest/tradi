import pandas as pd
import numpy as np

def calculate_moving_average(data, window):
    return data.rolling(window=window).mean()

def momentum_trading_strategy(data, short_window, long_window):
    signals = pd.DataFrame(index=data.index)
    signals['price'] = data['Close']
    signals['short_mavg'] = calculate_moving_average(signals['price'], short_window)
    signals['long_mavg'] = calculate_moving_average(signals['price'], long_window)
    
    signals.loc[signals.index[short_window:], 'signal'] = np.where(
        signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0
    )
    signals['positions'] = signals['signal'].diff()
    
    return signals
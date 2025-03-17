import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

def prepare_data(data, lookback=30):
    """Prepare data with technical indicators."""
    try:
        # Check if we have enough data
        if len(data) < lookback * 2:
            raise ValueError(f"Insufficient data points. Need at least {lookback * 2}, got {len(data)}")
            
        # Create feature DataFrame
        df = pd.DataFrame()
        df['Close'] = data['Close']
        df['Volume'] = data['Volume'] if 'Volume' in data.columns else 0
        
        # Add technical indicators
        # Moving averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Price momentum
        df['Price_Change'] = df['Close'].pct_change()
        df['Price_Change_5d'] = df['Close'].pct_change(5)
        
        # Volatility
        df['Volatility'] = df['Close'].rolling(window=20).std()
        
        # Target variable (future price)
        df['Target'] = df['Close'].shift(-1)  # Next day's price
        
        # Drop NaN values
        df = df.dropna()
        
        # Feature scaling
        features = df.drop('Target', axis=1)
        target = df['Target']
        
        scaler = MinMaxScaler()
        features_scaled = scaler.fit_transform(features)
        
        return features_scaled, target.values, scaler, features.columns
    except Exception as e:
        raise Exception(f"Data preparation failed: {str(e)}")

def train_sk_model(data):
    """Train RandomForest model for price prediction."""
    try:
        X, y, scaler, feature_names = prepare_data(data)
        
        # Time series split for validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        # Use RandomForest for more stable predictions
        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15, 
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        # Train on the last split
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
        
        model.fit(X_train, y_train)
        
        # Calculate scores
        train_score = r2_score(y_train, model.predict(X_train))
        test_score = r2_score(y_test, model.predict(X_test))
        
        # Get feature importance
        feature_importance = dict(zip(feature_names, model.feature_importances_))
        print("Feature importance:", feature_importance)
        
        return model, scaler, (train_score, test_score)
    except Exception as e:
        raise Exception(f"Model training failed: {str(e)}")

def make_sk_predictions(model, data, scaler):
    """Make price predictions for different time horizons."""
    try:
        # Get the most recent data point
        recent_data = data.iloc[-60:]
        
        # Prepare features
        features, _, _, _ = prepare_data(recent_data)
        
        # Use the most recent feature vector
        latest_features = features[-1:] 
        
        # Make base prediction
        base_prediction = model.predict(latest_features)[0]
        current_price = data['Close'].iloc[-1]
        
        # Apply some market wisdom
        predictions = {}
        
        # Short-term: more influenced by recent momentum
        predictions["1d"] = base_prediction
        
        # Medium-term: regression to the mean
        sma20 = data['Close'].rolling(20).mean().iloc[-1]
        predictions["7d"] = 0.7 * base_prediction + 0.3 * sma20
        
        # Longer-term: more weight to longer moving averages
        sma50 = data['Close'].rolling(50).mean().iloc[-1]
        predictions["30d"] = 0.5 * base_prediction + 0.3 * sma20 + 0.2 * sma50
        
        # Very long-term: even more regression to the mean
        if len(data) >= 200:
            sma200 = data['Close'].rolling(200).mean().iloc[-1]
            predictions["90d"] = 0.3 * base_prediction + 0.2 * sma20 + 0.2 * sma50 + 0.3 * sma200
        else:
            predictions["90d"] = 0.4 * base_prediction + 0.3 * sma20 + 0.3 * sma50
        
        return predictions
    except Exception as e:
        raise Exception(f"Prediction generation failed: {str(e)}")
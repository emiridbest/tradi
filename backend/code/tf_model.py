import numpy as np
import pandas as pd
import os as _os
_os.environ["TF2_BEHAVIOR"] = "1"
from tensorflow.python import tf2 as _tf2
_tf2.enable()
import tensorflow as tf
import matplotlib.pyplot as plt
from keras.src.models import  Model
from keras.src.layers import LSTM, Dense, Dropout, BatchNormalization, Bidirectional, Input
from keras.src.optimizers import Adam
from keras.src.callbacks import EarlyStopping, ReduceLROnPlateau



def prepare_data(data, lookback=30, forecast_horizon=1):
    """Prepare data with technical indicators and proper scaling."""
    try:
        # Add debug prints
        print(f"Data shape: {data.shape}")
        print(f"Columns: {data.columns.tolist()}")
        
        if len(data) < lookback * 2:
            raise ValueError(f"Insufficient data points. Need at least {lookback * 2}, got {len(data)}")
        
        # Handle possible MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            # Find Volume and Close columns
            volume_cols = [col for col in data.columns if 'Volume' in col]
            close_cols = [col for col in data.columns if 'Close' in col]
            
            # Create a new DataFrame with flattened column names
            flattened_data = pd.DataFrame()
            
            # Copy Close data
            if close_cols:
                flattened_data['Close'] = data[close_cols[0]]
            
            # Copy Volume data if available
            if volume_cols:
                flattened_data['Volume'] = data[volume_cols[0]]
                
            data = flattened_data
            print("Flattened MultiIndex columns to:", data.columns.tolist())
        
        
        # Select the features and target
        df = data.copy()
        
        # Scale the features using TensorFlow
        feature_data = df.values.astype('float32')
        
        # Calculate min and max for each feature for normalization
        data_min = np.min(feature_data, axis=0)
        data_max = np.max(feature_data, axis=0)
        
        # Avoid division by zero in normalization
        data_range = np.maximum(data_max - data_min, 1e-10)
        
        # Normalize data to [0, 1] range
        scaled_data = (feature_data - data_min) / data_range
        
        X, y = [], []
        
        # Create sequences for LSTM
        for i in range(lookback, len(scaled_data) - forecast_horizon + 1):
            X.append(scaled_data[i - lookback:i])
            future_idx = i + forecast_horizon - 1
            # Ensure future_idx is within bounds
            if future_idx < len(scaled_data):
                # The first column is Close price
                y.append(scaled_data[future_idx][0])
        
        # Create a custom scaler object to remember the scaling parameters
        scaler = {
            'min': data_min,
            'range': data_range
        }
        
        return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32), scaler
    except Exception as e:
        print(f"Error in prepare_data: {str(e)}")
        raise Exception(f"Data preparation failed: {str(e)}")

def tf_train_test_split(X, y, test_size=0.2):
    """Split data into train and test sets using TensorFlow."""
    # Calculate split index - ensure we maintain time order for time series data
    split_idx = int(len(X) * (1 - test_size))
    
    # Create TensorFlow tensors
    X_train = tf.convert_to_tensor(X[:split_idx], dtype=tf.float32)
    y_train = tf.convert_to_tensor(y[:split_idx], dtype=tf.float32)
    X_test = tf.convert_to_tensor(X[split_idx:], dtype=tf.float32)
    y_test = tf.convert_to_tensor(y[split_idx:], dtype=tf.float32)
    
    return X_train, X_test, y_train, y_test

def create_tf_datasets(X, y, test_size=0.2, batch_size=32):
    """Create TensorFlow datasets for training and validation."""
    # Split data
    X_train, X_test, y_train, y_test = tf_train_test_split(X, y, test_size)
    
    # Create TensorFlow datasets
    train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
    test_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test))
    
    # Batch and prefetch for performance
    train_dataset = train_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    test_dataset = test_dataset.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    
    return train_dataset, test_dataset, X_test, y_test

def train_tf_model(data):
    """Train LSTM model with multiple horizons."""
    try:
        results = {}
        horizons = [1, 7]  # Short and medium-term forecasts
        
        for horizon in horizons:
            print(f"Training model for {horizon}-day horizon...")
            
            X, y, scaler = prepare_data(data, lookback=30, forecast_horizon=horizon)
            
            # Ensure minimum data requirements
            min_samples = 100
            if len(X) < min_samples:
                raise ValueError(f"Insufficient samples for training. Need {min_samples}, got {len(X)}")
            
            # Use TensorFlow's data API for training/test split
            batch_size = min(32, len(X) // 10)
            train_dataset, test_dataset, X_test, y_test = create_tf_datasets(
                X, y, test_size=0.2, batch_size=batch_size
            )
            
            # Create and train model - USING MSE LOSS INSTEAD OF BINARY CROSS-ENTROPY
            model = create_model(input_shape=(X.shape[1], X.shape[2]), learning_rate=0.001) 
            
            # Callbacks for better training
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=20, restore_best_weights=True, mode='min'),  
                ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=10, min_lr=1e-6)
            ]
            
            # Train the model using TensorFlow datasets
            history = model.fit(
                train_dataset,
                validation_data=test_dataset,
                epochs=50,  # Increase epochs but rely on early stopping
                callbacks=callbacks,
                verbose=1   
            )
            
            # Evaluate model
            train_loss = history.history['loss'][-1]
            val_loss = history.history['val_loss'][-1]
            
            # Make predictions
            y_pred = model.predict(X_test, verbose=0)
            
            # PROPER DENORMALIZATION - assuming first column (index 0) is Close price
            # For target values
            original_y_test = y_test * scaler['range'][0] + scaler['min'][0]
            
            # For predicted values 
            original_y_pred = y_pred.flatten() * scaler['range'][0] + scaler['min'][0]
            
            # Calculate metrics on denormalized values
            # MSE on original scale
            test_mse = tf.reduce_mean(tf.square(original_y_test - original_y_pred)).numpy()
            
            # Proper R² calculation on original scale
            mean_y_test = tf.reduce_mean(original_y_test)
            ss_total = tf.reduce_sum(tf.square(original_y_test - mean_y_test)).numpy()
            ss_residual = tf.reduce_sum(tf.square(original_y_test - original_y_pred)).numpy()
            
            # Avoid division by zero
            if ss_total < 1e-10:
                test_r2 = 0.0
            else:
                test_r2 = 1 - (ss_residual / ss_total)
            
            # Store results
            results[horizon] = {
                'model': model,
                'scaler': scaler,
                'metrics': {
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                    'test_mse': test_mse,
                    'test_r2': test_r2
                }
            }
            
            print(f"Model for {horizon}-day horizon - R² score: {test_r2:.4f}, MSE: {test_mse:.6f}")
            
        return results
    except Exception as e:
        print(f"Error in train_model: {str(e)}")
        raise Exception(f"Model training failed: {str(e)}")

def create_model(input_shape, learning_rate=0.001):
    """Create an LSTM model for regression (price prediction)."""
    # Clear previous models from memory
    tf.keras.backend.clear_session()
    
    # Use Keras functional API to define the model
    inputs = Input(shape=input_shape)
    
    # Add BatchNormalization to stabilize input
    x = BatchNormalization()(inputs)
    
    # LSTM layers with more capacity
    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = Dropout(0.2)(x)
    
    # Dense layers
    x = Dense(16, activation='relu')(x)
    x = Dropout(0.1)(x)
    
    # Regression output - single neuron with no activation for price prediction
    outputs = Dense(1)(x)
    
    # Create the model
    model = Model(inputs=inputs, outputs=outputs)
    
    # Compile model with appropriate regression loss
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='mean_squared_error', 
        metrics=['mean_absolute_error'] 
    )    
    return model


def make_tf_predictions(results, data):
    """Make price predictions using trained models for different time horizons."""
    try:
        predictions = {}
        
        # Handle possible MultiIndex columns for Close
        if isinstance(data.columns, pd.MultiIndex):
            close_cols = [col for col in data.columns if 'Close' in col]
            if close_cols:
                current_price = data[close_cols[0]].iloc[-1]
            else:
                raise ValueError("No Close column found in MultiIndex")
        else:
            current_price = data['Close'].iloc[-1]
        
        # Use 1-day model for short term prediction
        if 1 in results:
            model_1day = results[1]['model']
            scaler_1day = results[1]['scaler']
            
            # Prepare data for 1-day prediction
            X_1day, _, _ = prepare_data(data.iloc[-100:], lookback=30, forecast_horizon=1)
            if len(X_1day) > 0:
                pred_1day = model_1day.predict(X_1day[-1:], verbose=0)[0][0]

                
                predictions["1d"] = pred_1day
        
        # Use 7-day model for medium term
        if 7 in results:
            model_7day = results[7]['model']
            scaler_7day = results[7]['scaler']
            
            # Prepare data for 7-day prediction
            X_7day, _, _ = prepare_data(data.iloc[-100:], lookback=30, forecast_horizon=7)
            if len(X_7day) > 0:
                pred_7day = model_7day.predict(X_7day[-1:], verbose=0)[0][0]
                
                predictions["7d"] = pred_7day
        
        if "1d" in predictions and "7d" in predictions:
            # 30-day prediction: extrapolate with some regression to mean
            trend_factor = (predictions["7d"] / predictions["1d"]) - 1 
            # Handle possible MultiIndex for SMA calculation
            if isinstance(data.columns, pd.MultiIndex):
                close_cols = [col for col in data.columns if 'Close' in col]
                if close_cols:
                    sma50 = data[close_cols[0]].rolling(50).mean().iloc[-1] if len(data) >= 50 else current_price
                    sma200 = data[close_cols[0]].rolling(200).mean().iloc[-1] if len(data) >= 200 else current_price
                else:
                    sma50 = current_price
                    sma200 = current_price
            else:
                sma50 = data['Close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else current_price
                sma200 = data['Close'].rolling(200).mean().iloc[-1] if len(data) >= 200 else current_price
            
            # Blend of extrapolation and regression to long-term mean
            predictions["30d"] = current_price * (1 + trend_factor * 4) * 0.7 + sma50 * 0.3
            
            # 90-day prediction: more weight to long-term mean
            predictions["90d"] = current_price * (1 + trend_factor * 12) * 0.3 + sma50 * 0.3 + sma200 * 0.4
        
        # Ensure we have all horizons
        for horizon in ["1d", "7d", "30d", "90d"]:
            if horizon not in predictions:
                # Fallback method if models aren't available
                if horizon == "1d":
                    predictions[horizon] = current_price
                elif horizon == "7d":
                    predictions[horizon] = current_price * 1.01 # 1% increase
                elif horizon == "30d":
                    predictions[horizon] = current_price * 1.03
                elif horizon == "90d":
                    predictions[horizon] = current_price * 1.05
        
        return predictions
    except Exception as e:
        print(f"Error in make_predictions: {str(e)}")
        raise Exception(f"Prediction generation failed: {str(e)}")

def plot_predictions(data, predictions):
    """Plot the historical data and predictions."""
    try:
        last_date = data.index[-1]
        
        # Handle possible MultiIndex columns for Close
        if isinstance(data.columns, pd.MultiIndex):
            close_cols = [col for col in data.columns if 'Close' in col]
            if close_cols:
                current_price = data[close_cols[0]].iloc[-1]
                historical_data = data[close_cols[0]].iloc[-90:]
            else:
                raise ValueError("No Close column found in MultiIndex")
        else:
            current_price = data['Close'].iloc[-1]
            historical_data = data['Close'].iloc[-90:]
        
        # Create future dates for predictions
        future_dates = pd.date_range(
            start=last_date, 
            periods=91,
            freq='D'
        )
        
        # Create prediction series
        future_values = []
        for i in range(91):
            if i == 0:
                future_values.append(current_price)
            elif i == 1:
                future_values.append(predictions["1d"])
            elif i == 7:
                future_values.append(predictions["7d"])
            elif i == 30:
                future_values.append(predictions["30d"])
            elif i == 90:
                future_values.append(predictions["90d"])
            else:
                future_values.append(None)
                
        future_df = pd.Series(future_values, index=future_dates)
        future_df = future_df.interpolate(method='linear')
        
        # Plot
        plt.figure(figsize=(12, 6))
        
        # Historical data
        plt.plot(data.index[-90:], historical_data, label='Historical Price', color='blue')
        
        # Predictions
        plt.plot(future_dates, future_df, label='Predicted Price', color='red', linestyle='--')
        plt.scatter(future_dates[1], predictions["1d"], color='darkred', s=50)
        plt.scatter(future_dates[7], predictions["7d"], color='darkred', s=50)
        plt.scatter(future_dates[30], predictions["30d"], color='darkred', s=50)
        plt.scatter(future_dates[90], predictions["90d"], color='darkred', s=50)
        
        # Annotations
        plt.annotate(f"1d: ${predictions['1d']:.2f}", (future_dates[1], predictions["1d"]), 
                    xytext=(10, -20), textcoords='offset points')
        plt.annotate(f"7d: ${predictions['7d']:.2f}", (future_dates[7], predictions["7d"]), 
                    xytext=(10, 15), textcoords='offset points')
        plt.annotate(f"30d: ${predictions['30d']:.2f}", (future_dates[30], predictions["30d"]), 
                    xytext=(10, -20), textcoords='offset points')
        plt.annotate(f"90d: ${predictions['90d']:.2f}", (future_dates[90], predictions["90d"]), 
                    xytext=(-70, 15), textcoords='offset points')
        
        plt.title('Price Prediction', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price ($)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        return plt.gcf()
    except Exception as e:
        print(f"Error in plot_predictions: {str(e)}")
        return None
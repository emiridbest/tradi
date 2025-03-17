class TFModel:
    def __init__(self, lookback=30, forecast_days=1, lstm_units=50, dropout=0.2):
        """Initialize TensorFlow LSTM model for time series prediction.
        
        Args:
            lookback: Number of previous time steps to use as input features
            forecast_days: Number of days to forecast
            lstm_units: Number of LSTM units in the model
            dropout: Dropout rate to prevent overfitting
        """
        from keras.models import Sequential
        from keras.layers import LSTM, Dense, Dropout
        from keras.callbacks import EarlyStopping
        
        self.lookback = lookback
        self.forecast_days = forecast_days
        self.model = Sequential([
            LSTM(lstm_units, return_sequences=True, input_shape=(lookback, 1)),
            Dropout(dropout),
            LSTM(lstm_units),
            Dropout(dropout),
            Dense(forecast_days)
        ])
        self.model.compile(optimizer='adam', loss='mse')
        self.scaler = None
        self.early_stopping = EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
    
    def _prepare_sequences(self, data):
        """Transform time series data into sequences for LSTM input"""
        X, y = [], []
        for i in range(len(data) - self.lookback - self.forecast_days + 1):
            X.append(data[i:i+self.lookback])
            y.append(data[i+self.lookback:i+self.lookback+self.forecast_days])
        return np.array(X), np.array(y)
    
    def train(self, data, epochs=100, batch_size=32, validation_split=0.2):
        """Train the LSTM model on closing price data.
        
        Args:
            data: DataFrame with 'Close' prices
            epochs: Number of training epochs
            batch_size: Training batch size
            validation_split: Fraction of data to use for validation
            
        Returns:
            Training history
        """
        from sklearn.preprocessing import MinMaxScaler
        
        # Normalize the data
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(data['Close'].values.reshape(-1, 1))
        
        # Create sequences
        X, y = self._prepare_sequences(scaled_data)
        
        # Reshape for LSTM [samples, time steps, features]
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        # Train-test split
        split = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split], X[split:]
        y_train, y_val = y[:split], y[split:]
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=[self.early_stopping],
            verbose=1
        )
        
        return history
    
    def predict(self, data):
        """Make predictions using the trained LSTM model.
        
        Args:
            data: DataFrame with recent price data
            
        Returns:
            Dictionary of price predictions for different time horizons
        """
        if self.scaler is None:
            raise ValueError("Model not trained yet. Call train() first.")
            
        # Scale the data
        scaled_data = self.scaler.transform(data['Close'].values.reshape(-1, 1))
        
        # Take the last lookback days for prediction
        last_sequence = scaled_data[-self.lookback:].reshape(1, self.lookback, 1)
        
        # Predict the next days
        scaled_prediction = self.model.predict(last_sequence)
        
        # Inverse transform to get actual prices
        prediction = self.scaler.inverse_transform(scaled_prediction)[0]
        
        # Create prediction dictionary for different horizons
        current_price = data['Close'].iloc[-1]
        predictions = {
            "1d": prediction[0],
            "7d": None,
            "30d": None,
            "90d": None
        }
        
        # For longer horizons, we could run sequential predictions
        # or implement a more sophisticated approach
        
        return predictions
    
    def evaluate(self, data):
        """Evaluate model performance on test data.
        
        Args:
            data: Test data with 'Close' prices
            
        Returns:
            Dictionary of evaluation metrics
        """
        from sklearn.metrics import mean_squared_error, mean_absolute_error
        import math
        
        # Scale data
        scaled_data = self.scaler.transform(data['Close'].values.reshape(-1, 1))
        
        # Prepare sequences
        X, y_true = self._prepare_sequences(scaled_data)
        X = X.reshape(X.shape[0], X.shape[1], 1)
        
        # Make predictions
        y_pred = self.model.predict(X)
        
        # Inverse transform
        y_true = self.scaler.inverse_transform(y_true.reshape(-1, self.forecast_days))
        y_pred = self.scaler.inverse_transform(y_pred)
        
        # Calculate metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = math.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        
        return {
            'mse': mse,
            'rmse': rmse,
            'mae': mae
        }
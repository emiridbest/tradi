import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math

class SKModel:
    def __init__(self, n_estimators=100, max_depth=10, random_state=42):
        """Initialize the sklearn RandomForest model for time series forecasting.
        
        Args:
            n_estimators: Number of trees in the forest
            max_depth: Maximum depth of each tree
            random_state: Random seed for reproducibility
        """
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1  # Use all available cores
        )
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns = None
        self.target_column = 'Close'
        self.trained = False
 
    def _create_features(self, data):
        """Create time series features from the data."""
        df = data.copy()
        
        # Fix DataFrame format issues (sometimes yfinance returns multi-level columns)
        if isinstance(df.columns, pd.MultiIndex):
            # If we have multi-level columns, flatten them
            print("Detected multi-level columns, flattening DataFrame")
            if ('Close', 'NVDA') in df.columns:
                close_col = df[('Close', 'NVDA')]
            else:
                for col in df.columns:
                    if 'Close' in col:
                        close_col = df[col]
                        break
            
            # Create a clean DataFrame with just the Close price
            df = pd.DataFrame({'Close': close_col})
            df.index = close_col.index
        
        # If 'Close' not in columns, try to find a suitable price column
        if self.target_column not in df.columns:
            print(f"'{self.target_column}' column not found, looking for alternatives")
            if 'Adj Close' in df.columns:
                print("Using 'Adj Close' as target column")
                df[self.target_column] = df['Adj Close']
            elif 'Price' in df.columns:
                print("Using 'Price' as target column")
                df[self.target_column] = df['Price']
            else:
                # If we can't find a suitable column, raise an error
                raise ValueError(f"Could not find {self.target_column} column or suitable alternative")
        
        print("DataFrame after preprocessing:")
        print(df)
        
        # Handle missing values in the target column
        df = df[df[self.target_column].notna()]
        
        # Price features (with safe handling of NaN and inf values)
        df['return_1d'] = df[self.target_column].pct_change(1)
        df['return_5d'] = df[self.target_column].pct_change(5)
        df['return_14d'] = df[self.target_column].pct_change(14)
        
        # Moving averages - ensure min_periods to avoid NaNs
        df['sma_5'] = df[self.target_column].rolling(window=5, min_periods=1).mean()
        df['sma_10'] = df[self.target_column].rolling(window=10, min_periods=1).mean()
        df['sma_20'] = df[self.target_column].rolling(window=20, min_periods=1).mean()
        df['sma_50'] = df[self.target_column].rolling(window=50, min_periods=1).mean()
        
        # Price relative to moving averages - replace div by zero with NaN
        df['price_sma5_ratio'] = df[self.target_column] / df['sma_5'].replace(0, np.nan)
        df['price_sma20_ratio'] = df[self.target_column] / df['sma_20'].replace(0, np.nan)
        
        # Volatility
        df['volatility_14d'] = df['return_1d'].rolling(window=14, min_periods=1).std()
        df['volatility_30d'] = df['return_1d'].rolling(window=30, min_periods=1).std()
        
        # Volume features
        if 'Volume' in df.columns:
            df['volume_change'] = df['Volume'].pct_change(1)
            df['volume_ma5'] = df['Volume'].rolling(window=5, min_periods=1).mean()
            df['volume_ma10'] = df['Volume'].rolling(window=10, min_periods=1).mean()
            # Avoid division by zero in volume ratio
            df['volume_ratio'] = df['Volume'] / df['volume_ma10'].replace(0, np.nan)
        
        # Target for next day prediction
        df['target_1d'] = df[self.target_column].shift(-1)
        df['target_7d'] = df[self.target_column].shift(-7)
        df['target_30d'] = df[self.target_column].shift(-30)
        
        # Drop NaN values
        df = df.dropna()
        
        # Replace any remaining infinities with NaNs and drop those rows
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        return df

    def train(self, data):
        """Train the RandomForest model on price data.
        
        Args:
            data: DataFrame with OHLCV price data
            
        Returns:
            Dictionary with training metrics
        """
        # Ensure we have the 'Close' column
        if self.target_column not in data.columns:
            raise ValueError(f"Data must contain '{self.target_column}' column")
        
        # Create features
        df = self._create_features(data)
        
        # Define features (all columns except targets)
        self.feature_columns = [col for col in df.columns 
                               if not col.startswith('target_') and col != 'Date']
        
        # Prepare training data for 1-day prediction
        X = df[self.feature_columns].values
        y = df['target_1d'].values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train-test split (time series split)
        train_size = int(len(X_scaled) * 0.8)
        X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        
        # Train model
        self.model.fit(X_train, y_train)
        self.trained = True
        
        # Calculate metrics
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = math.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Get feature importance
        importance = dict(zip(self.feature_columns, 
                              self.model.feature_importances_))
        sorted_importance = dict(sorted(importance.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True))
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'accuracy': self.model.score(X_test, y_test),
            'feature_importance': sorted_importance
        }
    
    def predict(self, data):
        """Make predictions using the trained RandomForest model with improved error handling."""
        if not self.trained:
            raise ValueError("Model not trained yet. Call train() first.")
            
        try:
            # Create features
            df = self._create_features(data)
            
            # Check if we have any data after preprocessing
            if len(df) == 0:
                raise ValueError("No valid data points after preprocessing")
            
            # Get the most recent data point
            recent_data = df.iloc[-1:][self.feature_columns].values
            
            # Check for inf/nan values
            if np.any(np.isnan(recent_data)) or np.any(np.isinf(recent_data)):
                print("Warning: Recent data contains NaN or infinite values")
                recent_data = np.nan_to_num(recent_data, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Scale the input
            try:
                recent_data_scaled = self.scaler.transform(recent_data)
            except Exception as e:
                # If transform fails, try fitting on this data first
                print(f"Scaler transform failed: {str(e)}. Attempting to refit...")
                recent_data_scaled = self.scaler.fit_transform(recent_data)
            
            # Make the 1-day prediction
            prediction_1d = self.model.predict(recent_data_scaled)[0]
            
            # For longer horizons, we'll use a more sophisticated approach
            # combining the model prediction with moving averages for longer-term
            current_price = df[self.target_column].iloc[-1]
            sma_5 = df['sma_5'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]
            
            # For 7-day prediction: weight recent price, model prediction, and moving averages
            prediction_7d = 0.4 * prediction_1d + 0.3 * current_price + 0.2 * sma_5 + 0.1 * sma_20
            
            # For 30-day prediction: give more weight to longer moving averages
            prediction_30d = 0.2 * prediction_1d + 0.1 * current_price + 0.3 * sma_20 + 0.4 * sma_50
            
            # For 90-day prediction: even more weight to longer moving averages
            # Use the 50-day SMA more heavily
            prediction_90d = 0.1 * prediction_1d + 0.1 * current_price + 0.2 * sma_20 + 0.6 * sma_50
            
            # For hourly data, adjust the predictions
            is_hourly = False
            if isinstance(df.index, pd.DatetimeIndex):
                # Check if the majority of intervals are around 1 hour
                time_diffs = pd.Series(df.index).diff().median()
                if pd.Timedelta('30 minutes') <= time_diffs <= pd.Timedelta('90 minutes'):
                    is_hourly = True
                    print("Detected hourly data, adjusting prediction labels")
            
            # Return predictions with appropriate labels based on data frequency
            if is_hourly:
                return {
                    "1h": prediction_1d,
                    "4h": prediction_7d,
                    "8h": prediction_30d,
                    "24h": prediction_90d
                }
            else:
                return {
                    "1d": prediction_1d,
                    "7d": prediction_7d,
                    "30d": prediction_30d,
                    "90d": prediction_90d
                }
        
        except Exception as e:
            print(f"Error during prediction: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return placeholder values based on last price
            try:
                last_price = data['Close'].iloc[-1] if 'Close' in data.columns else data.iloc[:, 0].iloc[-1]
                return {
                    "1d": last_price,
                    "7d": last_price,
                    "30d": last_price,
                    "90d": last_price,
                    "error": str(e)
                }
            except:
                return {
                    "1d": 0.0,
                    "7d": 0.0,
                    "30d": 0.0,
                    "90d": 0.0,
                    "error": str(e)
                }
            
    def evaluate(self, data):
        """Evaluate model performance on test data with better error handling."""
        if not self.trained:
            raise ValueError("Model not trained yet. Call train() first.")
            
        try:
            # Create features
            df = self._create_features(data)
            
            if len(df) < 5:  # Arbitrary minimum size
                print("Warning: Not enough data points after preprocessing for reliable evaluation")
                return {
                    'mse': float('nan'),
                    'rmse': float('nan'),
                    'mae': float('nan'),
                    'r2': float('nan')
                }
            
            # Prepare data
            X = df[self.feature_columns].values
            y_true = df['target_1d'].values
            
            # Check for remaining inf/nan values
            if np.any(np.isnan(X)) or np.any(np.isinf(X)):
                print("Warning: Data still contains NaN or infinite values after cleaning")
                # Replace any remaining problematic values
                X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            
            try:
                X_scaled = self.scaler.transform(X)
            except Exception as e:
                # If transform fails, try fitting on this data first
                print(f"Scaler transform failed: {str(e)}. Attempting to refit...")
                X_scaled = self.scaler.fit_transform(X)
            
            # Make predictions
            y_pred = self.model.predict(X_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_true, y_pred)
            rmse = math.sqrt(mse)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            accuracy = self.model.score(X_scaled, y_true)
            
            return {
                'mse': mse,
                'rmse': rmse,
                'mae': mae,
                'r2': r2,
                'accuracy': accuracy
            }
        
        except Exception as e:
            print(f"Error during model evaluation: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return placeholder values
            return {
                'mse': 0.0,
                'rmse': 0.0,
                'mae': 0.0,
                'r2': 0.0,
                'accuracy': 0.0,
                'error': str(e)
            }
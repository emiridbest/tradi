from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import traceback

# Import model from model_instance instead of app.config
from app.models.model_instance import sk_model, sk_model_trained
from app.utils.ai_utils import generate_chart_analysis
# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)

@api_bp.route('/train', methods=['POST'])
def train_model():
    """Train the ML model using provided data."""
    try:
        # Get training data from request
        data = request.get_json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data['price_history'])
        
        # Train the model
        global sk_model, sk_model_trained
        metrics = sk_model.train(df)
        sk_model_trained = True
        
        return jsonify({
            'status': 'success',
            'message': 'Model trained successfully',
            'metrics': {k: float(v) if isinstance(v, np.float64) else v 
                        for k, v in metrics.items() if k != 'feature_importance'}
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@api_bp.route('/predict', methods=['POST'])
def predict():
    """Make predictions using trained model."""
    try:
        global sk_model, sk_model_trained
        
        # Get input data
        data = request.get_json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data['price_history'])
        
        # Train model if not already trained (per chart)
        if not sk_model_trained:
            metrics = sk_model.train(df)
            sk_model_trained = True
        
        # Make prediction
        predictions = sk_model.predict(df)
        
        # Convert numpy values to Python native types
        predictions = {k: float(v) for k, v in predictions.items()}
        
        return jsonify({
            'status': 'success',
            'predictions': predictions,
            'current_price': float(df['Close'].iloc[-1])
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 500

            

@api_bp.route('/predict', methods=['POST'])
def reset_model_endpoint():
    """Reset the model to untrained state"""
    from app.models.model_instance import reset_model
    return jsonify(reset_model())
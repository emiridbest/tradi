from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import traceback

# Import models
from app.models.model_instance import sk_model, tf_model, sk_model_trained, tf_model_trained

# Create a Blueprint (don't use the same name as the file)
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/train', methods=['POST'])
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

@api_blueprint.route('/predict', methods=['POST'])
def predict():
    """Make predictions using trained model."""
    try:
        global sk_model, sk_model_trained
        if not sk_model_trained:
            return jsonify({
                'status': 'error',
                'message': 'Model not trained. Please train the model first.'
            }), 400
            
        # Get input data
        data = request.get_json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data['price_history'])
        
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
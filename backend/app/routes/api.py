from flask import Blueprint, jsonify, request
import pandas as pd
import numpy as np
import traceback
from flask_cors import cross_origin
import traceback
from datetime import datetime
# Import utility functions
from app.utils.trading_strategy import fetch_stock_data
from app.utils.trading_strategy import momentum_trading_strategy
# Import models
from app.models.model_instance import sk_model, sk_model_trained
from app.models.model_instance import reset_model
from app.utils.ai_utils import InjectiveChatAgent
from app.utils.json_utils import clean_for_json

# Import model from model_instance instead of app.config
from app.models.model_instance import sk_model, sk_model_trained
# Create a Blueprint for the API routes
api_bp = Blueprint('api', __name__)
# Initialize chat agent
agent = InjectiveChatAgent()



@api_bp.route("/ping", methods=["GET"])
@cross_origin()
def ping():
    """Health check endpoint"""
    return jsonify({
        "status": "ok", 
        "timestamp": datetime.now().isoformat(), 
        "version": "1.0.0"
    })

@api_bp.route("/stock-data", methods=["POST"])
@cross_origin()
def stock_data_endpoint():
    """Endpoint to fetch stock data and prepare it for the frontend chart"""
    try:
        if request.is_json:
            # Get data from JSON body
            data = request.get_json()
            symbol = data.get('symbol', 'NVDA')
            timeframe = data.get('timeframe', '1Y') 
            interval = data.get('interval', 'day')
        else: 
            symbol = request.args.get('symbol', 'NVDA')
            timeframe = request.args.get('timeframe', '1Y')
            interval = request.args.get('interval', 'day')
        print(f"Fetching stock data for {symbol} - {timeframe} - {interval}")
        
        # Fetch data using your existing functions
        data = fetch_stock_data(symbol, timeframe, interval)
        signals = momentum_trading_strategy(data)
        
        # Create response with the exact field names expected by frontend
        response = {
            'symbol': symbol,
            'timeframe': timeframe,
            'interval': interval,
            'price': data['Close'].tolist(),             # Changed from 'Close' to 'price'
            'dates': data.index.strftime('%Y-%m-%d').tolist(),  # Changed from 'Date' to 'dates', simplified format
            'short_mavg': signals['short_mavg'].tolist(),  # Changed from 'Short_mavg' to 'short_mavg'
            'long_mavg': signals['long_mavg'].tolist(),    # Changed from 'Long_mavg' to 'long_mavg'
            'positions': signals['positions'].tolist()     # Changed from 'Positions' to 'positions'
        }
        
        # Clean any NaN or non-JSON serializable values
        clean_for_json(response)
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch stock data'
        }), 500


@api_bp.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict_endpoint():
    """API endpoint for price predictions"""
    try:
        # Get parameters based on request method
        if request.method == "POST":
            if request.is_json:
                # Get data from JSON body
                data = request.get_json()
                symbol = data.get('symbol', 'NVDA')
                timeframe = data.get('timeframe', '1Y') 
                interval = data.get('interval', 'day')
                model_type = data.get('model', 'default')
            else:
                # Form data
                symbol = request.form.get('symbol', 'NVDA')
                timeframe = request.form.get('timeframe', '1Y')
                interval = request.form.get('interval', 'day')
                model_type = request.form.get('model', 'default')
        else:
            # GET request - get from query parameters
            symbol = request.args.get('symbol', 'NVDA')
            timeframe = request.args.get('timeframe', '1Y')
            interval = request.args.get('interval', 'day')
            model_type = request.args.get('model', 'default')
            
        print(f"Generating predictions for {symbol} ({timeframe}, {interval}) using model: {model_type}")

        # Fetch data
        data = fetch_stock_data(symbol, timeframe, interval)
        
        # Train model if not already trained
        global sk_model, sk_model_trained
        if not sk_model_trained:
            print("Training model on data shape:", data.shape)
            metrics = sk_model.train(data)
            sk_model_trained = True
        
        # Get performance metrics
        performance = sk_model.evaluate(data)
        
        # Make predictions
        predictions = sk_model.predict(data)
        current_price = float(data['Close'].iloc[-1])
        
        # Convert any NumPy types to Python native types for JSON serialization
        def convert_to_native_types(obj):
            if isinstance(obj, (np.integer, np.floating)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return [float(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: convert_to_native_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native_types(x) for x in obj]
            return obj
            
        clean_predictions = convert_to_native_types(predictions)
        clean_performance = convert_to_native_types(performance)
        
        print(f"Predictions complete: {clean_predictions}")
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'predictions': clean_predictions,
            'performance': clean_performance,
            'status': 'success'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate predictions',
            'status': 'error'
        }), 500

@api_bp.route("/reset-model", methods=["POST"])
@cross_origin()
def reset_model_endpoint():
    """Reset the model"""
    try:
        result = reset_model()
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to reset model'
        }), 500

@api_bp.route("/chart-analysis", methods=["POST"])
@cross_origin()
def chart_analysis_endpoint():
    """Endpoint to analyze chart data and initialize conversation"""
        
    try:
        if request.is_json:
            # Get data from JSON body
            data = request.get_json()
            symbol = data.get('symbol', 'NVDA')
            timeframe = data.get('timeframe', '1Y') 
            interval = data.get('interval', 'day')
        else: 
            symbol = request.args.get('symbol', 'NVDA')
            timeframe = request.args.get('timeframe', '1Y')
            interval = request.args.get('interval', 'day')
      
        if not data or "symbol" not in data:
            return jsonify({
                "error": "Missing symbol",
                "response": "Please provide a symbol for analysis."
            }), 400
        data = fetch_stock_data(symbol, timeframe, interval)

        # Convert signals to DataFrame properly
        signals = momentum_trading_strategy(data)
        session_id = data.get("session_id", f"analysis_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Check if signals DataFrame is empty
        if signals.empty:
            return jsonify({
                "error": "Empty data",
                "response": f"No valid data available for {symbol}."
            }), 400
            
        # Generate analysis
        analysis_result = agent.generate_chart_analysis(symbol, signals)
        
        return jsonify({
            "response": analysis_result,
            "session_id": session_id,
            "symbol": symbol
        })
        
    except Exception as e:
        print(f"Error in chart analysis: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "response": f"Error analyzing chart: {str(e)}"
        }), 500


@api_bp.route("/chat", methods=["POST"])
@cross_origin()
def chat_endpoint():
    """Main chat endpoint"""
    if not request.is_json:
        return jsonify({
            "error": "Invalid request format",
            "response": "Request must be in JSON format"
        }), 400
        
    data = request.get_json()
    try:
        if not data or "message" not in data:
            return jsonify({
                "error": "No message provided",
                "response": "Please provide a message to continue our conversation.",
                "session_id": data.get("session_id", "default"),
                "agent_id": data.get("agent_id", "default"),
                "agent_key": data.get("agent_key", "default"),
                "environment": data.get("environment", "testnet"),
            }), 400

        session_id = data.get("session_id", "default")
        private_key = data.get("agent_key", "default")
        agent_id = data.get("agent_id", "default")
        environment = data.get("environment", "testnet")
        
        # Create a separate thread to run the async function
        import threading
        response_container = [None]
        
        def run_async_chat():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_container[0] = loop.run_until_complete(
                agent.get_response(data["message"], session_id, private_key, agent_id, environment)
            )
            loop.close()
            
        thread = threading.Thread(target=run_async_chat)
        thread.start()
        thread.join()
        
        response = response_container[0]
        if response is None:
            return jsonify({
                "error": "Failed to get response",
                "response": "An error occurred while processing your request.",
                "session_id": session_id
            }), 500

        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "response": "I apologize, but I encountered an error. Please try again.",
            "session_id": data.get("session_id", "default"),
        }), 500

@api_bp.route("/history", methods=["GET"])
@cross_origin()
def history_endpoint():
    """Get chat history endpoint"""
    session_id = request.args.get("session_id", "default")
    return jsonify({
        "history": agent.get_history(session_id),
        "token_context": agent.get_token_context(session_id)
    })
    
@api_bp.route("/clear", methods=["POST"])
@cross_origin()
def clear_endpoint():
    """Clear chat history endpoint"""
    session_id = request.args.get("session_id", "default")
    agent.clear_history(session_id)
    return jsonify({"status": "success"})
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

@api_bp.errorhandler(Exception)
def handle_exception(e):
    """Handle exceptions in API routes"""
    return jsonify({
        "error": str(e),
        "traceback": traceback.format_exc()
    }), 500
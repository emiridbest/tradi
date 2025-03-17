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

@api_bp.route("/stock-data", methods=["GET"])
@cross_origin()
def stock_data_endpoint():
    """Endpoint to fetch stock data and prepare it for the frontend chart"""
    try:
        symbol = request.args.get('symbol', 'NVDA')
        timeframe = request.args.get('timeframe', '1Y')
        interval = request.args.get('interval', 'day')
        
        # Fetch data using your existing functions
        data = fetch_stock_data(symbol, timeframe, interval)
        signals = momentum_trading_strategy(data)
        
        # Format the signal data for the frontend chart
        formatted_signals = []
        for index, row in signals.iterrows():
            formatted_signals.append({
                'date': index.strftime('%Y-%m-%d'),
                'price': float(row['price']),
                'short_mavg': float(row['short_mavg']),
                'long_mavg': float(row['long_mavg']),
                'positions': int(row['positions'])
            })
        
        response = {
            'symbol': symbol,
            'timeframe': timeframe,
            'signals': formatted_signals,
            'stats': {
                'trade_count': len(signals[signals['positions'] != 0]),
                'buy_signals': len(signals[signals['positions'] == 1.0]),
                'sell_signals': len(signals[signals['positions'] == -1.0]),
                'price_change': float(((signals['price'].iloc[-1] - signals['price'].iloc[0]) / 
                               signals['price'].iloc[0] * 100))
            },
            'last_price': float(signals['price'].iloc[-1])
        }
        
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to fetch stock data'
        }), 500

@api_bp.route("/predict", methods=["GET"])
@cross_origin()
def predict_endpoint():
    """API endpoint for price predictions"""
    try:
        symbol = request.args.get('symbol', 'NVDA')
        timeframe = request.args.get('timeframe', '1Y')
        interval = request.args.get('interval', 'day')
        
        # Fetch data
        data = fetch_stock_data(symbol, timeframe, interval)
        
        # Train model if not already trained
        global sk_model, sk_model_trained
        if not sk_model_trained:
            metrics = sk_model.train(data)
            sk_model_trained = True
        
        # Get performance metrics
        performance = sk_model.evaluate(data)
        
        # Make predictions
        predictions = sk_model.predict(data)
        current_price = float(data['Close'].iloc[-1])
        
        return jsonify({
            'symbol': symbol,
            'current_price': current_price,
            'predictions': predictions,
            'performance': performance
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate predictions'
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
    if not request.is_json:
        return jsonify({
            "error": "Invalid request format",
            "response": "Request must be in JSON format"
        }), 400
        
    data = request.get_json()
    try:
        if not data or "symbol" not in data or "signals" not in data:
            return jsonify({
                "error": "Missing required data",
                "response": "Please provide a symbol and signals data."
            }), 400

        symbol = data["symbol"]
        signals = pd.DataFrame(data["signals"])
        session_id = data.get("session_id", f"analysis_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Create a separate thread to run the async function
        import threading
        
        def run_async_analysis():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(agent.analyze_chart(symbol, signals, session_id))
            loop.close()
            return result
            
        thread = threading.Thread(target=run_async_analysis)
        thread.start()
        thread.join()
        
        # Generate analysis directly for Flask synchronous context
        analysis_result = agent.generate_chart_analysis(symbol, signals)
        
        # Add to token context
        agent.add_token_context(session_id, symbol, analysis_result)
        
        result = {
            "response": analysis_result,
            "session_id": session_id,
            "symbol": symbol
        }
        
        if "error" in result:
            return jsonify(result), 400
            
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "response": "I apologize, but I encountered an error analyzing the chart data."
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

        
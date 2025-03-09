from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pandas as pd
import traceback

# Import utility functions
from app.utils.trading_strategy import fetch_stock_data
from app.utils.chart_utils import plot_strategy, save_figure_to_base64
from app.utils.analysis import generate_chart_analysis, apply_trading_strategies

# Import models
from app.models.model_instance import sk_model, tf_model, sk_model_trained, tf_model_trained

# Create a Blueprint (don't use the same name as the file)
views_blueprint = Blueprint('views', __name__)

@views_blueprint.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@views_blueprint.route('/analyze', methods=['GET', 'POST'])
def analyze():
    """Page for stock analysis."""
    if request.method == 'POST':
        # Get form data
        symbol = request.form.get('symbol', 'NVDA')
        timeframe = request.form.get('timeframe', '1Y')
        
        if not symbol:
            flash('Please enter a stock symbol')
            return redirect(url_for('views.analyze'))
        
        try:
            # Fetch data
            data = fetch_stock_data(symbol, timeframe)
            
            # Apply trading strategies
            results = apply_trading_strategies(data)
            
            # Generate chart for default strategy (5, 20)
            fig = plot_strategy(results['5_20'], symbol)
            chart_img = save_figure_to_base64(fig)
            
            # Generate AI analysis
            analysis = generate_chart_analysis(symbol, results['5_20'])
            
            # Store results in session
            session['symbol'] = symbol
            session['timeframe'] = timeframe
            session['last_price'] = float(results['5_20']['price'].iloc[-1])
            
            # Prepare strategy statistics
            stats = {}
            for key, signals in results.items():
                short_window, long_window = key.split('_')
                stats[key] = {
                    'short_window': short_window,
                    'long_window': long_window,
                    'trade_count': len(signals[signals['positions'] != 0]),
                    'buy_signals': len(signals[signals['positions'] == 1.0]),
                    'sell_signals': len(signals[signals['positions'] == -1.0])
                }
            
            return render_template(
                'analysis_result.html',
                symbol=symbol,
                timeframe=timeframe,
                chart_img=chart_img,
                analysis=analysis,
                stats=stats,
                last_price=session['last_price']
            )
            
        except Exception as e:
            flash(f'Error: {str(e)}')
            traceback.print_exc()
            return redirect(url_for('views_blueprint.analyze'))
    
    # For GET requests
    symbol = request.args.get('symbol', 'NVDA')
    timeframe = request.args.get('timeframe', '1Y')
    timeframes = ['1M', '3M', '6M', '1Y', '2Y', '5Y']
    
    return render_template('analyze.html', symbol=symbol, timeframe=timeframe, timeframes=timeframes)

@views_blueprint.route('/predict', methods=['GET'])
def predict():
    """Page for price predictions."""
    if 'symbol' not in session or 'timeframe' not in session:
        flash('Please analyze a stock first')
        return redirect(url_for('views_blueprint.analyze'))
    
    symbol = session['symbol']
    timeframe = session['timeframe']
    last_price = session.get('last_price', 0)
    
    try:
        # Get data
        data = fetch_stock_data(symbol, timeframe)
        
        # Make predictions using the trained models
        global sk_model, tf_model, sk_model_trained, tf_model_trained
        
        if not sk_model_trained:
            # Train model if not already trained
            metrics = sk_model.train(data)
            sk_model_trained = True
            flash('SK model trained successfully!')
        
        if not tf_model_trained:
            # Train TF model if not already trained
            metrics = tf_model.train(data)
            tf_model_trained = True
            flash('TF model trained successfully!')
        
        # Get predictions
        sk_predictions = sk_model.predict(data)
        tf_predictions = tf_model.predict(data)
        
        return render_template(
            'predictions.html',
            symbol=symbol,
            timeframe=timeframe,
            sk_predictions=sk_predictions,
            tf_predictions=tf_predictions,
            last_price=last_price
        )
        
    except Exception as e:
        flash(f'Error: {str(e)}')
        traceback.print_exc()
        return redirect(url_for('views_blueprint.analyze'))

@views_blueprint.route('/about')
def about():
    """About page."""
    return render_template('about.html')
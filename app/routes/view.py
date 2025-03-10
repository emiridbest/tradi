from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import pandas as pd
import traceback

# Import utility functions
from app.utils.trading_strategy import fetch_stock_data
from app.utils.chart_utils import plot_to_base64
from app.utils.trading_strategy import momentum_trading_strategy
# Import models
from app.models.model_instance import sk_model, sk_model_trained

# Define the blueprint with the correct name
views_bp = Blueprint('views_bp', __name__)

@views_bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@views_bp.route('/analyze', methods=['GET', 'POST'])
@views_bp.route('/analyse/', methods=['GET', 'POST'])
def analyze():
    """Page for stock analysis."""
    if request.method == 'POST':
        # Get form data
        symbol = request.form.get('symbol', 'NVDA')
        timeframe = request.form.get('timeframe', '1Y')
        
        if not symbol:
            flash('Please enter a stock symbol')
            return redirect(url_for('views_bp.analyze'))
        
        try:
            # Fetch data
            data = fetch_stock_data(symbol, timeframe)
            
            signals = momentum_trading_strategy(data)
        
            chart_img = plot_to_base64(signals, symbol)
            
            if chart_img is None:
                flash("Failed to generate chart. Please try again.")
                return redirect(url_for('views_bp.analyze'))
            
            # Prepare strategy statistics
            stats = {
                'trade_count': len(signals[signals['positions'] != 0]),
                'buy_signals': len(signals[signals['positions'] == 1.0]),
                'sell_signals': len(signals[signals['positions'] == -1.0]),
                'price_change': ((signals['price'].iloc[-1] - signals['price'].iloc[0]) / 
                               signals['price'].iloc[0] * 100)
            }
            
            # Generate analysis using OpenAI
            try:
                from app.utils.ai_utils import generate_chart_analysis
                analysis = generate_chart_analysis(symbol, signals)
            except Exception as ai_error:
                print(f"AI analysis error: {str(ai_error)}")
                analysis = f"Analysis for {symbol}: The stock shows {stats['buy_signals']} buy signals and {stats['sell_signals']} sell signals over the selected timeframe."
            
            # Store results in session
            session['symbol'] = symbol
            session['timeframe'] = timeframe
            session['last_price'] = float(signals['price'].iloc[-1])
            session['chart_img'] = chart_img
            session['stats'] = stats  
            session['analysis'] = analysis
            
            return render_template(
                'analysis_result.html',
                symbol=symbol,
                timeframe=timeframe,
                chart_img=chart_img,
                analysis=analysis,
                stats=stats,
                last_price=float(signals['price'].iloc[-1])
            )
            
        except Exception as e:
            flash(f'Error: {str(e)}')
            import traceback
            traceback.print_exc()
            return redirect(url_for('views_bp.analyze'))
    
    # For GET requests
    symbol = request.args.get('symbol', 'NVDA')
    timeframe = request.args.get('timeframe', '1Y')
    timeframes = ['1M', '3M', '6M', '1Y', '2Y', '5Y']
    
    return render_template('analyze.html', symbol=symbol, timeframe=timeframe, timeframes=timeframes)

@views_bp.route('/analysis_result', methods=['GET'])
def analysis_result():
    """Page for displaying analysis results."""
    symbol = session.get('symbol', 'NVDA')
    timeframe = session.get('timeframe', '1Y')
    last_price = session.get('last_price', 0.0)
    chart_img = session.get('chart_img', None)
    stats = session.get('stats', None)
    analysis = session.get('analysis', None)
    
    return render_template('analysis_result.html', 
                          symbol=symbol, 
                          timeframe=timeframe, 
                          last_price=last_price,
                          chart_img=chart_img,
                          stats=stats,
                          analysis=analysis)

@views_bp.route('/predict', methods=['GET', 'POST'])
@views_bp.route('/predict')  
def predict():
    """Page for price predictions."""
    if request.method == 'POST':
        symbol = request.form.get('symbol', 'NVDA')
        timeframe = request.form.get('timeframe', '1Y')
        
        try:
            # Fetch data
            data = fetch_stock_data(symbol, timeframe)
            
            # Train model if not already trained
            global sk_model, sk_model_trained
            if not sk_model_trained:
                metrics = sk_model.train(data)
                sk_model_trained = True
                flash('Model trained successfully!')
            
            # Get performance metrics
            performance = sk_model.evaluate(data)
            
            # Make predictions
            predictions = sk_model.predict(data)
            current_price = float(data['Close'].iloc[-1])
            
            # Store for display
            session['predictions'] = {k: float(v) for k, v in predictions.items()}
            session['price'] = current_price
            session['performance'] = performance  # Store metrics in session
            
            return render_template('predictions.html',
                                  symbol=symbol,
                                  predictions=session['predictions'],
                                  current_price=current_price,
                                  performance=performance)  # Pass metrics to template
                                  
        except Exception as e:
            flash(f'Error: {str(e)}')
            traceback.print_exc()
            return redirect(url_for('views_bp.predict'))
    
    # For GET requests
    symbol = request.args.get('symbol', session.get('symbol', 'NVDA'))
    timeframes = ['1M', '3M', '6M', '1Y', '2Y', '5Y']
    
    # Get any stored predictions
    predictions = session.get('predictions', {})
    current_price = session.get('price', 0.0)
    performance = session.get('performance', None)
    
    return render_template('predict.html',
                          symbol=symbol,
                          timeframes=timeframes,
                          predictions=predictions,
                          current_price=current_price,
                          performance=performance)  # Pass metrics here too
@views_bp.route('/about', methods=['GET', 'POST'])
def about():
    """About page."""
    return render_template('about.html')
from flask import Flask

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_for_testing')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
    
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    
    # Initialize OpenAI
    from openai import OpenAI
    app.config["OPENAI_CLIENT"] = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )
    
    # Initialize models
    from models.sk_models import SKModel
    app.config["SK_MODEL"] = SKModel()
    app.config["MODEL_TRAINED"] = False
    
    # Register blueprints
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    from routes.api import views_bp
    app.register_blueprint(views_bp)
    
    # Register utility functions with app
    from utils.trading_strategy import generate_chart_analysis, apply_trading_strategies
    app.generate_chart_analysis = generate_chart_analysis
    app.apply_trading_strategies = apply_trading_strategies
    
    # Health check route
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "model_trained": app.config["MODEL_TRAINED"]}
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return app.render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return app.render_template('500.html'), 500
    
    return app
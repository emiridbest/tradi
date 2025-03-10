from flask import Flask, render_template

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

    # Register blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/routes/api')
    
    from app.routes.view import views_bp
    app.register_blueprint(views_bp)
    
    # Register utility functions with app
    from app.utils.analysis import generate_chart_analysis, apply_trading_strategies
    app.generate_chart_analysis = generate_chart_analysis
    app.apply_trading_strategies = apply_trading_strategies
    
    # Health check route
    @app.route('/health')
    def health_check():
        from app.models.model_instance import get_model_status
        return {"status": "healthy", "model": get_model_status()}
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    print("Registering blueprints...")

    

    return app
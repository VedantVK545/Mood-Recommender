"""
Main Flask application for the Mood-Based Recommendation System.

This is the entry point for the web application.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from config import Config
from database import init_db, seed_initial_data
from routes.recommendation import recommendation_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    """
    Application factory function.
    
    Creates and configures the Flask application instance.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Enable CORS for API endpoints
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize database
    with app.app_context():
        try:
            init_db()
            seed_initial_data()
            logger.info("Database initialized and seeded successfully")
        except Exception as e:
            logger.error(f"[ERR] Database initialization failed: {e}")
    
    # Register blueprints
    app.register_blueprint(recommendation_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        """Handle 404 errors."""
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors."""
        logger.error(f"Server error: {e}")
        return {'error': 'Internal server error'}, 500
    
    # Health check endpoint
    @app.route('/health')
    def health():
        """Simple health check."""
        return {'status': 'healthy'}, 200
    
    logger.info("Flask application created successfully")
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Development server
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        threaded=True
    )

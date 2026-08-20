"""Flask API application for Voyage Analytics."""

from flask import Flask
from logging.config import dictConfig

from api.routes import register_routes


def create_app() -> Flask:
    """
    Create and configure the Flask application.

    Returns:
        Configured Flask application instance.
    """
    # Configure logging
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_exceptions_handler",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }
    )

    app = Flask(__name__)

    # Load configuration
    app.config["JSON_SORT_KEYS"] = False

    # Register routes
    register_routes(app)

    return app


# Create app instance for WSGI
app = create_app()


if __name__ == "__main__":
    from config.settings import settings

    app.run(
        host=settings.api_host,
        port=settings.api_port,
        debug=False,
    )

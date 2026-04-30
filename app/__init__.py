import os
from flask import Flask
from flask_session import Session
from app.config import Config, ProductionConfig


def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), "static"),
        static_url_path="/static",
        template_folder="templates",
    )

    if os.environ.get("FLASK_ENV") == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(Config)
        Session(app)   # filesystem sessions only in dev

    from app.blueprints.auth      import auth_bp
    from app.blueprints.journal   import journal_bp
    from app.blueprints.insights  import insights_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(insights_bp)

    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        from app.services.scheduler import start_scheduler
        start_scheduler()

    return app
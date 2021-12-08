from flask import Flask


def create_app():
    app = Flask(__name__)
    app.app_context().push()

    from .config import conf

    app.config.from_object(conf)

    from .routes import routes_bp

    app.register_blueprint(routes_bp)

    return app

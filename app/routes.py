# app/routes.py
from .controllers.auth_controller import auth_bp
from .controllers.user_controller import user_bp
from .controllers.management_controller import management_bp

def init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(management_bp)

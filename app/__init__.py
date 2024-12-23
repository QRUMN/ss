from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from config import config

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from app.routes import auth, events, admin, members, creator
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(members.bp)
    app.register_blueprint(creator.bp)

    # User loader for Flask-Login
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    return app

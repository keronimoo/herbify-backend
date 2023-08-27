from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login.login_manager import LoginManager #added 


db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'thisismysecretkeydonotstealit'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

    app.config['UPLOAD_FOLDER'] = 'static'
  

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .classification import classification as classification_blueprint
    app.register_blueprint(classification_blueprint)

    return app

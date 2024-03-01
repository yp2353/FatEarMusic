from flask import Flask
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET KEY'] = 'hellotankyou'
    app.secret_key = 'hellotankyou'

    from .views import views
    from .auth import auth, User, login_manager

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # check
    #login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    return app
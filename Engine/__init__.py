from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask import Flask

load_dotenv()  

login_manager = LoginManager()
login_manager.login_view = 'user.login'

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)

    app.config.from_prefixed_env()

    app.config['SESSION_TYPE'] = "filesystem"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    login_manager.init_app(app)
    db.init_app(app)

    from Engine.user.views import user
    from Engine.rate.views import rating
    from Engine.index.views import index
    from Engine.comment.views import comment
    from Engine.profile.views import profile
    from Engine.errors.handlers import errors
    from Engine.recommender.views import recommender

    app.register_blueprint(user)
    app.register_blueprint(index)
    app.register_blueprint(rating)
    app.register_blueprint(errors)
    app.register_blueprint(comment)
    app.register_blueprint(profile)
    app.register_blueprint(recommender)

    return app

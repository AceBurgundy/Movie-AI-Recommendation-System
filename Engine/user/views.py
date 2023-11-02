from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from Engine.api_response import RouteResponse, RouteResponseType
from flask_login import current_user, login_user, logout_user
from Engine.user.forms import RegisterForm, LoginForm
from sqlalchemy.exc import SQLAlchemyError
from Engine.csv_alchemy import CsvAlchemy
from Engine.models import User

# Create a blueprint for user routes
user = Blueprint('user', __name__, template_folder='templates/user', static_folder='static/user')

@user.get("/user/csv_id")
def csv_id() -> RouteResponseType:
    """
    Returns the path for a current user's profile picture.
    """
    if not current_user:
        return RouteResponse.failed("User csv id not found")
    return RouteResponse.success(data={ "csv_id" : current_user.csv_id })

@user.get("/user/username")
def username() -> RouteResponseType:
    """
    Returns the path for a current user's profile picture.
    """
    if not current_user:
        return RouteResponse.failed("Username not found")
    return RouteResponse.success(data={ "username" : current_user.username })

@user.get("/user/<int:user_id>/profile_picture")
def profile_picture(user_id: int) -> RouteResponseType:
    """
    Returns the path for a user's profile picture.
    """
    user: User = User.query.filter_by(id=user_id).first()
    if not user:
        return RouteResponse.failed("Profile picture cannot be found")
    return RouteResponse.success(data={ "profile_picture" : url_for('static', filename='profile_pictures/' + user.profile_picture) })

@user.get("/user/profile_picture")
def current_user_profile_picture() -> RouteResponseType:
    """
    Returns the path for a current user's profile picture.
    """
    if not current_user:
        return RouteResponse.failed("Profile picture cannot be found")
    return RouteResponse.success(data={ "profile_picture": url_for('static', filename='profile_pictures/' + current_user.profile_picture) })

@user.get("/login")
def login_form() -> str:
    """
    Displays the login form.
    """
    logout_user()
    form: LoginForm = LoginForm()
    return render_template("login.html", form=form)

@user.post("/login")
def login() -> RouteResponseType:
    """
    Logs the user in.
    """
    form: LoginForm = LoginForm(request.form)
    email_input: str = form.login_email.data.strip()
    password_input: str = form.login_password.data

    user: User = User.query.filter_by(email=email_input).first()
    
    if not form.validate():
        return RouteResponse.failed("Login validation failed", data=[field.errors for field in form if field.errors])
    
    if user and not check_password_hash(user.password, password_input):
        return RouteResponse.failed("No matching password")
    
    login_user(user)
    
    return RouteResponse.success(data={ "url" : url_for('index._index') })

@user.get("/logout")
def logout() -> any:
    """
    Logs the user out.
    """
    logout_user()
    return redirect(url_for('user.login_form'))

@user.get("/register")
def register_form() -> any:
    """
    Displays the registration form.
    """
    form: RegisterForm = RegisterForm()
    return render_template("register.html", form=form)

@user.post("/register")
def register() -> RouteResponseType:
    """
    Registers the user.
    """
    form: RegisterForm = RegisterForm(request.form)
    
    if not form.validate():
        return RouteResponse.failed([field.errors for field in form if field.errors])
    
    new_user = User()

    new_user.email: str = form.register_email.data
    new_user.username: str = form.register_username.data
    new_user.password: str = generate_password_hash(form.register_password.data)

    try:

        new_user.insert()
        return RouteResponse.success(data={ "url" : url_for('user.login_form') })
    
    except SQLAlchemyError as error:
        print(str(error))
        return RouteResponse.failed("Error in registering the user")

    except CsvAlchemy.RowNotFoundException:
        return RouteResponse.failed("Error in saving user to csv")

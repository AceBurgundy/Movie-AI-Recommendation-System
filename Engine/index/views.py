from Engine.api_response import RouteResponse, RouteResponseType
from flask import render_template, request, url_for, Blueprint
from flask_login import current_user, login_required
from flask import request
from Engine import db

index = Blueprint('index', __name__, template_folder='templates/index', static_folder='static/index')

@index.get("/night-mode")
def get_current_mode():
    """
    Retrieve the current night mode setting for the user.

    Returns:
    --------
        JSON: The current night mode setting.
    """
    return RouteResponse.success(data={"mode": current_user.night_mode})

@index.post("/night-mode")
def set_current_mode() -> RouteResponseType:
    """
    Set the current night mode setting for the user.

    Returns:
    --------
        JSON: Success status of setting the mode.
    """
    data = request.get_json()
    mode = data.get('mode')
    
    if mode == "Day":
        current_user.night_mode: bool = False
        db.session.commit()
        return RouteResponse.success()
    
    if mode == "Night":
        current_user.night_mode: bool = True
        db.session.commit()
        return RouteResponse.success()

    return RouteResponse.failed("Error in setting mode")

@index.get("/")
@login_required
def _index() -> str:
    """
    Load the root page.

    Returns:
    --------
        render_template: Rendered HTML template with necessary data.
    """
    page_title: str = "DASHBOARD"
    image_file: str = url_for( 'static', filename='profile_pictures/' + current_user.profile_picture )
    
    return render_template(
        "index.html",
        image_file=image_file,
        page_title=page_title
    )

@index.get("/about")
def about() -> str:
    """
    Load the about page.

    Returns:
    --------
        render_template: Rendered HTML template with necessary data.
    """
    page_title: str = "DASHBOARD"
    image_file: str = url_for( 'static', filename='profile_pictures/' + current_user.profile_picture )
    
    return render_template(
        "about.html",
        image_file=image_file,
        page_title=page_title
    )

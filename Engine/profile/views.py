from typing import Union
from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from Engine.api_response import RouteResponse, RouteResponseType
from Engine.profile.forms import DeleteAccountForm, ProfileForm
from flask_login import current_user, login_required
from Engine.helpers import save_picture
from Engine.models import User
from Engine import db

profile: Blueprint = Blueprint('profile', __name__, template_folder='templates/profile', static_folder='static/profile')

profiles_folder = 'profile_pictures/'

@profile.get("/profile/<int:user_id>")
@login_required
def get_profile(user_id) -> str:
    """
    Route to retrieve and render the profile page for a user.

    Args:
    -----
        user_id (int): The ID of the user to display the profile for.

    Returns:
    --------
        rendered_template (str): The HTML template rendered with the user's profile information.
    """

    user: User = User.query.get(user_id)
    user_image: str = url_for('static', filename=profiles_folder + user.profile_picture)

    form: ProfileForm = ProfileForm()
    delete_account_form: DeleteAccountForm = DeleteAccountForm()

    image_file: str = url_for('static', filename=profiles_folder + current_user.profile_picture)

    form.username.data: str = user.username
    form.banner.data: str = user.banner

    return render_template(
        "profile.html",
        form=form,
        delete_account_form=delete_account_form,
        image_file=image_file,
        user_id=user_id,
        user_image=user_image
    )

@profile.post("/profile")
@login_required
def post_profile() -> Union[Response, str]:
    """
    Route to handle updating the user's profile.

    Returns:
    --------
        response (str): Redirects to the user's profile page if the profile is successfully updated.
                        Otherwise, renders the profile page with the appropriate error messages.
    """
    form: ProfileForm = ProfileForm()
    delete_account_form: DeleteAccountForm = DeleteAccountForm()
    image_file: str = url_for('static', filename=profiles_folder + current_user.profile_picture)

    if form.validate_on_submit():
        if form.profilePicture.data:
            current_user.profile_picture: str = save_picture("static/profile_pictures", form.profilePicture.data)

        current_user.username: str = form.username.data
        current_user.banner: str = form.banner.data
        flash('Successfully updated profile')
        db.session.commit()
        return redirect(url_for('profile.get_profile', user_id=current_user.id))
    else:
        return render_template(
            'profile.html',
            form=form,
            delete_account_form=delete_account_form,
            image_file=image_file,
            error=form.errors
        )


@profile.post("/change-password")
@login_required
def change_password() -> RouteResponseType:
    """
    Route to handle changing the user's password.

    Returns:
    --------
        response (str): JSON response indicating the success or failure of the password change.
    """
    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not new_password or not old_password:
        return RouteResponse.failed("Fields cannot be empty")
    
    if not check_password_hash(current_user.password, old_password):
        return RouteResponse.failed("Passwords do not match")
    
    current_user.password: str = generate_password_hash(new_password)
    db.session.commit()

    return RouteResponse.success("Password Changed")

@profile.post("/profile/delete")
@login_required
def delete_account() -> RouteResponseType:
    """
    Route to handle deleting the user's account.

    Returns:
    --------
        response (str): JSON response indicating the success or failure of the account deletion.
    """
    delete_account_form: DeleteAccountForm = DeleteAccountForm()

    if delete_account_form.validate_on_submit():

        if not check_password_hash(current_user.password, delete_account_form.password.data):
            return RouteResponse.failed("Account deletion failed. Passwords do not match")
        
        current_user.delete()

        # Redirect the user to the login page immediately
        return RouteResponse.success(data={"url": url_for('user.login')})
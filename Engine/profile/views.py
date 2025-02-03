from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from Engine.profile.forms import deleteAccountForm, profileForm
from flask_login import current_user, login_required
from Engine.helpers import save_picture
from Engine.models import User
from Engine import db
from Engine.recommender.CsvAlchemy import CsvAlchemy

profile = Blueprint('profile', __name__, template_folder='templates/profile', static_folder='static/profile')

@profile.get("/profile/<int:user_id>")
@login_required
def get_profile(user_id):
    """
    Route to retrieve and render the profile page for a user.

    Args:
        user_id (int): The ID of the user to display the profile for.

    Returns:
        rendered_template (str): The HTML template rendered with the user's profile information.
    """

    user = User.query.get(user_id)
    user_image = url_for('static', filename='profile_pictures/' + user.profile_picture)

    form = profileForm()
    delete_account_form = deleteAccountForm()

    image_file = url_for('static', filename='profile_pictures/' + current_user.profile_picture)

    form.username.data = user.username
    form.banner.data = user.banner

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
def post_profile():
    """
    Route to handle updating the user's profile.

    Returns:
        response (str): Redirects to the user's profile page if the profile is successfully updated.
                        Otherwise, renders the profile page with the appropriate error messages.
    """

    form = profileForm()
    delete_account_form = deleteAccountForm()
    image_file = url_for('static', filename='profile_pictures/' + current_user.profile_picture)

    if form.validate_on_submit():
        if form.profilePicture.data:
            current_user.profile_picture = save_picture("static/profile_pictures", form.profilePicture.data)

        current_user.username = form.username.data
        current_user.banner = form.banner.data
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
def change_password():
    """
    Route to handle changing the user's password.

    Returns:
        response (str): JSON response indicating the success or failure of the password change.
    """

    data = request.get_json()

    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not new_password or not old_password:
        return jsonify({'status': 'success', 'message': 'Fields cannot be empty'})

    if not check_password_hash(current_user.password, old_password):
        return jsonify({'status': 'error', 'message': 'Passwords do not match'})

    current_user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Password Changed'})

from flask import current_app

@profile.post("/profile/delete")
@login_required
def delete_account():
    """
    Route to handle deleting the user's account.

    Returns:
        response (str): JSON response indicating the success or failure of the account deletion.
    """

    delete_account_form = deleteAccountForm()

    if delete_account_form.validate_on_submit():

        if not check_password_hash(current_user.password, delete_account_form.password.data):
            return jsonify({'status': 'error', 'message': 'Passwords do not match'})

        try:
            current_user.delete()
        except CsvAlchemy.RowNotFoundException as error:
            print(str(error))
            return jsonify({'status': 'error', 'message': 'Failed to delete user'})

        # Redirect the user to the login page immediately
        return jsonify({'status': 'success', 'url': url_for('user.login')})

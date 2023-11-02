import asyncio
from Engine.api_response import RouteResponse, RouteResponseType
from flask import jsonify, Blueprint, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from Engine.csv_alchemy import CsvAlchemy
from Engine.models import Comment, User
from flask_login import current_user
from typing import Union

from Engine.recommender.AI import refilter_users

comment = Blueprint("comment", __name__)

@comment.get('/comments/user/<int:author_csv_id>/profile_picture')
def get_author_data(author_csv_id):
    """
    The function `get_author_data` retrieves the username and profile picture path of a user based on
    their CSV ID.
    
    Args:
    -----
        author_csv_id: The `author_csv_id` parameter is the unique identifier of the author in the CSV file. 
        It is used to query the database and retrieve the author's data.
    
    Returns:
    --------
        a JSON response. If the author is found, it returns a success response with the author's username
        and profile picture path. If the author is not found, it returns a failed response with an error
        message.
    """
    author = User.query.filter_by(csv_id=author_csv_id).one()

    if author:
        return RouteResponse.success(data={
            "username": author.username,
            "profile_picture_path": url_for('static', filename='profile_pictures/' + author.profile_picture)
        })
    
    return RouteResponse.failed("Cannot find user profile")
    
@comment.get('/comments/<int:movie_csv_id>')
def movie_comments(movie_csv_id) -> RouteResponseType:
    """
    The function `movie_comments` retrieves comments for a given movie title and returns them in a JSON
    response.
    
    Args:
    -----
        movie_csv_id: str = The `movie_csv_id` parameter is the title of the movie which we want to retrieve
        the comments.
    
    Returns:
    --------
        a JSON response with the comments for a specific movie. If the movie cannot be found, it returns a
        failed response with an error message. If there are no comments for the movie, it returns a failed
        response with a message indicating that no comments were found. If there are comments for the movie,
        it returns a successful response with the comments in a list format.
    """
    comments = Comment.query.filter_by(movie_csv_id=movie_csv_id).all()

    if comments:
        return RouteResponse.success(data={
            "comments" : comments, 
            "current_user_csv_id" : current_user.csv_id
            })
    
    return RouteResponse.failed("No comments yet")

@comment.post('/comment/<int:parameter_movie_csv_id>/create')
def comment_movie(parameter_movie_csv_id) -> RouteResponseType:
    """
    Comments on a movie using its title and user ID, while analyzing the sentiment polarity of the comment.

    Args:
    - parameter_movie_csv_id (str): The title of the movie to be commented on.

    Returns:
    - JSON: A JSON response indicating the success or failure of the commenting operation.
    """
    data = request.get_json()
    comment: Union[str, None] = data.get('comment', None)

    if comment is None or comment.strip() == '':
        return RouteResponse.failed("Comment cannot be empty")

    try:

        new_comment = Comment()
        new_comment.content = comment
        new_comment.user_csv_id=current_user.csv_id
        new_comment.movie_csv_id=parameter_movie_csv_id

        new_comment.insert()

        asyncio.create_task(refilter_users())

        return RouteResponse.success("Comment successfully added", { 
            "new_comment" : new_comment,
            "current_user_csv_id" : current_user.csv_id
        })
    
    except (SQLAlchemyError, CsvAlchemy.RowNotFoundException) as error:        
        
        print(str(error))
        return RouteResponse.failed("Failed to add comment")
    
@comment.post('/comment/<int:comment_id>/update')
def update_comment(comment_id) -> RouteResponseType:
    """
    Updates a comment on a movie using its id

    Args:
    - comment_id (int): The id of the comment.

    Returns:
    - JSON: A JSON response indicating the success or failure of the commenting operation.
    """
    data = request.get_json()
    new_comment: Union[str, None] = data.get('new_comment', None)

    if new_comment is None or new_comment.strip() == '':
        return RouteResponse.failed("Comment cannot be empty")

    try:

        comment = Comment.query.filter_by(id=comment_id).one()

        if comment:
            comment.update(new_comment)

        asyncio.create_task(refilter_users())

        return RouteResponse.success("Comment successfully added", { "comment" : comment } )
    
    except (SQLAlchemyError, CsvAlchemy.RowNotFoundException) as error:        
        
        print(str(error))
        return RouteResponse.failed("Failed to update comment")

@comment.post('/comment/<int:comment_id>/delete')
def remove_comment(comment_id) -> RouteResponseType:
    """
    Removes a comment based on its ID.

    Args:
    - comment_id (int): The ID of the comment to be removed.

    Returns:
    - JSON: A JSON response indicating the success or failure of the comment removal operation.
    """
    if comment_id is None:
        return RouteResponse.failed("Comment id is required")

    try:
    
        comment: Comment = Comment.query.filter_by(id=comment_id).one()

        if comment:
            comment.delete()

        asyncio.create_task(refilter_users())

        return RouteResponse.success("Comment removed successfully")
    
    except CsvAlchemy.RowNotFoundException as error:

        print(str(error))
        return RouteResponse.failed("Failed to delete comment")

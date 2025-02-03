from Engine.recommender.CsvAlchemy import CsvAlchemy, ratings, movies
from Engine.api_response import RouteResponse, RouteResponseType
from flask import request, jsonify, Blueprint
from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user
from Engine.models import Comment
from . import AI_less_comments
from sqlalchemy import insert
from numpy import ndarray
from typing import Dict, List, Union
from Engine import db
from . import AI

recommender = Blueprint('recommender', __name__)

@recommender.post('/recommend')
def get_recommendations() -> RouteResponseType:
    """
    Uses collaborative filtering and content-based filtering to find 20 movie recommendations for the user.

    Returns:
    - JSON: A JSON response containing movie recommendations.
    """
    title = request.form["title"]

    if not title or str(title).strip() == '':
        return jsonify(RouteResponse.failed("Missing movie title"))

    recommendations = AI.recommend(title)

    # Check if recommendations is a NumPy array and convert it to a list if necessary
    if isinstance(recommendations, ndarray):
        recommendations = recommendations.tolist()

    return jsonify(RouteResponse.success(None, recommendations))

@recommender.post('/rate/<movie_title>')
def rate_movie(movie_title) -> RouteResponseType:
    """
    Rates a movie using its title and the user ID.

    Args:
    - movie_title (str): The title of the movie to be rated.

    Returns:
    - JSON: A JSON response indicating the success or failure of the rating operation.
    """
    data = request.get_json()
    rating = data.get('rating', None)

    if rating is None:
        return jsonify(RouteResponse.failed("Missing rating data"))

    retrieve_movie = None

    try:
        retrieve_movie = movies.clean_retrieve({
            "column_name": "title",
            "column_data": movie_title
        })
    except Exception as error:
        print(str(error))
        return jsonify(RouteResponse.failed("Movie not found"))

    movie_id = retrieve_movie["movie_id"]

    try:

        rating_result = ratings.insert_row({
            "user_id": current_user.id,
            "movie_id": movie_id,
            "rating": rating
        })
        return jsonify(RouteResponse.success("Movie rated successfully", rating_result))

    except CsvAlchemy.InsertionException as error:

        print(str(error))
        return jsonify(RouteResponse.failed(f"Failed to rate movie {movie_title}"))

@recommender.post('/unrate/<movie_title>')
def unrate_movie(movie_title) -> RouteResponseType:
    """
    Unrates a movie using its title and the user ID.

    Args:
    - movie_title (str): The title of the movie to be unrated.

    Returns:
    - JSON: A JSON response indicating the success or failure of the unrating operation.
    """
    movie_id = find_movie_id(movie_title)

    if movie_id is None:
        return jsonify(RouteResponse.failed("Cannot unrate movie as it cannot be not found"))

    try:

        ratings.delete_row({
            "user_id": current_user.id,
            "movie_id": movie_id
        })

        return jsonify(RouteResponse.success("Rating removed successfully"))

    except Exception as error:

        print(str(error))
        return jsonify(RouteResponse.failed("Failed to unrate movie"))

@recommender.post('/comments/<movie_title>')
def movie_comments(movie_title) -> RouteResponseType:
    """
    The function `movie_comments` retrieves comments for a given movie title and returns them in a JSON
    response.

    Args:
        movie_title: The `movie_title` parameter is the title of the movie for which you want to retrieve
        comments.

    Returns:
        a JSON response containing the comments for a specific movie. If the movie cannot be found, it
        returns a failed response with an error message. If there are no comments for the movie, it returns
        a failed response with a corresponding message. If there are comments for the movie, it returns a
        successful response with the comments as a list of dictionaries.
    """
    movie_id = find_movie_id(movie_title)

    if movie_id is None:
        return jsonify(RouteResponse.failed("Cannot comment on movie as it cannot be not found"))

    movie_data = movies.csv_data

    comments_for_the_movie = movie_data[movie_data['movie_id'] == movie_id]

    if comments_for_the_movie.empty:
        return jsonify(RouteResponse.failed("No comments found for this movie"))

    comment_list: List[Dict[str, Union[int, str]]] = comments_for_the_movie[['user_id', 'comment_id', 'content']].to_dict(orient='records')

    return jsonify(RouteResponse.failed("Comments for the movie", comment_list))

@recommender.post('/comment/<movie_title>/create')
def comment_movie(movie_title) -> RouteResponseType:
    """
    Comments on a movie using its title and user ID, while analyzing the sentiment polarity of the comment.

    Args:
    - movie_title (str): The title of the movie to be commented on.

    Returns:
    - JSON: A JSON response indicating the success or failure of the commenting operation.
    """
    data = request.get_json()
    comment = data.get('comment', None)

    if comment is None or comment.strip() == '':
        return jsonify(RouteResponse.failed("Comment cannot be empty"))

    movie_id = find_movie_id(movie_title)

    if movie_id is None:
        return jsonify(RouteResponse.failed("Cannot comment on movie as it cannot be not found"))

    try:

        db.session.execute(insert(Comment).values(
            content=comment,
            user_csv_id=current_user.csv_id,
            movie_csv_id=movie_id
        ))

        return jsonify(RouteResponse.success("Comment successfully added", { "comment": comment} ))

    except (SQLAlchemyError, CsvAlchemy.RowNotFoundException) as error:

        print(str(error))
        return jsonify(RouteResponse.failed("Failed to add comment"))

@recommender.post('/comment/<int:comment_id>/update')
def update_comment(comment_id) -> RouteResponseType:

    data = request.get_json()
    new_comment = data.get('new_comment', None)

    if new_comment is None:
        return jsonify(RouteResponse.failed("New comment cannot be empty"))

    if str(new_comment) == '':
        return jsonify(RouteResponse.failed("New comment cannot be empty"))

    try:

        comment = Comment.query.filter_by(id=comment_id).first()

        if comment:
            comment.update(new_comment=comment)

        return jsonify(RouteResponse.success("Comment updated successfully"))

    except (CsvAlchemy.RowNotFoundException, CsvAlchemy.ValidationException) as error:

        print(str(error))
        return jsonify(RouteResponse.failed("Failed to update comment"))

@recommender.post('/comment/<int:comment_id>/delete')
def remove_comment(comment_id) -> RouteResponseType:
    """
    Removes a comment based on its ID.

    Args:
    - comment_id (int): The ID of the comment to be removed.

    Returns:
    - JSON: A JSON response indicating the success or failure of the comment removal operation.
    """

    try:

        comment = Comment.query.filter_by(id=comment_id)

        if comment:
            comment.delete()

        return jsonify(RouteResponse.success("Comment removed successfully"))

    except CsvAlchemy.RowNotFoundException as error:

        print(str(error))
        return jsonify(RouteResponse.failed("Failed to delete comment"))

def find_movie_id(movie_title) -> Union[int, None]:
    """
    Searches for the movie ID based on its title in a CSV file.

    Args:
    - movie_title (str): The title of the movie to search for.

    Returns:
    - int or None: The movie ID if found, or None if not found.
    """
    try:

        retrieve_movie = movies.clean_retrieve({
            "column_name": "title",
            "column_data": movie_title
        })

        return retrieve_movie["movie_id"]

    except CsvAlchemy.RowNotFoundException as error:

        print(str(error))
        return None

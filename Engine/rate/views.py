import asyncio
from Engine.api_response import RouteResponse, RouteResponseType
from Engine.csv_alchemy import CsvAlchemy, ratings
from flask_login import current_user
from flask import Blueprint, request
from pandas import DataFrame

from Engine.recommender.AI import refilter_users

rating: Blueprint = Blueprint('rating', __name__)

@rating.get('/rate/<int:movie_csv_id>/user')
def user_movie_rating(movie_csv_id) -> RouteResponseType:
    """
    Returns the users current rating of a movie using its csv id and user csv id.

    Args:
    -----
    - movie_csv_id (int): The csv id of the movie to be rated.

    Returns:
    --------
    - JSON: A JSON response indicating the success or failure of acquiring the movies rating.
    """

    result = ratings.clean_retrieve({
        "user_id" : current_user.csv_id,
        "movie_id" : movie_csv_id,
    })

    if not result:
        return RouteResponse.failed()

    return RouteResponse.success(data=result)

@rating.get('/rate/<int:movie_csv_id>')
def movie_rating(movie_csv_id) -> RouteResponseType:
    """
    Returns the current rating of a movie using its csv id.

    Args:
    -----
    - movie_csv_id (int): The  csv id of the movie to be rated.

    Returns:
    --------
    - JSON: A JSON response indicating the success or failure of acquiring the movies rating.
    """
    ratings_rows: DataFrame = ratings.csv_data[ratings.csv_data['movie_id'] == movie_csv_id]

    if ratings_rows.empty:
        return RouteResponse.failed()

    average_rating = ratings_rows['content'].mean()

    return RouteResponse.success(data={ 
        "avarage_rating" : average_rating,
        "vote_count" : len(ratings_rows)
    })

@rating.post('/rate/<int:movies_csv_id>/create')
def rate_movie(movies_csv_id) -> RouteResponseType:
    """
    Rates a movie using its csv id and the user csv id.

    Args:
    -----
    - movies_csv_id (int): The csv id of the movie to be rated.

    Returns:
    --------
    - JSON: A JSON response indicating the success or failure of the rating operation.
    """
    data = request.get_json()
    rating = data.get('rating', None)

    if rating is None:
        return RouteResponse.failed("Missing rating data")

    try:

        rating_value = float(rating)
        
        if rating_value <= 5 and rating_value >= 0:

            ratings.insert_row({
                "user_id": current_user.csv_id,
                "movie_id": movies_csv_id,
                "content": rating_value
            })

            asyncio.create_task(refilter_users())

            return RouteResponse.success("Movie rated successfully")
        else:
            return RouteResponse.failed("Rating must be between 0 and 5")
    
    except ValueError:
        return RouteResponse.failed("Input must be a number or a decimal number")
    
    except (CsvAlchemy.ValidationException, CsvAlchemy.InsertionException):
        return RouteResponse.failed(f"Failed to rate movie with id {movies_csv_id}")
    
@rating.post('/rate/<int:movie_csv_id>/delete')
def unrate_movie(movie_csv_id) -> RouteResponseType:
    """
    Unrates a movie using its csv id and the user csv id.

    Args:
    -----
    - movie_csv_id (int): The csv id of the movie to be unrated.

    Returns:
    --------
    - JSON: A JSON response indicating the success or failure of the unrating operation.
    """
    try:
        
        ratings.delete_row({
            "user_id": current_user.csv_id,
            "movie_id": movie_csv_id
        })

        asyncio.create_task(refilter_users())

        return RouteResponse.success("Rating removed successfully")
    
    except CsvAlchemy.RowNotFoundException:
    
        return RouteResponse.failed("Failed to unrate movie")

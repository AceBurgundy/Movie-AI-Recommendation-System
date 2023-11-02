from Engine.api_response import RouteResponse, RouteResponseType 
from flask import request, jsonify, Blueprint
from typing import Dict, List, Union
from . import AI

recommender = Blueprint('recommender', __name__)

memo: Dict[str, List[str]] = {}

@recommender.post('/recommend')
def get_recommendations() -> RouteResponseType:
    """
    Uses collaborative filtering and content-based filtering to find 20 movie recommendations for the user.

    Returns:
    --------
        JSON: A JSON response containing movie recommendations.
    """

    global memo

    title: str = request.form["title"]

    if not title:
        return RouteResponse.failed("Missing movie title")

    if str(title).strip() == '':
        return RouteResponse.failed("Missing movie title")

    cached_recommendation = memo.get(title, None)

    if cached_recommendation:
        return RouteResponse.success(data=cached_recommendation)

    recommendations: List[Dict[str, Union[str, int]]] = AI.old_recommend(title)

    memo[title] = recommendations

    return RouteResponse.success(data=recommendations)

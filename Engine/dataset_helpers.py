from Engine.csv_alchemy import CsvAlchemy, movies, ratings, user_ids, comments
from typing import Any, Callable, Optional, Union
import re

# Type aliases
StringList = list[str]
DataFrame = Any  # Import 'Any' if the DataFrame type is not from a known library

def run_simple_io(worker: Optional[Callable[[str], Any]] = None, message: str = "\n\tInput: ") -> Any:
    """
    Runs a simple input-output operation with an optional callback function.
    
    Args:
    -----
        worker (function): The callback function to process user input.
        message (str): The message to display as input prompt (default is "\n\tInput:").

    Returns:
    --------
        The result of the callback function if provided, otherwise None.
    """
    value = ''
    while value == '':
        value = input(message)
    if worker:
        return worker(value)

def clean_title(title: str) -> str:
    """
    Removes any non-alphanumeric or non-space characters from a string.

    Args:
    -----
        title (str): The input string.

    Returns:
    --------
        str: The cleaned string.
    """
    return re.sub("[^a-zA-Z0-9 ]", '', title)

def get_latest_csv_user_id() -> int:
    """
    Retrieves the latest user ID from CSV files and initializes it if necessary.

    Returns:
    --------
        int: The latest user ID.
    """
    
    if ratings.csv_data.empty:
        set_initial_user_id(1)
        return 1

    if user_ids.csv_data.empty:
        most_recent_user = ratings.csv_data['user_id'].max() + 1        
        set_initial_user_id(most_recent_user)
        return most_recent_user.item()

    most_recent_user = user_ids.csv_data['user_id'].max() + 1
    set_initial_user_id(most_recent_user)
    return most_recent_user.item()

def get_latest_csv_comment_id() -> int:
    """
    Retrieves the latest comment ID from CSV files and initializes it if necessary.

    Returns:
    --------
        int: The latest comment ID.
    """

    if comments.csv_data.empty:
        return 1

    most_recent_user = comments.csv_data['comment_id']

    if most_recent_user.empty:
        return 1

    next_user = most_recent_user.max() + 1
    return next_user.item()

def set_initial_user_id(user_id: int) -> None:
    """
    Sets the initial user ID in a CSV file.

    Args:
    -----
        user_id (int): The user ID to be added to the CSV file.

    Returns:
    --------
        None
    """
    return user_ids.insert_row({
        "user_id": user_id
    })

def remove_csv_user_id(user_id: int) -> None:
    """
    Removes a user id record from user_ids.csv

    Args:
    -----
        user_id (int): The user ID to be removed from the CSV file.
    """
    return user_ids.delete_row({
        "user_id" : user_id
    })

def remove_csv_comment_id(comment_id: int) -> None:
    """
    Removes a comment id record from comments.csv

    Args:
    -----
        comment_id (int): The comment ID to be removed from the CSV file.
    """
    return comments.delete_row({
        "comment_id" : comment_id
    })

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
            "title" : movie_title
        })

        return retrieve_movie["movie_id"]

    except CsvAlchemy.RowNotFoundException:
        
        return None

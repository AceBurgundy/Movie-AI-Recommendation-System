from ..csv_alchemy import movies as movies_csv, ratings as ratings_csv, comments as comments_csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from numpy import ndarray, argpartition, isnan, isin
import Engine.dataset_helpers as dataset_helpers
from typing import Dict, List, Optional, Union
from pandas import Series, DataFrame, concat
from scipy.sparse import spmatrix, vstack
from ..helpers import timer
import asyncio
import json

LIST_OF_DICTIONARIES = List[Dict[str, any]]

'''
    Guidelines on comments:
    To remove all multiline comments, find with regex """[^"]*""" { newline }, then Alt + Enter , then backspace <-
'''

movies: DataFrame = movies_csv.csv_data
"""
    Reads the movie dataset
"""

movies["clean_titles"]: Series = movies["title"].apply(dataset_helpers.clean_title)
"""
    creates a new column | clean_titles | then,
    loops through each title and sets the value of that movies' clean_title column
    into the clean title of the movie

    +------------------+-------------------+
    |      title       |    clean_titles   |
    +------------------+-------------------+
    |  Jumanji (1995)  |    Jumanji 1995   |
    +------------------+-------------------+
    | Bad Poems (1995) |  Bad Poems 2018   |
    +------------------+-------------------+ 
"""

vectorizer: TfidfVectorizer = TfidfVectorizer(ngram_range=(1,2))
"""
    Creates a vector of movie titles and their corresponding frequency value

    Term Frequency
                    +----------+-----------+----------+
                    |  potter  |   harry   |   the    |
                    +----------+-----------+----------+
         The        |    0     |     0     |    1     |
                    +----------+-----------+----------+
   Harry the Potter |    1     |     1     |    1     |
                    +----------+-----------+----------+ 
      The Harry     |    0     |     1     |    1     |
                    +----------+-----------+----------+ 

    Inverse Document Frequency

                    +----------+----------+----------+
                    |  potter  |   harry  |   the    |
                    +----------+----------+----------+
         The        | log(3/1) | log(3/2) | log(3/3) |
                    +----------+----------+----------+
   Harry the Potter | log(3/1) | log(3/2) | log(3/3) |
                    +----------+----------+----------+ 
      The Harry     | log(3/1) | log(3/2) | log(3/3) |
                    +----------+----------+----------+
                    
    Term Frequency * Inverse Document Frequency

    +----------+-----------+----------+ 
    |  potter  |   harry   |   the    | Returns a vector of each movie which 
    +----------+-----------+----------+ is a set of numbers that describe each movie
    |    0     |     0     |    1     |
    +----------+-----------+----------+
    |   .477   |   .176    |    0     |
    +----------+-----------+----------+ 
    |    0     |   .176    |    0     |
    +----------+-----------+----------+ 

    How searching works?

    Let's assume you are looking for "Harry Potter"

    Harry Potters TF * IDF will be
    
    +----------+-----------+----------+
    |   .477   |   .176    |    0     |
    +----------+-----------+----------+ 

    Then compares Harry Potters vector with all vectors in the dataset
    In this case, it returns the middle value as it has the most similar value
    which means it is the closest to Harry Potter
    +----------+-----------+----------+ 
    |  potter  |   harry   |   the    | 
    +----------+-----------+----------+ 
    |    0     |     0     |    1     | .0
    +----------+-----------+----------+
    |   .477   |   .176    |    0     | 1
    +----------+-----------+----------+ 
    |    0     |   .176    |    0     | 0
    +----------+-----------+----------+ 

    ngram_range(1,2) Not only reads "the", "harry" and "harry", 
    but also 2 consecutive word combination. ("the harry", "harry potter")
    which helps searches become a little more accurate

    This is all done by sckit-learns::TfidfVectorizer
"""

tfidf: spmatrix = vectorizer.fit_transform(movies["clean_titles"])
"""
    The code implements both Content-Based Filtering and Collaborative Filtering.

    The search function uses Content-Based Filtering. 
    It uses TF-IDF (Term Frequency-Inverse Document Frequency) 
    to convert movie titles into a matrix of TF-IDF features. 
    
    Then, the find_similar_movies function uses cosine similarity to calculate 
    the similarity between the movie titles.
"""

def update_tfidf(list_of_new_movie_indices: list[int]) -> None:
    """

    For future purposes where in any case that a new movie will be added.
    ---------------------------------------------------------------------

    The function `update_model` takes a list of new movie indices, retrieves the corresponding movie
    titles from a dataframe, cleans the title, transforms them using a vectorizer, 
    and updates the global variables `tfidf` by appending the new data.
    
    Args:
    -----
        list_of_new_movie_indices (list[int]): A list of integers representing the indices of new movies
        in the dataset that you want to add to the model.
    """
    global tfidf
    new_data: Series = movies["title"].iloc(list_of_new_movie_indices)
    clean_data: Series = new_data.apply(dataset_helpers.clean_title)
    new_tfidf: spmatrix = vectorizer.transform(clean_data)
    tfidf = vstack([tfidf, new_tfidf])

# search
def search(title: str) -> DataFrame:
    """
    The `search` function takes a movie title as input, converts it into a vector using a query
    vectorizer, calculates the cosine similarity between the query vector and the TF-IDF vectors of all
    movies, selects the top 10 similar movies based on the similarity scores, and returns the details of
    those movies in a DataFrame.
    
    Args:
    -----
        title (str): The `title` parameter is a string that represents the movie title you want to search for.
    
    Returns:
    --------
        a DataFrame containing the top 10 movies that are similar to the given movie title. The movies are
        sorted in descending order of relevance.
    """

    query_vectorizer = vectorizer.transform([dataset_helpers.clean_title(title)])
    """        
        query_vectorizer = 
            (0, 153617)   0.6768756912902416
            (0, 153609)   0.6189879213267938
            (0, 138134)   0.39836321591217777

        (0, 153617)   0.6768756912902416 means
        +---+--------------------+
        |   |       153617       | The value at row 0 column 153617 is 0.6768756912902416
        +---+--------------------+ which might be the weight of a string in Toy Story
        | 0 | 0.6768756912902416 |
        +---+--------------------+

        There are 3 coordinates in the query_vectorizer specifying the weight of each string and its ngram.
        "Toy", "Story", "Toy Story"
    """

    list_of_scores_similar_to_the_movie: ndarray = cosine_similarity(query_vectorizer, tfidf).flatten()
    """
        returns a list where the higher the value of the element, 
        the closer it is to being the same as the movie title

        list_of_scores_similar_to_the_movie = [0.77362283, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    """

    indices_of_the_top_10_movies: ndarray = argpartition(list_of_scores_similar_to_the_movie, -10)[-10:]
    """
        returns a list with 5 elements where each element is the index of the similarity value
        indices_of_the_top_5_movie = [20497, 59767, 0, 14813,  3021]
    """

    results: DataFrame = movies.iloc[indices_of_the_top_10_movies][::-1]
    """
        indexes the movie data using the similarity indexes
        
              movie_id  ...              clean_titles
        20497   106022  ...  Toy Story of Terror 2013
        59767   201588  ...          Toy Story 4 2019
        0            1  ...            Toy Story 1995
        14813    78499  ...          Toy Story 3 2010
        3021      3114  ...          Toy Story 2 1999

        Now we have 5 movies that are related to "Toy Story" and arranged in descending order using ([::-1])
        as more relevant results are stored at the bottom of the results.
    """

    return results

filtered_users: Optional[Series] = None
rating_boundery: int = 4

# Define a function to filter users based on their average sentiment score
def include_user(user) -> bool:
    """
    The function filters users based on their average sentiment score, including them if the score is
    above 50% or if they have no comments and their rating is above a certain threshold.
    
    Args:
    -----
        user: The user parameter represents a row of data for a user in a dataset. It is assumed
        that the dataset contains columns such as "average_sentiment_score" and "rating" for each user.
    
    Returns:
    --------
        a boolean value. If the user has no comments (average_sentiment_score is NaN), it will return True
        if their rating is greater than the rating_boundery. If the user has comments, it will return True
        if their average sentiment score is greater than 0.5.
    """
    user_has_no_comments: bool = isnan(user["average_sentiment_score"])
    if_ratings_had_passed: bool = user["content"] > rating_boundery
    check_if_comments_had_passed: bool = user["average_sentiment_score"] > 0.5
    return if_ratings_had_passed if user_has_no_comments else check_if_comments_had_passed

async def refilter_users():

    global filtered_users

    ratings: Series = ratings_csv.csv_data
    comments: Series = comments_csv.csv_data
    
    """
        Assume these initial ratings and comments csv data

        user_id | movie_id | rating
        1       | 100      | 4.5
        2       | 100      | 5.0
        3       | 200      | 4.0
        4       | 300      | 4.5
        5       | 100      | 4.0
        
        user_id | movie_id | content | sentiment_score
        1       | 100      | Good movie! | 0.8
        2       | 100      | Excellent!  | 0.9
        4       | 300      | Very entertaining  | 0.7
    """

    user_average_sentiment: Series = comments.groupby("user_id")["sentiment_score"].mean().reset_index()
    user_average_sentiment.rename(columns={"sentiment_score": "average_sentiment_score"}, inplace=True)

    """
        To easily explain the code above, let me explain reset_index first.
        reset_index() - sets the old index as a new column while creating a new index
        DataFrame with a custom index:

            A  B
            X  1  4
            Y  2  5
            Z  3  6

        into

        index  A  B
            0  X  1  4
            1  Y  2  5
            2  Z  3  6
        
        To explain the two line of code above, it first groups each comment by the user id, averages its sentiment scores, and resets its indexes.
        Then it renames the column sentiment_score to average_sentiment_score which now contains the averaged sentiment score of all of the users comments.
        
            user_id | avg_sentiment_score
            1       | 0.8
            2       | 0.9
            4       | 0.7
            5       | NaN
    """

    merged_ratings: DataFrame = ratings.merge(user_average_sentiment, on="user_id", how="left")
    """
        Merges user average sentiment scores with the ratings
        user_id | movie_id | rating | avg_sentiment_score
        1       | 100      | 4.5    | 0.8
        2       | 100      | 5.0    | 0.9
        3       | 200      | 4.0    | NaN
        4       | 300      | 4.5    | 0.7
        5       | 100      | 4.0    | NaN
    """

    # Update the global variable by applying the filter to get users who meet the criteria
    filtered_users = merged_ratings[merged_ratings.apply(include_user, axis=1)]

# run the filter on initial start up
asyncio.run(refilter_users())

def find_similar_movies(input_id: int) -> LIST_OF_DICTIONARIES:

    ratings: DataFrame = ratings_csv.csv_data
    movie_id: Series = ratings["movie_id"] 
    user_id: Series = ratings["user_id"]
    rating: Series = ratings["content"]

    # Get the unique users who meet the criteria
    users_who_like_a_movie: Series = filtered_users[filtered_users["movie_id"] == input_id]["user_id"].unique()
    """
        returns a unique list of ids of users who gave a 5 star rating to the movie you searched and where the average of their comments sentiment score
        are greater than 50% excluding users who has yet to comment on the movie.

        This prevents users who highly upvotes a movie for the purpose of it reaching the top comment and have their bad comments be noticed.

        users_who_like_a_movie = [36,  75,  86 ... 162527 162530 162533]
    """

    similar_movies_to_users_who_like_a_movie = ratings[(isin(user_id, users_who_like_a_movie)) & (rating > rating_boundery)]["movie_id"]
    """
        returns movies watched by users who voted 5 starts to the movie you searched

            5101            1
            5105           34
            5111          110
            5114          150
            5127          260
                        ...  
            24998854    60069
            24998861    67997
            24998876    78499
            24998884    81591
            24998888    88129
    """
    
    # movies that greater than 10% users similar to us liked
    percentage_of_each_movies_occurence: Series = similar_movies_to_users_who_like_a_movie.value_counts() / (len(users_who_like_a_movie))
    """
        similar_movies_to_users_who_like_a_movie.value_counts() returns the number of occurences for each movie id 
        
        ex: movie_id 1 showed up 18835 times

            1         18835
            318        8393
            260        7605
            356        6973
            296        6918
                    ...  
            128478        1
            125125        1
            119701        1
            107563        1
            7625          1
    
        by dividing it by the length of the ids of user who like the movie we get

            1         1.000000
            318       0.445607
            260       0.403770
            356       0.370215
            296       0.367295
                        ...   
            128478    0.000053
            125125    0.000053
            119701    0.000053
            107563    0.000053
            7625      0.000053
    """

    greater_than_10_percent_occurences: Series = percentage_of_each_movies_occurence[percentage_of_each_movies_occurence > .1]
    """
        filters the result to the number of occurences is greater than 10 percent or .1
        
            1        1.000000
            318      0.445607
            260      0.403770
            356      0.370215
            296      0.367295
                    ...   
            953      0.103053
            551      0.101195
            1222     0.100876
            745      0.100345
            48780    0.100186
    """

    movies_with_greater_than_10_percent_occurences: DataFrame = ratings[isin(movie_id, greater_than_10_percent_occurences.index) & (rating > rating_boundery)]
    """
        returns the ratings of the users to the movies with greater than 10 percent occurences

                    user_id  movie_id  rating   timestamp
            0              1      296     5.0  1147880044
            29             1     4973     4.5  1147869080
            48             1     7361     5.0  1147880055
            72             2      110     5.0  1141416589
            76             2      260     5.0  1141417172
            ...          ...      ...     ...         ...
            25000062  162541     5618     4.5  1240953299
            25000065  162541     5952     5.0  1240952617
            25000078  162541     7153     5.0  1240952613
            25000081  162541     7361     4.5  1240953484
            25000090  162541    50872     4.5  1240953372
    """

    greater_than_10_percent_movie_percentages: Series = movies_with_greater_than_10_percent_occurences["movie_id"].value_counts() / len(movies_with_greater_than_10_percent_occurences["user_id"].unique())
    """
        318      0.342220
        296      0.284674
        2571     0.244033
        356      0.235266
        593      0.225909
                ...   
        551      0.040918
        50872    0.039111
        745      0.037031
        78499    0.035131
        2355     0.025091
    """

    """ CREATING A RECOMMENDATION SCORE """

    percentage_comparisons: DataFrame = concat([greater_than_10_percent_occurences, greater_than_10_percent_movie_percentages], axis = 1)
    percentage_comparisons.columns = ["similar", "all"]
    """
                 similar        all
        movie_id
        1        1.000000  0.124728
        318      0.445607  0.342220
        260      0.403770  0.222207
        356      0.370215  0.235266
        296      0.367295  0.284674
        ...           ...       ...
        953      0.103053  0.045792
        551      0.101195  0.040918
        1222     0.100876  0.066877
        745      0.100345  0.037031
        48780    0.100186  0.068314

        movie_id shows all the movies recommended to the user
        similar shows the score of how much a person similar to the user likes the movie
        all shows the score of how an average person likes the movie
    """ 

    percentage_comparisons["score"]: Series = percentage_comparisons["similar"] / percentage_comparisons["all"]
    sorted_percentages: DataFrame = percentage_comparisons.sort_values("score", ascending=False)
    """
        adds a new column called score which contains the ratio between similar and all columns sorted in a descending order
                    similar       all     score
            movie_id
            1        1.000000  0.124728  8.017414
            318      0.445607  0.342220  1.302105
            260      0.403770  0.222207  1.817089
            356      0.370215  0.235266  1.573604
            296      0.367295  0.284674  1.290232
            ...           ...       ...       ...
            953      0.103053  0.045792  2.250441
            551      0.101195  0.040918  2.473085
            1222     0.100876  0.066877  1.508376
            745      0.100345  0.037031  2.709748
            48780    0.100186  0.068314  1.466543

        The higher the score, the better the recommendation
    """

    top_10_movie_recommendations: DataFrame = sorted_percentages.head(10).merge(movies_csv.csv_data, left_index=True, right_on="movie_id")[["movie_id", "title"]]

    top_10_movie_recommendations: LIST_OF_DICTIONARIES = top_10_movie_recommendations[["movie_id", "title"]].to_dict(orient='records')
        
    return top_10_movie_recommendations 

@timer
def recommend(movie_name: str) -> Union[LIST_OF_DICTIONARIES, List]:
    """
    The function `recommend` takes a movie name as input, searches for similar movies using
    content-based and collaborative filtering, and returns a recommendation based on the search results.
    
    Args:
    -----
        movie_name (str): The `movie_name` parameter is a string that represents the name of the movie for
        which you want to get recommendations.
    
    Returns:
    --------
        Recommendations for a movie in the format `List[Dict[str, any]]` or any empty list. 
        If similar movies are found using both content-based and collaborative filtering, those recommendations are returned. 
        If only content-based recommendations are found, those are returned. 
        If no recommendations are found, an empty list is returned.
    """
    search_results: DataFrame = search(movie_name)

    if search_results.empty:
        return []

    for movie_id in search_results["movie_id"]:

        similar_movies: LIST_OF_DICTIONARIES = find_similar_movies(movie_id)
        
        # return the recommendation found
        if len(similar_movies) > 0:
            print("\n\tRecommendation returned from both Content-Based and Collaborative filtering\n", json.dumps(similar_movies, indent = 4))
            return similar_movies
            
    search_result_recommendation: LIST_OF_DICTIONARIES = search_results[['movie_id', 'clean_titles']].to_dict(orient='records')
    print("\n\tRecommendation returned from Content-Based only\n", json.dumps(search_result_recommendation, indent = 4))

    # return the result of search results as a list of dictionaries
    return search_result_recommendation
    
if __name__ == "__main__":
    dataset_helpers.run_simple_io(recommend)

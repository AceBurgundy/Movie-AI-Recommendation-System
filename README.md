# Whisma Movie Recommender App

Welcome to the Whisma Movie Recommender App! Before you can start using the app, please follow these instructions carefully.

## Prerequisites
- Make sure you have the latest version of Python installed on your system.
- (Optional) Create a virtual environment.

## Installation
1. Clone or download this repository to your local machine.
2. Open a terminal or command prompt and navigate to the project's root directory.

   ```shell
   cd path/to/Movie-AI-Recommendation-System

3. Install the required libraries from the requirements.txt file using pip:

   ```shell
   pip install -r requirements.txt

5. Download the dataset files from the following link https://tinyurl.com/bdf8kt8a.

6. Place the downloaded dataset files in a folder called `backup` inside the project's root directory. If the backup folder doesn't exist, make one.

## Setting up the TMDB API
1. Get a working API for the script from https://www.themoviedb.org/settings/api
2. Go to apiKey.js and replace the string with your own api key

    ```shell 
    Movie-AI-Recommendation-System/Engine/static/apiKey.js 
    
## Database Setup
To set up the database for the app, run the following command:
    
    python create_database.py

This script will copy the dataset files from the backup folder to their appropriate location, create the database, and prepare it for use.

It will then prompt you if you want to start running the app.

## Running the App

The next time you run the app you may simply use the command:

    python app.py

If you want to rebuild fresh with the original dataset:

    python create_database.py

The app should now be accessible by visiting http://localhost:8080 in your web browser.

## License

[MIT](https://choosealicense.com/licenses/mit/)


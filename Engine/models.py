
from Engine.recommender.dataset_helpers import get_latest_csv_comment_id, get_latest_csv_user_id, remove_csv_comment_id, remove_csv_user_id
from Engine.recommender.CsvAlchemy import user_ids as user_ids_csv, comments as comments_csv
from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Union, override
from sqlalchemy.orm import relationship
from Engine import db, login_manager
from flask_login import UserMixin
from sqlalchemy import DateTime
from flask import current_app
from textblob import TextBlob
from datetime import datetime
from pytz import utc
import os

delete_all: str = "all, delete-orphan"

def pretty_print(table_name: str, details: Any) -> str:
    """
    The function `pretty_print` takes a table name and details as input, and returns a formatted string
    representation of the table name and details.

    Args:
        table_name: The name of the table that you want to print. It is a string value.
        details: The `details` parameter is a dictionary that contains the details or attributes of a
        table. Each key-value pair in the dictionary represents a specific detail of the table.

    Returns:
        a formatted string that includes the table name and the details. The details are formatted as
        key-value pairs, with each pair on a new line and indented with a tab.
    """
    clean_details = ",\n\t".join([f"{key}: {value}" for key, value in details.items()])
    return f"\n{table_name}:\n\t{clean_details}\n"

@login_manager.user_loader
def load_user(user_id):
    """
    The `load_user` function is a callback function used by the `login_manager` to load a user object
    from the database based on the user ID.

    Args:
        user_id: The user_id parameter is the unique identifier for a user. It is used to load a user
        object from the database based on the user_id.

    Returns:
        a User object with the specified user_id.
    """
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):

    __tablename__ = 'user'

    id: int = db.Column(db.Integer, primary_key=True)
    csv_id: int = db.Column(db.Integer, nullable=False)
    username: str = db.Column(db.String(50), unique=True)
    email: str = db.Column(db.String(120), unique=True)
    password: str = db.Column(db.String(200))
    night_mode: bool = db.Column(db.Boolean(), nullable=False, default=True)
    creation_date: DateTime = db.Column(db.DateTime(), default=datetime.now(utc))
    profile_picture: str = db.Column(db.String(100), nullable=False, default='default.jpg')
    last_online: DateTime = db.Column(db.DateTime(), default=datetime.now, onupdate=datetime.now)
    banner: str = db.Column(db.String(200), default="Give a small introduction about yourself")

    bookmarks: relationship = db.relationship('Bookmark', backref='bookmark', lazy=True, cascade="")
    comments: relationship = db.relationship('Comment', backref='comment', lazy=True, cascade=delete_all)

    @override
    def insert(self) -> Union[Exception, None]:
        """
            This function inserts a new user into a database and a CSV file, and rolls back the changes if an error occurs.
        """
        try:

            latest_csv_id: int = get_latest_csv_user_id()

            user_ids_csv.insert_row({
                "user_id" : latest_csv_id
            })

            self.csv_id: int = latest_csv_id

            db.session.add(self)
            db.session.commit()

        except SQLAlchemyError as error:

            print(str(error))
            remove_csv_user_id(self.csv_id)
            raise error

    @override
    def delete(self):
        """
            The `delete` method deletes a user from the database and csv file, removes their profile picture if it exists
            and if its not the default picture, and commits the changes to the database.
        """
        user_ids_csv.delete_row({
            "column_name" : "user_id",
            "column_data" : self.csv_id
        })

        # Delete the image if it exists and if the profile picture isn't the default profile picture
        if self.profile_picture and self.profile_picture != "default.jpg":
            image_path: str = os.path.join(current_app.static_folder, 'profile_pictures', self.profile_picture)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(self)
        db.session.commit()

    @override
    def __repr__(self) -> str:
        return pretty_print(self.table_name, self.fields)

class Bookmark(db.Model):
    __tablename__ = 'bookmark'

    id: int = db.Column(db.Integer, primary_key=True)
    movie_csv_id: int = db.Column(db.Integer, nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    @override
    def __repr__(self) -> str:
        return pretty_print(self.table_name, self.fields)

class Comment(db.Model):
    __tablename__ = 'comment'

    id: int = db.Column(db.Integer, primary_key=True)
    content: str = db.Column(db.Text, nullable=False)
    csv_id: int = db.Column(db.Integer, nullable=False)
    movie_csv_id: int = db.Column(db.Integer, nullable=False)
    user_csv_id: int = db.Column(db.Integer, db.ForeignKey('user.csv_id', ondelete='CASCADE'), nullable=False)

    @override
    def update(self, new_comment: str) -> Union[Exception, None]:
        """
        The function updates a comment in a CSV file and in a database.

        Args:
            new_comment: The `new_comment` parameter is the updated content of the comment that needs to be
            updated in the database.
        """
        comments_csv.update({
            "column_name": "comment_id",
            "column_data": self.csv_id
        }, {
            "content" : new_comment
        })

        self.content: str = new_comment
        db.session.commit()

    @override
    def insert(self) -> Union[Exception, None]:
        """
            The `insert` function inserts a comment into a CSV file and a database, along with its sentiment score.
        """
        try:

            comment_id: int = get_latest_csv_comment_id()
            comment: TextBlob = TextBlob(self.content)
            comment_polarity: float = comment.sentiment.polarity

            comments_csv.insert_row({
                "user_id": self.user_csv_id,
                "comment_id": comment_id,
                "movie_id": self.movie_csv_id,
                "sentiment_score": comment_polarity
            })

            self.csv_id: int = comment_id

            db.session.add(self)
            db.session.commit()

        except SQLAlchemyError as error:
            remove_csv_comment_id(self.csv_id)
            raise error

    @override
    def delete(self) -> Union[Exception, None]:
        """
        Deletes the row data from the csv file first before removing the comment from the database
        """
        comments_csv.delete_row({
            "column_name": "comment_id",
            "column_data": self.csv_id
        })

        db.session.delete(self)
        db.session.commit()

    @override
    def __repr__(self):
        return pretty_print(self.table_name, self.fields)

from Engine.recommender.playground import test_csv_alchemy
from pandas import Series, read_csv, DataFrame, concat
from typing import Any, Dict, Union
from os import path
import json


SEARCH = Dict[str, Any]

class CsvAlchemy:

    class ValidationException(Exception):
        pass

    class InsertionException(Exception):
        pass

    class RowNotFoundException(Exception):
        pass

    def __init__(self, filename) -> None:
        """
        Initializes a CSV_Alchemy instance.

        for example::

            csv_instance = CSV_Alchemy("file.csv")

        Args:
        -----
            filename (str): The name of the CSV file.
        """
        self.filename: str = filename
        self.filepath: str = self._get_csv(filename)
        self.csv_data: DataFrame = read_csv(self.filepath)
        self.columns: Union[list[str], list[None]] = list(self.csv_data.columns) if not self.csv_data.columns.empty else []

    def __str__(self) -> str:
        """
        Returns a string representation of the first 6 rows of the CSV data.

        for example::

            print(csv_instance)

        Returns:
        --------
            str: String representation of data.
        """
        return str(self.csv_data.head(6))

    def _get_csv(self, filename: str) -> str:
        """
        Returns the absolute path to a CSV file in the "Engine/recommender/dataset" directory.

        Args:
        -----
            filename (str): The name of the CSV file.

        Returns:
        --------
            str: The absolute file path.
        """
        return path.abspath(f"dataset/{filename}")

    def _validate_data(self, search_dictionary) -> Union[Exception, None]:
        """
        Validates a search dictionary for correctness.

        Args:
        -----
            search_dictionary (dict): Dictionary containing search parameters.

        Raises:
        -------
            Exception: If any validation condition is not met or none if passes.
        """
        json_dictionary = json.dumps(search_dictionary, indent=4)

        if "column_name" not in search_dictionary:
            raise self.ValidationException(f"Missing or wrong 'column_name' for the following data {json_dictionary}")

        if "column_data" not in search_dictionary:
            raise self.ValidationException(f"Missing or wrong 'column_data' for the following data {json_dictionary}")

        if str(search_dictionary["column_name"]).strip() == '':
            raise self.ValidationException(f"'column_name' cannot be empty for the following data {json_dictionary}")

        if str(search_dictionary["column_data"]).strip() == '':
            raise self.ValidationException(f"'column_data' cannot be empty for the following data {json_dictionary}")

        if search_dictionary["column_name"] not in self.columns:
            raise self.ValidationException(f"The following column_name {search_dictionary['column_name']} is not among this csv file's columns -> {', '.join(self.columns)}")

    def insert_row(self, data_dictionary: Dict[str, Union[str, Any]]) -> Union[SEARCH, Exception]:
        """
        Inserts a new row of data into the CSV file.

        for example::

            data_to_insert = {
                "user_id": 1,
                "movie_id": 244,
                "rating": 3.7
            }

            result = csv_instance.insert_row(data_to_insert)
            # { "user_id": 1,  "movie_id": 244,  "rating": 3.7, ... other column : data }
        Args:
        -----
            data_dictionary (dict): Dictionary containing data to be inserted.

        Raises:
        -------
            Exception: If the data insertion fails.

        Returns:
        --------
            The row as a dictionary.
        """

        for column_name in data_dictionary:
            if column_name not in self.columns:
                raise self.InsertionException(f"Column '{column_name}' does not exist in the CSV file '{self.filename}'")

        try:
            new_data: DataFrame = DataFrame(data_dictionary, index=[0])
            self.csv_data: DataFrame = concat([self.csv_data, new_data], ignore_index=True)
            self.csv_data.to_csv(self.filepath, index=False)
            inserted_row: SEARCH = new_data.to_dict(orient='records')[0]
            return inserted_row
        except Exception as error:
            raise self.InsertionException(f"Failed to insert new data into CSV file: {str(error)}")

    def _retrieve(self, search_dictionary: SEARCH) -> Union[Series, Exception]:
        """
        Retrieves data from the CSV file based on search criteria.

        Args:
        -----
            search_dictionary (dict): Dictionary containing search parameters.

        Returns:
        --------
            DataFrame: DataFrame with retrieved data.

        Raises:
        -------
            Exception: If retrieval fails.
        """
        self._validate_data(search_dictionary)

        column_data: Series = self.csv_data[search_dictionary["column_name"]]
        input_data: str = search_dictionary["column_data"]

        try:
            input_data: int = int(input_data)
        except ValueError:
            pass

        row: Series = self.csv_data[column_data == input_data]

        if row.empty:
            search_query: str = json.dumps(search_dictionary, indent=4)
            raise self.RowNotFoundException(f"Row search by the following values {search_query} is empty")

        return row

    def clean_retrieve(self, search_dictionary: SEARCH) -> Series:
        """
        Retrieves data from the CSV file based on search criteria and returns a clean response.

        for example::

            search_criteria = {
                "column_name": "user_id",
                "column_data": 7
            }

            result = csv_instance.clean_retrieve(search_criteria)
            # { "user_id": 7, ... other column : data }

        Args:
        -----
            search_dictionary (dict): Dictionary containing search parameters.

        Returns:
        --------
            dict: Dictionary with retrieved data.

        Raises:
        -------
            RowNotFoundException: If search dictionary does not return any rows.
        """
        retrieved_data: DataFrame = self._retrieve(search_dictionary)

        row: Series = retrieved_data.to_dict(orient='records')[0]
        return row

    def delete_row(self, search_dictionary: SEARCH) -> Union[Exception, None]:
        """
        Deletes a row from the CSV file based on search criteria.

        For example::

            search_criteria = {
                "column_name": "user_id",
                "column_data": 12
            }

            csv_instance.delete_row(search_criteria)

        Args:
        ----
            search_dictionary (dict): Dictionary containing search parameters.

        Raises:
        -------
            RowNotFoundException: If search dictionary does not return any rows.
        """
        row_to_delete: Series = self._retrieve(search_dictionary)

        self.csv_data: DataFrame = self.csv_data.drop(row_to_delete.index)
        self.csv_data.to_csv(self.filepath, index=False)

    def update(self, row_search_dictionary: SEARCH, data_dictionary: SEARCH) -> Union[Exception, None]:
        """
        Updates a row in the CSV file based on search criteria.

        for example::

            new_comment: str = "Sorry about that"

            search_criteria: Dict[str, Any] = {
                "column_name": "comment_id",
                "column_data": 26
            }\n
            update_data: Dict[str, Any] = {
                "content": new_comment,
                "sentiment_score": TextBlob(new_comment).sentiment.polarity
            }

            csv_instance.update(search_criteria, update_data)

        Args:
        ----
            row_search_dictionary (dict): Dictionary containing search parameters for the row to be updated.
            data_dictionary (dict): Dictionary containing the updated data.

        Raises:
        -------
            Exception: If update fails.
        """
        row_to_update: DataFrame = self._retrieve(row_search_dictionary)

        updated_index: int = row_to_update.index[0]

        for key, value in data_dictionary.items():
            self.csv_data.at[updated_index, key] = value

        self.csv_data.to_csv(self.filepath, index=False)

user_ids: CsvAlchemy = CsvAlchemy("user_ids.csv")
comments: CsvAlchemy = CsvAlchemy("comments.csv")
ratings: CsvAlchemy = CsvAlchemy("ratings.csv")
movies: CsvAlchemy = CsvAlchemy("movies.csv")
names: CsvAlchemy = CsvAlchemy("names.csv")

if __name__ == "__main__":
    test_csv_alchemy(names)

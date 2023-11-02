from typing import Any, Callable, Dict, List
from .csv_alchemy import CsvAlchemy, names
from pandas import Series

BASIC_DICTIONARY = Dict[str, Any]

def clear() -> None:
    """
    The `clear()` function clears the console screen.
    """
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def prompt() -> bool:
    """
    The function `prompt` asks the user to input 'Y' or 'N' and returns True if the input is 'Y' and
    False if the input is 'N'.
    
    Returns:
    -------
        The function `prompt()` returns a boolean value. It returns `True` if the user's decision is 'Y'
        (indicating they want to proceed), and `False` if the user's decision is 'N' (indicating they do not want to proceed).
    """
    while True:
        decision: str = input("\n\tProceed? Y or N: ")
        if decision not in ["Y", "N"]:
            print("\n\tChoose between Y or N only")
            continue
        return decision == 'Y'

def show_current_csv_data(csv_instance: CsvAlchemy) -> None:
    """
    The function `show_current_csv_data` displays the current data in a CSV instance.
    
    Args:
    -----
        csv_instance: The `csv_instance` parameter is an instance of a CSV object. It represents a CSV
        file and contains the data stored in the file.
    """
    clear()
    print(f"\n{csv_instance.csv_data}\n")

def create_insert_data(csv_instance: CsvAlchemy) -> BASIC_DICTIONARY:
    """
    The function `create_insert_data` takes a CSV instance as input and prompts the user to enter
    values for each column, then returns a dictionary with column names as keys and user input as
    values.
    
    Args:
    -----
        csv_instance: The parameter `csv_instance` is expected to be an instance of a CSV file. It is
        assumed that the CSV file has columns that can be used as keys in the query dictionary.
    
    Returns:
    -------
      a dictionary with column names as keys and user-inputted values as values.
    """
    query_dictionary: BASIC_DICTIONARY = {}
    for column in csv_instance.columns:
        value: str = input(f"\n\tEnter {column}: ")
        query_dictionary[column] = value
    return query_dictionary

def create_search_criteria_for(purpose: str) -> BASIC_DICTIONARY:
    """
    The function `create_search_criteria_for` takes a purpose as input and returns a dictionary with a
    column name and column data based on user input.
    
    Args:
    -----
        purpose (str): The purpose parameter is a string that represents the purpose of the search
        criteria. It is used to provide a description or context for the search criteria being created.
    
    Returns:
    --------
        a dictionary with two key-value pairs. The keys are "column_name" and "column_data", and the
        values are obtained from user input prompts.
    """

    search_dictionary = {}

    while True:

        column_name = input(f"\n\tEnter column name for {purpose}: ")

        while column_name == '':
            print("\n\tColumn name cannot be empty")
            column_name = input(f"\n\tEnter column name for {purpose}: ")

        search_dictionary[column_name] = input(f"\n\tEnter column data for {purpose}. May be empty: ")

        if not prompt():
            return search_dictionary

def watch(callback: Callable[[], None]) -> Callable[[], None]:
    """
    The `watch` function takes a callback function with no argument and return values as an argument 
    executes it and handles specific exceptions that may occur during execution.
    
    Args:
    -----
        callback: The `callback` parameter is a function that will be executed within the `watch`
        function. It is a way to pass a function as an argument to another function.
    
    Returns:
    --------
        The `watch` function returns the result of calling the `callback` function.
    """
    try:
        return callback()
    except CsvAlchemy.InsertionException as error:
        print(f"\n\t{str(error)}")
    except CsvAlchemy.RowNotFoundException:
        print("\n\tRow not found")
    except CsvAlchemy.ValidationException as error:
        print(f"\n\t{str(error)}")

def acquire_update_data(csv_instance: CsvAlchemy) -> BASIC_DICTIONARY:
    """
    The function `acquire_update_data` prompts the user to enter new data for each column in a CSV file
    and returns a dictionary containing the updated data.
    
    Args:
    -----
        csv_instance (CsvAlchemy): The `csv_instance` parameter is an instance of the `CsvAlchemy` class.
        This class represents a CSV file and provides methods to read and manipulate the data in the CSV
        file.
    
    Returns:
    --------
        a dictionary containing the updated data for the columns in the CSV file.
    """
    number_of_columns: int = len(csv_instance.columns)
    update_data: BASIC_DICTIONARY = {}
    
    for index in range(number_of_columns):
        column_name: str = csv_instance.columns[index]
        new_data: str = input(f"\n\tEnter new data for {column_name} (Enter to skip): ")

        if new_data.strip() != '':
            update_data[column_name] = new_data
    return update_data

def test_csv_alchemy(csv_instance: CsvAlchemy) -> None:
    """
    The function `test_csv_alchemy` provides a menu-driven interface to interact with a `CsvAlchemy`
    object, allowing the user to insert, retrieve, update, or delete data from a CSV file.
    
    Args:
    -----
        csv_instance (CsvAlchemy): The `csv_instance` parameter is an instance of the `CsvAlchemy` class.
        It is used to perform operations on a CSV file, such as inserting, retrieving, updating, and
        deleting data.
    """

    options: List[str] = ["\n\n\t1. Insert", "\n\t2. Retrieve", "\n\t3. Update", "\n\t4. Delete", "\n\t5. Exit"]
    
    while True:

        try:

            choice: int = int(input(f"\n\tEnter a number (1-4) to choose a method\n{''.join(options)}\n\n\tChoice: "))
            
            if 1 <= choice <= 5:
                
                show_current_csv_data(csv_instance)
                
                def process_insertion() -> None:
                    """
                    The function "process_insertion" inserts a row of data into a CSV file and prints
                    the inserted row.
                    """
                    data_to_insert: BASIC_DICTIONARY = create_insert_data(csv_instance)
                    inserted_row: BASIC_DICTIONARY = csv_instance.insert_row(data_to_insert)
                    print(f"\n\tInserted row: {inserted_row}")
                                                        
                def process_retrieval() -> None:
                    """
                    The function "process_retrieval" retrieves and prints cleaned data based on search
                    criteria.
                    """
                    search_criteria: BASIC_DICTIONARY = create_search_criteria_for("retrieve")
                    retrieved_data: Series = csv_instance.clean_retrieve(search_criteria)
                    print(f"\n\tRetrieved data: {retrieved_data}")

                def process_update() -> None:
                    """
                    The function "process_update" updates a row in a CSV file based on search criteria
                    and prints a confirmation message.
                    """
                    search_criteria: BASIC_DICTIONARY = create_search_criteria_for("update")
                    update_data: BASIC_DICTIONARY = acquire_update_data(csv_instance)

                    csv_instance.update(search_criteria, update_data)
                    print("\n\tRow updated.")
                
                def process_deletion() -> None:
                    """
                    The function "process_deletion" deletes a row from a CSV file based on a search
                    criteria.
                    """
                    search_criteria: BASIC_DICTIONARY = create_search_criteria_for("delete")
                    csv_instance.delete_row(search_criteria)
                    print("\n\tRow deleted.")
                
                def process_exit() -> None:
                    """
                    The function "process_exit" prints a message and exits the program.
                    """
                    print("\n\tExiting the program.\n")
                    exit(0)
            
                processes: List[Callable[[], None]] = [
                    process_insertion, 
                    process_retrieval, 
                    process_update, 
                    process_deletion, 
                    process_exit
                ]

                watch(processes[choice - 1])

            else:
                print("\n\tInvalid input. Please enter a number between 1 and 5.")
            
            if not prompt():
                clear()
                break
            
            clear()
        
        except ValueError:
            print("\n\tInvalid input. Please enter a valid number.")

if __name__ == "__main__":
    test_csv_alchemy(names)
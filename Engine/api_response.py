from typing import Dict, Union

from flask import jsonify

FAILED = "failed"
SUCCESS = "success"

# This indicates that the function will return a dictionary where the key is of type 'str' and its value may be of type 'str' or None
RouteResponseType = Dict[str, Union[str, None]]

class RouteResponse:
    """
        The `RouteResponse` class provides static methods to generate custom api response 
        dictionary with a status, data, and message.
    """
    
    @staticmethod
    def success(message="", data=None) -> RouteResponseType:
        """
        The `success` function returns a dictionary with a success status, optional data, and an optional
        message.
        
        Args:
        -----
            message: The message parameter is an optional string that represents a success message. 
                It can be used to provide additional information or context about the success status.
            
            data: The `data` parameter is used to pass any additional data that needs to be returned along with the success response.
                It can be any type of data, such as a dictionary, list, string, etc.
        
        Returns:
        --------
            A Jsonfied dictionary is being returned with three key-value pairs: 
            "status" with the value of "success", 
            "data" with the value of the data parameter (which can be None), 
            "message" with the value of the message parameter (which can be an empty string).
        """
        return jsonify({"status": SUCCESS, "body": data, "message": message})

    @staticmethod
    def failed(message="", data=None) -> RouteResponseType:
        """
        The above function returns a dictionary with a status, data, and message.
        
        Args:
        -----
            message: The "message" parameter is a string that represents an optional error message. 
                It can be used to provide additional information about the failure.

            data: The `data` parameter is an optional parameter that can be used to pass additional data along with the response. 
                It can be any type of data, such as a dictionary, list, string, etc.
        
        Returns:
        --------
            A Jsonfied  dictionary is being returned with three key-value pairs: 
            "status" with the value of "failed", 
            "data" with the value of the data parameter (which can be None), 
            "message" with the value of the message parameter (which can be an empty string).
        """
        return jsonify({"status": FAILED, "body": data, "message": message})
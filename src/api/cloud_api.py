import typing
import requests
import logging
import config
import json


METHOD_GET = "http_get"
METHOD_POST = "http_post"
METHOD_PUT = "http_put"
METHOD_DELETE = "http_delete"


class ApiResponse:
    """A class to handle API responses."""

    def __init__(self, response_code: int, response_body: str):
        """
        Initializes the ApiResponse object.
        Args:
            response_code (int): The HTTP response code.
            response_body (str): The HTTP response body.
        """
        self.response_code = response_code
        self.response_body = response_body

    def as_paginated_response(self):
        """
        Converts the response to a paginated response.
        Returns:
            dict: The paginated response.
        """
        try:
            response = json.loads(self.response_body)
            if not response.get("current_page"):
                return StdResponse(response)
            return PaginatedResponse(response)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON: {e}")
            raise


class StdResponse:
    """A class to handle standard API responses."""

    def __init__(self, pr: dict):
        if not pr:
            raise ValueError("Response cannot be None")
        self.data = pr["data"]


class PaginatedResponse:
    """A class to handle paginated API responses."""

    def __init__(self, pr: dict):
        if not pr:
            raise ValueError("Response cannot be None")
        self.data = pr["data"]
        self._page = pr["current_page"]
        self._first_page = pr["first_page"]
        self._last_page = pr["last_page"]
        self._prev_page = pr["prev_page"]
        self._next_page = pr["next_page"]
        self._total = pr["total"]


def __get_headers() -> dict:
    """
    Returns the headers for the API request.
    Returns:
        dict: The headers for the API request.
    """
    headers = {}
    headers["api-key"] = config.API_KEY
    headers["Content-Type"] = "application/json"

    return headers


def __call_api(
    method: str, url: str, headers: dict = None, payload: dict = None
) -> ApiResponse:
    """
    Calls the API with the specified method, URL, headers, and payload.
    Args:
        method (str): The HTTP method to use (GET, POST, PUT, DELETE).
        url (str): The URL to call.
        headers (dict): The headers for the request.
        payload (dict): The payload for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    if headers is None:
        headers = __get_headers()
    if payload is None:
        payload = {}

    try:
        if method == METHOD_GET:
            response = requests.get(url, headers=headers)
        elif method == METHOD_POST:
            response = requests.post(url, headers=headers, json=payload)
        elif method == METHOD_PUT:
            response = requests.put(url, headers=headers, json=payload)
        elif method == METHOD_DELETE:
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        logging.debug(
            f"API call to {url} with method {method} returned status code {response.status_code}"
        )

        return ApiResponse(response.status_code, response.text)
    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        raise


def form_url_endpoint(endpoint: str) -> str:
    """
    Forms the full URL for the API endpoint.
    Args:
        endpoint (str): The API endpoint.
    Returns:
        str: The full URL for the API endpoint.
    """
    return f"{config.API_BASE_URL}/{endpoint}"


def api_get(endpoint: str, headers: dict = None) -> ApiResponse:
    """
    Calls the API with the GET method.
    Args:
        endpoint (str): The API endpoint.
        headers (dict): The headers for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    url = form_url_endpoint(endpoint)
    return __call_api(METHOD_GET, url, headers=headers)


def api_post(endpoint: str, payload: dict, headers: dict = None) -> ApiResponse:
    """
    Calls the API with the POST method.
    Args:
        endpoint (str): The API endpoint.
        payload (dict): The payload for the request.
        headers (dict): The headers for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    url = form_url_endpoint(endpoint)
    return __call_api(METHOD_POST, url, headers=headers, payload=payload)


def api_put(endpoint: str, payload: dict, headers: dict = None) -> ApiResponse:
    """
    Calls the API with the PUT method.
    Args:
        endpoint (str): The API endpoint.
        payload (dict): The payload for the request.
        headers (dict): The headers for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    url = form_url_endpoint(endpoint)
    return __call_api(METHOD_PUT, url, headers=headers, payload=payload)


def api_delete(endpoint: str, headers: dict = None) -> ApiResponse:
    """
    Calls the API with the DELETE method.
    Args:
        endpoint (str): The API endpoint.
        headers (dict): The headers for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    url = form_url_endpoint(endpoint)
    return __call_api(METHOD_DELETE, url, headers=headers)

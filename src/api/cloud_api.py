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
        self.data = pr["data"]  # depends on the API response structure
        self._page = pr["current_page"]
        self._first_page = pr["first_page"]
        self._last_page = pr["last_page"]
        self._prev_page_url = pr[
            "prev_page_url"
        ]  # depends on the API response structure
        self._next_page_url = pr[
            "next_page_url"
        ]  # depends on the API response structure

        self._first_url = pr["first_page_url"]  # depends on the API response structure
        self._next_url = pr["next_page_url"]  # depends on the API response structure

    def _set_data_from_new_reponse(self, pr: dict):
        """
        Sets the data from a new response.
        Args:
            pr (dict): The new response data.
        """
        if not pr:
            raise ValueError("Response cannot be None")
        self.data = pr["data"]
        self._page = pr["current_page"]
        self._first_page = pr["first_page"]
        self._last_page = pr["last_page"]
        self._prev_page_url = pr["prev_page_url"]
        self._next_page_url = pr["next_page_url"]
        self._first_url = pr["first_page_url"]
        self._next_url = pr["next_page_url"]

    def has_next_page(self) -> bool:
        """
        Checks if there is a next page.
        Returns:
            bool: True if there is a next page, False otherwise.
        """
        return self._page < self._last_page

    def has_prev_page(self) -> bool:
        """
        Checks if there is a previous page.
        Returns:
            bool: True if there is a previous page, False otherwise.
        """
        return self._page < self._first_page

    def go_next_page(self):
        """
        Returns the next page number.
        Returns:
            int: The next page number.
        """
        if self._page >= self._last_page:
            raise IndexError("No next page available")
        r = api_get(self._next_page_url)
        if r.response_code != 200:
            raise ValueError(
                f"Failed to get next page: {r.response_code} - {r.response_body}"
            )
        json_data = json.loads(r.response_body)
        self._set_data_from_new_reponse(json_data)

    def go_prev_page(self):
        """
        Returns the previous page number.
        Returns:
            int: The previous page number.
        """
        if self._page <= self._first_page:
            raise IndexError("No previous page available")
        r = api_get(self._prev_page_url)
        if r.response_code != 200:
            raise ValueError(
                f"Failed to get previous page: {r.response_code} - {r.response_body}"
            )
        json_data = json.loads(r.response_body)
        self._set_data_from_new_reponse(json_data)

    def go_first_page(self):
        """
        Returns the first page number.
        Returns:
            int: The first page number.
        """
        r = api_get(self._first_url)
        if r.response_code != 200:
            raise ValueError(
                f"Failed to get first page: {r.response_code} - {r.response_body}"
            )
        json_data = json.loads(r.response_body)
        self._set_data_from_new_reponse(json_data)

    def go_last_page(self):
        """
        Returns the last page number.
        Returns:
            int: The last page number.
        """
        r = api_get(self._next_url)
        if r.response_code != 200:
            raise ValueError(
                f"Failed to get last page: {r.response_code} - {r.response_body}"
            )
        json_data = json.loads(r.response_body)
        self._set_data_from_new_reponse(json_data)


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

    response_code = response.status_code
    response_text = response.text

    logging.debug(
        f"API call to {url} with method {method} returned status code {response.status_code}"
    )
    return ApiResponse(response_code, response_text)


def form_url_endpoint(endpoint: str) -> str:
    """
    Forms the full URL for the API endpoint.
    Args:
        endpoint (str): The API endpoint.
    Returns:
        str: The full URL for the API endpoint.
    """
    return f"{config.API_BASE_URL}/{endpoint}"


def api_get(endpoint: str) -> ApiResponse:
    """
    Calls the API with the GET method.
    Args:
        endpoint (str): The API endpoint.
        headers (dict): The headers for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    url = form_url_endpoint(endpoint)
    headers = __get_headers()
    return __call_api(METHOD_GET, url, headers=headers)


def api_post(endpoint: str, payload: dict) -> ApiResponse:
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
    headers = __get_headers()
    return __call_api(METHOD_POST, url, headers=headers, payload=payload)


def api_put(endpoint: str, payload: dict) -> ApiResponse:
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
    headers = __get_headers()
    return __call_api(METHOD_PUT, url, headers=headers, payload=payload)


def api_delete(endpoint: str) -> ApiResponse:
    """
    Calls the API with the DELETE method.
    Args:
        endpoint (str): The API endpoint.
        headers (dict): The headers for the request.
    Returns:
        ApiResponse: The response from the API.
    """
    url = form_url_endpoint(endpoint)
    headers = __get_headers()
    return __call_api(METHOD_DELETE, url, headers=headers)

import typing
import datetime
import logging
import pytz
import config


def cache_fetch_by_id(cache_key: str, target_id, cache: typing.Dict):
    """
    Fetches an item from the cache by its ID.

    Args:
        cache_key (str): The key under which the item is stored in the cache.
        target_id: The ID of the item to fetch.
        cache (typing.Dict): The cache dictionary.

    Returns:
        The item if found, otherwise None.
    """
    if target_id in cache.get(cache_key, {}):
        return cache[cache_key][target_id]
    return None


def cache_object_by_id(cache_key: str, cache: typing.Dict, objects: typing.List):
    """
    Caches a list of objects by their IDs.

    Args:
        cache_key (str): The key under which to store the objects in the cache.
        cache (typing.Dict): The cache dictionary.
        objects (typing.List): The list of objects to cache.

    Returns:
        None
    """
    if cache_key not in cache:
        cache[cache_key] = {}
    for obj in objects:
        cache[cache_key][obj.id] = obj


def posix_timestamp_to_localtime(posix_timestamp: int) -> datetime.datetime:
    """
    Converts a POSIX timestamp to local time.

    Args:
        posix_timestamp (int): The POSIX timestamp to convert.

    Returns:
        datetime.datetime: The local time.
    """
    tz_utc = pytz.utc
    tz_local = pytz.timezone(config.LOCAL_TIMEZONE)  # Replace with your local timezone
    return datetime.datetime.fromtimestamp(posix_timestamp, tz_utc).astimezone(tz_local)


def handle_response(
    response: typing.Dict,
    action_description: str,
    http_method: str,
    success_codes: typing.List[int],
) -> typing.Dict[int, str]:
    """
    Handles the API response.

    Args:
        response (typing.Dict): The API response.
        response_code (int): The HTTP response code.
        response_body (str): The HTTP response body.
        cache_key (str): The key under which to store the objects in the cache.
        cache (typing.Dict): The cache dictionary.

    Returns:
        None or the object if found.
    """
    response_code = (
        response.response_code if hasattr(response, "response_code") else response_code
    )
    if response_code in success_codes:
        logging.info(
            f"Action '{action_description}' completed successfully with response code {response_code}."
        )
    if not response:
        logging.error("Response is None")
        return None
    if not isinstance(response, dict):
        logging.error("Response is not a dictionary")
        return None
    if not isinstance(response_code, int):
        logging.error("Response code is not an integer")
        return None

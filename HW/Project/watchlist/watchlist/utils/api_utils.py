import logging
import os
import requests
from dotenv import load_dotenv

#PLAYLIST VERSION // NOT EDITED

from utils.logger import configure_logger


RANDOM_ORG_BASE_URL = os.getenv("RANDOM_ORG_BASE_URL",
                                "https://www.random.org/integers/?num=1&min=1&col=1&base=10&format=plain&rnd=new")


logger = logging.getLogger(__name__)
configure_logger(logger)


def get_random(max: int) -> int:
    """
    Fetches a random integer between 1 and max inclusive from random.org.

    Args:
        max (int): The upper bound (inclusive) for the random number.

    Returns:
        int: A random number between 1 and max.

    Raises:
        RuntimeError: If the request to random.org fails.
        ValueError: If the response from random.org is not a valid integer.
    """
    if max < 1:
        raise ValueError("max must be at least 1")

    # Construct the full URL dynamically
    url = f"{RANDOM_ORG_BASE_URL}&max={max}"

    try:
        # Log the request to random.org
        logger.info(f"Fetching random number from {url}")

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        random_number_str = response.text.strip()

        try:
            random_number = int(random_number_str)
        except ValueError:
            logger.error(f"Invalid response from random.org: {random_number_str}")
            raise ValueError(f"Invalid response from random.org: {random_number_str}")

        logger.info(f"Received random number: {random_number}")
        return random_number

    except requests.exceptions.Timeout:
        logger.error("Request to random.org timed out.")
        raise RuntimeError("Request to random.org timed out.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to random.org failed: {e}")
        raise RuntimeError(f"Request to random.org failed: {e}")


def validate_string(value) -> bool:
    """
    Ensures that the passed in variable is a string.

    Args:
        value (any): Value that will be checked to see if it is a string or not

    Returns:
        bool: Whether or not the value was a string or not.

    """
    if isinstance(value, str):
        return True
    else:
        return False

def get_api_key() -> str:
    """
    Gets the api-key for TMDB database from a .env file and returns it.

    Returns:
        API_KEY (str): The api-key if found in the .env file.

    Raises:
        RuntimeError: If there is no set API_KEY value or no .env file.
    """
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        raise RuntimeError("API_KEY for TMDB not set in environment")
    return API_KEY

def api_get_movie_by_title(title: str):
    """
    Queries the TMDB for a movie by title.

    Args:
        title (str): The title of the movie.

    Returns:
        raw_movie_data (any): A dictionary that stores the movie information.

    Raises:
        ValueError: If the title is not inputted as a str or if the movie is not found in the TMDB.
    """
    url = "https://api.themoviedb.org/3/search/movie"

    if validate_string(title):
        query = title
    else:
        raise ValueError("Movie title must be inputted as a String!")

    params = {
        "query": query,
        "page": 1,
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {get_api_key()}"
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    num_responses = data["total_results"]
    raw_movie_data = None
    if num_responses > 1:
        raw_movie_data = data["results"][0]
    else:
        raise ValueError("Movie with entered title does not exist in the database. ")
    return raw_movie_data


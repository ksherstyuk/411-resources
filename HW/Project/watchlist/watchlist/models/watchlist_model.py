import logging
import os
import time
import requests
from typing import List

from .movie_model import Movies
from ..utils.api_utils import get_random, api_get_movie_by_title
from ..utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WatchlistModel:
    """
    A class to manage a watchlist of movies.
    """

    def __init__(self):
        """Initializes the WatchlistModel with an empty watchlist.

        The watchlist is a list of Movies (that the user wants to watch).
        """
        self.watchlist: List[str] = []

    def _get_movie_from_tmdb(self, title: str) -> Movies:
        """
        Retrieves a movie by its title, using TMDB.

        Args:
            title (str): The unique title of the movie to retrieve.

        Returns:
            Movies: The movie object corresponding to the given title.

        Raises:
            ValueError: If the movie cannot be found in the database.
        """
        try:
            movie = Movies.get_movie_by_title(title)
            logger.info(f"Movie '{title}' loaded from TMDB")
        except ValueError as e:
            logger.error(f"Movie '{title}' not found in TMDB: {e}")
            raise ValueError(f"Movie '{title}' not found in TMDB") from e

        return movie

    def add_movie_to_watchlist(self, title: str) -> None:
        """
        Adds a movie to the watchlist by title, by querying the TMDB Api.

        Args:
            title (str): The name of the movie to add to the watchlist.

        Raises:
            ValueError if non-string title is entered or movie title is not found in TMDB database.
        """
        logger.info(f"Received request to add movie '{title}' to the watchlist")

        title = self.validate_movie_title(title)

        if title in self.watchlist:
            logger.error(f"Movie called '{title}' already exists in the watchlist")
            raise ValueError(f"Movie called '{title}' already exists in the watchlist")

        try:
            new_movie = self._get_movie_from_tmdb(title)
        except ValueError:
            logger.info(f"Movie '{title}' not found in DB. Fetching from TMDB API.")
            raw_movie_data = api_get_movie_by_title(title)
            if not raw_movie_data:
                logger.error(f"Movie '{title}' not found in TMDB API")
                raise ValueError(f"Movie '{title}' not found in TMDB API")

            Movies.create_movie(
                title=raw_movie_data["title"],
                release_year=raw_movie_data["release_year"],
                runtime=raw_movie_data["runtime"],
                popularity=raw_movie_data["popularity"],
                average_rating=raw_movie_data["average_rating"],
            )
            new_movie = self._get_movie_from_tmdb(title)

        self.watchlist.append(new_movie.title)
        logger.info(
            f"Successfully added to watchlist: '{new_movie.title}' ({new_movie.release_year})"
        )

    def remove_movie_from_watchlist(self, title: str) -> None:
        """Removes a movie from the watchlist by its title.

        Args:
            title (str): The name of the movie to remove from the watchlist.

        Raises:
            ValueError: If the watchlist is empty or the movie title is invalid.
        """
        logger.info(f"Received request to remove movie '{title}'")

        self.check_if_empty()
        title = self.validate_movie_title(title)

        if title not in self.watchlist:
            logger.warning(f"Movie '{title}' not found in the watchlist")
            raise ValueError(f"Movie '{title}' not found in the watchlist")

        self.watchlist.remove(title)
        logger.info(f"Successfully removed movie '{title}' from the watchlist")

        try:
            movie_to_delete = Movies.get_movie_by_title(title)
            Movies.delete_movie(movie_to_delete.id)
            logger.info(f"Successfully deleted movie '{title}' from database")
        except ValueError as e:
            logger.error(f"Movie '{title}' could not be deleted from database: {e}")
            raise

    def clear_watchlist(self) -> None:
        """Clears all movies from the watchlist.

        Clears all movies from the watchlist. If the watchlist is already empty, logs a warning.
        """
        logger.info("Received request to clear the watchlist")

        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty watchlist")

        self.watchlist.clear()
        logger.info("Successfully cleared the watchlist")

    ##################################################
    # Watchlist Retrieval Functions
    ##################################################

    def get_all_movies(self) -> List[Movies]:
        """Returns a list of all movies in the watchlist using cached movie data.

        Returns:
            List[Movies]: A list of all movies in the watchlist.

        Raises:
            ValueError: If the watchlist is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving all movies in the watchlist")
        return [self._get_movie_from_tmdb(title) for title in self.watchlist]

    def get_watchlist_length(self) -> int:
        """Returns the number of movies in the watchlist.

        Returns:
            int: The total number of movies in the watchlist.
        """
        length = len(self.watchlist)
        logger.info(f"Retrieving watchlist length: {length} movies")
        return length

    def get_random_movie_from_watchlist(self) -> Movies:
        """Returns a randomly-selected movie from the watchlist.

        Returns:
            Movies: A randomly selected movie from the watchlist.

        Raises:
            ValueError: If the watchlist is empty.
        """
        self.check_if_empty()

        index = get_random(self.get_watchlist_length())
        selected_title = self.watchlist[index - 1]
        movie = self._get_movie_from_tmdb(selected_title)

        logger.info(
            f"Successfully retrieved random movie from watchlist: {movie.title} ({movie.release_year})"
        )
        return movie

    ##################################################
    # Utility Functions
    ##################################################

    def validate_movie_title(self, title: str) -> str:
        """
        Validates the given movie title.

        Args:
            title (str): The movie title to validate.

        Returns:
            str: The validated movie title.

        Raises:
            ValueError: If the movie title is not a string.
        """
        try:
            if not isinstance(title, str):
                raise ValueError
        except ValueError:
            logger.error(f"Invalid movie title: {title}")
            raise ValueError(f"Invalid movie title: {title}")

        return title

    def check_if_empty(self) -> None:
        """
        Checks if the watchlist is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the watchlist is empty.
        """
        if not self.watchlist:
            logger.error("Watchlist is empty")
            raise ValueError("Watchlist is empty")

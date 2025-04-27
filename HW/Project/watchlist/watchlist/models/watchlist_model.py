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
        self.watchlist: List[int] = []

    ##################################################
    # Movie Management Functions
    ##################################################


    def _get_movie_from_tmdb(self, title: str) -> Movies: 
        """
        Retrieves a movie by its title, using TMDB

        Args:
            title (str): The unique title of the movie to retrieve.

        Returns:
            Movies: The movie object corresponding to the given ID.

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
        logger.info(
            f"Received request to add movie '{title}' to the watchlist"
        )

        title = self.validate_movie_title(title)

        if title in self.watchlist:
            logger.error(f"Movie called '{title}' already exists in the watchlist")
            raise ValueError(f"Movie called '{title}' already exists in the watchlist")
        
        try:
            new_movie = self._get_movie_from_tmdb(title)
        except ValueError as e:
            logger.error(f"Failed to add movie: {e}")
            raise

        self.watchlist.append(movie.title)
        logger.info(f"Successfully added to watchlist: '{movie.title}' ({movie.release_year})")

        # create instance in the database now -- more logic necessary... do i use the cls thing?

    def remove_movie_from_watchlist(self, title: str) -> None:
        """Removes a movie from the watchlist by its title.

        Args:
            title (str): The name of the movie to remove from the watchlist.

        Raises:
            ValueError: If the watchlist is empty or the movie ID is invalid.

        """
        logger.info(f"Received request to remove movie '{title}'")

        self.check_if_empty()
        title = self.validate_movie_title(title)

        if title not in self.watchlist:
            logger.warning(f"Movie '{title}' not found in the watchlist")
            raise ValueError(f"Movie '{title}' not found in the watchlist")

        self.watchlist.remove(movie.title)
        logger.info(f"Successfully removed movie '{title}' from the watchlist")

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

    def get_all_movies(self) -> List[Movies]: #YES
        """Returns a list of all movies in the watchlist using cached movie data.

        Returns:
            List[Movies]: A list of all songs in the watchlist.

        Raises:
            ValueError: If the watchlist is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving all movies in the watchlist")
        return [
            self._get_movie_from_tmdb(title) for title in self.watchlist
        ]

    def get_watchlist_length(self) -> int:
        """Returns the number of movies in the watchlist.

        Returns:
            int: The total number of movies in the watchlist.

        """
        length = len(self.watchlist)
        logger.info(f"Retrieving watchlist length: {length} movies")
        return length

    def get_random_movie_from_watchlist(self):
        """Returns a randomly-selected movie from the watchlist.

        Returns:
            Movie: The movie with the specified ID.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()

        # Get a random index using the random.org API
        movie_id_rand = get_random(self.get_watchlist_length()) 
        logger.info(
            f"Retrieving randomly-selected movie with ID {movie_id_rand} from the watchlist"
        )
        for movie_id, title in self.watchlist: ##REALLLYYY HACKKYYYY
            if movie_id == movie_id_rand:
                movie = Movie.get_movie_by_title(title)
        logger.info(
            f"Successfully retrieved random movie from watchlist: {movie.title} ({movie.release_year})"
        )
        return movie

    ##################################################
    # Utility Functions
    ##################################################

    ####################################################################################################
    #
    # Note: I am only testing these things once. EG I am not testing that everything rejects an empty
    # list as they all do so by calling this helper
    #
    ####################################################################################################

    def validate_movie_title(self, title: str) -> str:
        """
        Validates the given movie ID.

        Args:
            title (str): The movie title to validate.

        Returns:
            str: The validated movie title.

        Raises:
            ValueError: If the movie ID is not a string, or not found in the database.
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

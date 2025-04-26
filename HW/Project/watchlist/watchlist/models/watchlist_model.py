import logging
import os
import time
from typing import List

from watchlist.models.movie_model import Movies
from watchlist.utils.api_utils import get_random
from watchlist.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WatchlistModel:
    """
    A class to manage a watchlist of movies.

    """

    def __init__(self):
        """Initializes the WatchlistModel with an empty watchlist. 

        The watchlist is a list of Movies (that the user wants to watch).
        The TTL (Time To Live) for movie caching is set to a default value from the environment variable "TTL",
        which defaults to 60 seconds if not set.

        """
        #self.current_track_number = 1
        self.watchlist: List[int] = []
        self._movie_cache: dict[int, Movies] = {}
        self._ttl: dict[int, float] = {}
        self.ttl_seconds = int(os.getenv("TTL", 60))  # Default TTL is 60 seconds


    ##################################################
    # Movie Management Functions
    ##################################################

    def _get_movie_from_cache_or_db(self, movie_id: int) -> Movies:
        """
        Retrieves a movie by ID, using the internal cache if possible.

        This method checks whether a cached version of the movie is available
        and still valid. If not, it queries the database, updates the cache, and returns the movie.

        Args:
            movie_id (int): The unique ID of the movie to retrieve.

        Returns:
            Movies: The movie object corresponding to the given ID.

        Raises:
            ValueError: If the movie cannot be found in the database.
        """
        now = time.time()

        if movie_id in self._movie_cache and self._ttl.get(movie_id, 0) > now:
            logger.debug(f"Movie ID {movie_id} retrieved from cache")
            return self._movie_cache[movie_id]

        try:
            movie = Movies.get_movie_by_id(movie_id)
            logger.info(f"Movie ID {movie_ID} loaded from DB")
        except ValueError as e:
            logger.error(f"Movie ID {movie_ID} not found in DB: {e}")
            raise ValueError(f"Movie ID {movie_ID} not found in database") from e

        self._movie_cache[movie_id] = movie
        self._ttl[movie_id] = now + self.ttl_seconds
        return movie

    def add_movie_to_watchlist(self, movie_id: int) -> None:
        """
        Adds a movie to the watchlist by ID, using the cache or database lookup.

        Args:
            movie_id (int): The ID of the movie to add to the watchlist.

        Raises:
            ValueError: If the movie ID is invalid or already exists in the watchlist.
        """
        logger.info(f"Received request to add movie with ID {movie_id} to the watchlist")

        movie_id = self.validate_movie_id(movie_id, check_in_watchlist=False)

        if movie_id in self.watchlist:
            logger.error(f"Movie with ID {movie_id} already exists in the watchlist")
            raise ValueError(f"Movie with ID {movie_id} already exists in the watchlist")

        try:
            movie = self._get_movie_from_cache_or_db(movie_id)
        except ValueError as e:
            logger.error(f"Failed to add movie: {e}")
            raise

        self.watchlist.append(movie.id)
        logger.info(f"Successfully added to watchlist: {movie.title} ({movie.release_year})")


    def remove_movie_by_movie_id(self, movie_id: int) -> None:
        """Removes a movie from the watchlist by its movie ID.

        Args:
            movie_id (int): The ID of the movie to remove from the playlist.

        Raises:
            ValueError: If the watchlist is empty or the movie ID is invalid.

        """
        logger.info(f"Received request to remove movie with ID {movie_id}")

        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)

        if movie_id not in self.watchlist:
            logger.warning(f"Movie with ID {movie_id} not found in the watchlist")
            raise ValueError(f"Movie with ID {movie_id} not found in the watchlist")

        self.watchlist.remove(movie_id)
        logger.info(f"Successfully removed movie with ID {movie_id} from the watchlist")


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
            List[Movies]: A list of all songs in the watchlist.

        Raises:
            ValueError: If the watchlist is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving all movies in the watchlist")
        return [self._get_movie_from_cache_or_db(movie_id) for movie_id in self.watchlist]


    def get_movie_by_movie_id(self, movie_id: int) -> Movies:
        """Retrieves a movie from the playlist by its movie ID using the cache or DB.

        Args:
            movie_ID (int): The ID of the movie to retrieve.

        Returns:
            Movie: The movie with the specified ID.

        Raises:
            ValueError: If the watchlist is empty or the movie is not found.
        """
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        logger.info(f"Retrieving movie with ID {movie_id} from the watchlist")
        movie = self._get_movie_from_cache_or_db(movie_id)
        logger.info(f"Successfully retrieved movie: {movie.title} ({movie.release_year})")
        return movie

    def get_movie_by_title(self, title: str) -> Movies:
        """Retrieves a movie from the playlist by its title using the cache or DB.

        Args:
            title (str): The title of the movie to retrieve.

        Returns:
            Movie: The movie with the specified ID.

        Raises:
            ValueError: If the watchlist is empty or the movie is not found.
        """
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        logger.info(f"Retrieving movie with ID {movie_id} from the watchlist")
        movie = self._get_movie_from_cache_or_db(movie_id)
        logger.info(f"Successfully retrieved movie: {movie.title} ({movie.release_year})")
        return movie



    def get_watchlist_length(self) -> int:
        """Returns the number of movies in the watchlist.

        Returns:
            int: The total number of movies in the watchlist.

        """
        length = len(self.watchlist)
        logger.info(f"Retrieving watchlist length: {length} movies")
        return length


    def get_random_movie_from_watchlist(self) -> None:
        """Returns a randomly-selected movie from the watchlist.

        Returns:
            Movie: The movie with the specified ID.

        Raises:
            ValueError: If the playlist is empty.

        """
        self.check_if_empty()

        # Get a random index using the random.org API
        movie_ID = get_random(self.get_watchlist_length()) ## CHECK THIS LOGIC?????????
        logger.info(f"Retrieving randomly-selected movie with ID {movie_id} from the watchlist")
        movie = self._get_movie_from_cache_or_db(movie_id)
        logger.info(f"Successfully retrieved random movie from watchlist: {movie.title} ({movie.release_year})")
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

    def validate_movie_id(self, movie_id: int, check_in_watchlist: bool = True) -> int:
        """
        Validates the given movie ID.

        Args:
            movie_id (int): The movie ID to validate.
            check_in_watchlist (bool, optional): If True, verifies the ID is present in the watchlist.
                                                If False, skips that check. Defaults to True.

        Returns:
            int: The validated movie ID.

        Raises:
            ValueError: If the movie ID is not a non-negative integer,
                        not found in the watchlist (if check_in_watchlist=True),
                        or not found in the database.
        """
        try:
            movie_id = int(movie_id)
            if movie_id < 0:
                raise ValueError
        except ValueError:
            logger.error(f"Invalid movie id: {movie_id}")
            raise ValueError(f"Invalid movie id: {movie_id}")

        if check_in_watchlist and movie_id not in self.watchlist:
            logger.error(f"Movie with id {movie_id} not found in watchlist")
            raise ValueError(f"Movie with id {movie_id} not found in watchlist")

        try:
            self._get_movie_from_cache_or_db(movie_id)
        except Exception as e:
            logger.error(f"Movie with id {movie_id} not found in database: {e}")
            raise ValueError(f"Movie with id {movie_id} not found in database")

        return movie_id


    def check_if_empty(self) -> None:
        """
        Checks if the watchlist is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the watchlist is empty.

        """
        if not self.watchlist:
            logger.error("Watchlist is empty")
            raise ValueError("Watchlist is empty")

import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from watchlist.db import db
from watchlist.utils.logger import configure_logger
from watchlist.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class Movies(db.Model):
    """Represents a Movie in the catalog.

    This model maps to the 'movies' table and stores metadata such as
    title, release date, runtime, popularity, and average user rating (out of 10).

    Used in a Flask-SQLAlchemy application for watchlist management,
    user interaction, and data-driven movie operations.
    """

    __tablename__ = "Movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    runtime = db.Column(db.Integer, nullable=False) #in minutes?
    popularity = db.Column(db.Float, nullable=False)
    average_rating = db.Column(db.Float, nullable=False)

    def validate(self) -> None:
        """Validates the movie instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.
        """
        if not self.title or not isinstance(self.title, str):
            raise ValueError("Title must be a non-empty string.")
        if not isinstance(self.release_year, int) or self.release_year <= 1900:
            raise ValueError("Release year must be an integer greater than 1900.")
        if not isinstance(self.runtime, int) or self.duration <= 0:
            raise ValueError("Runtime (in minutes) must be a positive integer.")
        if not isinstance(self.popularity, float) or self.popularity <= 0:
            raise ValueError("Popularity must be a positive float.")
        if not isinstance(self.average_rating, float) or self.average_rating < 0 or self.average_rating > 10:
            raise ValueError("Average rating must be a float between 0 and 10.")

    @classmethod
    def create_movie(cls, title: str, release_year: int, runtime: int, popularity: float, average_rating: float) -> None:
        """
        Creates a new movie in the movies table using SQLAlchemy.

        Args:
            title (str): The movie title.
            release_year (int): The year the movie was released.
            runtime (int): The runtime of the movie in minutes.
            popularity (float): An unitless number representing the relative popularity of the movie.
            average_rating (float): The average rating of the movie by IMDB users, out of 10.

        Raises:
            ValueError: If any field is invalid or if a movie with the same compound key already exists.
            SQLAlchemyError: For any other database-related issues.
        """
        logger.info(f"Received request to create movie: {title} ({release_year})")

        try:
            movie = Movies(
                title=artist.strip(),
                release_year=release_year,
                runtime=runtime,
                popularity=popularity,
                average_rating=average_rating
            )
            movie.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            # Check for existing movie with same compound key (title, year)
            existing = Movies.query.filter_by(title=title.strip(), release_year=release_year).first()
            if existing:
                logger.error(f"Movie already exists: {title} ({release_year})")
                raise ValueError(f"Movie with title '{title}' and release year {release_year} already exists.")

            db.session.add(movie)
            db.session.commit()
            logger.info(f"Movie successfully added: {title} ({release_year}))")

        except IntegrityError:
            logger.error(f"Movie already exists: {title} ({release_year})")
            db.session.rollback()
            raise ValueError(f"Movie with title '{title}' and release year {release_year} already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating movie: {e}")
            db.session.rollback()
            raise

    @classmethod
    def delete_movie(cls, movie_id: int) -> None:
        """
        Permanently deletes a movie from the catalog by ID.

        Args:
            movie_id (int): The ID of the movie to delete.

        Raises:
            ValueError: If the movie with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete movie with ID {movie_id}")

        try:
            movie = cls.query.get(movie_id)
            if not movie:
                logger.warning(f"Attempted to delete non-existent movie with ID {movie_id}")
                raise ValueError(f"Movie with ID {movie_id} not found")

            db.session.delete(movie)
            db.session.commit()
            logger.info(f"Successfully deleted movie with ID {movie_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting movie with ID {movie_id}: {e}")
            db.session.rollback()
            raise

    @classmethod
    def get_movie_by_id(cls, movie_id: int) -> "Movies":
        """
        Retrieves a movie by its ID.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Returns:
            Movies: The movie instance corresponding to the ID.

        Raises:
            ValueError: If no movie with the given ID is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve movie with ID {movie_id}")

        try:
            movie = cls.query.get(movie_id)

            if not movie:
                logger.info(f"Movie with ID {movie_id} not found")
                raise ValueError(f"Movie with ID {movie_d} not found")

            logger.info(f"Successfully retrieved Movie: {title} ({release_year})")
            return movie

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving movie by ID {movie_id}: {e}")
            raise

    @classmethod
    def get_movie_by_title(cls, title: str) -> "Movies":
        """
        Retrieves a movie by its title.

        Args:
            title (str): The movie title.

        Returns:
            Movies: The movie instance corresponding to the title.

        Raises:
            ValueError: If no movie with the given title is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve movie with title '{title}'")

        try:
            movie = cls.query.get(title)

            if not movie:
                logger.info(f"Movie with title '{title}' not found")
                raise ValueError(f"Movie with title '{title}' not found")

            logger.info(f"Successfully retrieved Movie: {title} ({release_year})")
            return movie

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving movie by title '{title}': {e}")
            raise

    @classmethod
    def get_all_movies(cls, sort_by_average_rating: bool = False) -> list[dict]:
        """
        Retrieves all movies from the catalog as dictionaries.

        Args:
            sort_by_average_rating (bool): If True, sort the movies by rating in descending order.

        Returns:
            list[dict]: A list of dictionaries representing all movies with ratings.

        Raises:
            SQLAlchemyError: If any database error occurs.
        """
        logger.info("Attempting to retrieve all movies from the catalog")

        try:
            query = cls.query
            if sort_by_average_rating:
                query = query.order_by(cls.average_rating.desc())

            movies = query.all()

            if not movies:
                logger.warning("The movie catalog is empty.")
                return []

            results = [
                {
                    "id": movie.id,
                    "title": movie.title,
                    "release_year": movie.release_year,
                    "runtime": movie.runtime,
                    "popularity": movie.popularity,
                    "average_runtime": movie.average_runtime
                }
                for movie in movies
            ]

            logger.info(f"Retrieved {len(results)} movies from the catalog")
            return results

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving all movies: {e}")
            raise

    @classmethod
    def get_random_movie(cls) -> dict:
        """
        Retrieves a random movie from the catalog as a dictionary.

        Returns:
            dict: A randomly selected movie dictionary.
        """
        all_movies = cls.get_all_movies()

        if not all_movies:
            logger.warning("Cannot retrieve random movie because the movie catalog is empty.")
            raise ValueError("The movie catalog is empty.")

        index = get_random(len(all_movies))
        logger.info(f"Random index selected: {index} (total movies: {len(all_movies)})")

        return all_movies[index - 1]

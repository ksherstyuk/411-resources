import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from db import db
from utils.logger import configure_logger
from utils.api_utils import get_random

logger = logging.getLogger(__name__)
configure_logger(logger)


class Movies(db.Model):
    __tablename__ = "movies"

    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, primary_key=True, nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    runtime = db.Column(db.Integer, nullable=False)  # in minutes
    popularity = db.Column(db.Float, nullable=False)
    average_rating = db.Column(db.Float, nullable=False)

    def validate(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Title must be a non-empty string.")
        if not isinstance(self.release_year, int) or self.release_year <= 1900:
            raise ValueError("Release year must be an integer greater than 1900.")
        if not isinstance(self.runtime, int) or self.runtime <= 0:
            raise ValueError("Runtime (in minutes) must be a positive integer.")
        if not isinstance(self.popularity, (int, float)) or self.popularity <= 0:
            raise ValueError("Popularity must be a positive number.")
        if not isinstance(self.average_rating, (int, float)) or not (
            0 <= self.average_rating <= 10
        ):
            raise ValueError("Average rating must be a number between 0 and 10.")

    @classmethod
    def create_movie(
        cls,
        title: str,
        release_year: int,
        runtime: int,
        popularity: float,
        average_rating: float,
    ) -> None:
        logger.info(f"Received request to create movie: {title} ({release_year})")
        title_clean = title.strip()

        # Validate inputs
        try:
            movie = Movies(
                title=title_clean,
                release_year=release_year,
                runtime=runtime,
                popularity=popularity,
                average_rating=average_rating,
            )
            movie.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        # Prevent duplicates
        existing = Movies.query.filter_by(title=title_clean).first()
        if existing:
            msg = f"Movie with title '{title_clean}' and release year {release_year} already exists."
            logger.error(msg)
            raise ValueError(msg)

        # Insert
        try:
            db.session.add(movie)
            db.session.commit()
            logger.info(
                f"Movie successfully added: {movie.title} ({movie.release_year})"
            )
        except IntegrityError:
            db.session.rollback()
            msg = f"Movie with title '{title_clean}' and release year {release_year} already exists."
            logger.error(msg)
            raise ValueError(msg)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error while creating movie: {e}")
            raise

    @classmethod
    def delete_movie(cls, title: str) -> None:
        logger.info(f"Received request to delete movie with title '{title}'")

        try:
            movie = cls.query.get(title.strip())
            if not movie:
                msg = f"Movie with title '{title}' not found"
                logger.warning(msg)
                raise ValueError(msg)

            db.session.delete(movie)
            db.session.commit()
            logger.info(f"Successfully deleted movie with title '{title}'")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(
                f"Database error while deleting movie with title '{title}': {e}"
            )
            raise

    @classmethod
    def get_movie_by_title(cls, title: str) -> "Movies":
        """
        Retrieves a movie from the database by its title.

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
            movie = cls.query.filter_by(title=title.strip()).first()

            if not movie:
                logger.info(f"Movie with title '{title}' not found in database")
                raise ValueError(f"Movie with title '{title}' not found")

            logger.info(
                f"Successfully retrieved Movie: {movie.title} ({movie.release_year})"
            )
            return movie

        except SQLAlchemyError as e:
            logger.error(
                f"Database error while retrieving movie by title '{title}': {e}"
            )
            raise

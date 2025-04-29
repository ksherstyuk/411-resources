from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from config import ProductionConfig

from watchlist.db import db
from watchlist.models.movie_model import Movies
from watchlist.models.watchlist_model import WatchlistModel
from watchlist.models.user_model import Users
from watchlist.utils.logger import configure_logger


load_dotenv()


def create_app(config_class=ProductionConfig) -> Flask:
    """Create a Flask application with the specified configuration.

    Args:
        config_class (Config): The configuration class to use.

    Returns:
        Flask app: The configured Flask application.

    """
    app = Flask(__name__)
    configure_logger(app.logger)

    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(
            jsonify({"status": "error", "message": "Authentication required"}), 401
        )

    watchlist_model = WatchlistModel()

    @app.route("/api/health", methods=["GET"])
    def healthcheck() -> Response:
        """Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(
            jsonify({"status": "success", "message": "Service is running"}), 200
        )

    ##########################################################
    #
    # User Management
    #
    #########################################################

    @app.route("/api/create-user", methods=["PUT"])
    def create_user() -> Response:
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(
                    jsonify(
                        {
                            "status": "error",
                            "message": "Username and password are required",
                        }
                    ),
                    400,
                )

            Users.create_user(username, password)
            return make_response(
                jsonify(
                    {
                        "status": "success",
                        "message": f"User '{username}' created successfully",
                    }
                ),
                201,
            )

        except ValueError as e:
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while creating user",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/login", methods=["POST"])
    def login() -> Response:
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(
                    jsonify(
                        {
                            "status": "error",
                            "message": "Username and password are required",
                        }
                    ),
                    400,
                )

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(
                    jsonify(
                        {
                            "status": "success",
                            "message": f"User '{username}' logged in successfully",
                        }
                    ),
                    200,
                )
            else:
                return make_response(
                    jsonify(
                        {"status": "error", "message": "Invalid username or password"}
                    ),
                    401,
                )

        except ValueError as e:
            return make_response(jsonify({"status": "error", "message": str(e)}), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred during login",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/logout", methods=["POST"])
    @login_required
    def logout() -> Response:
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(
            jsonify({"status": "success", "message": "User logged out successfully"}),
            200,
        )

    @app.route("/api/change-password", methods=["POST"])
    @login_required
    def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(
                    jsonify({"status": "error", "message": "New password is required"}),
                    400,
                )

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(
                jsonify(
                    {"status": "success", "message": "Password changed successfully"}
                ),
                200,
            )

        except ValueError as e:
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while changing password",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/reset-users", methods=["DELETE"])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(
                jsonify(
                    {
                        "status": "success",
                        "message": f"Users table recreated successfully",
                    }
                ),
                200,
            )

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while deleting users",
                        "details": str(e),
                    }
                ),
                500,
            )

    ##########################################################
    #
    # Movies
    #
    ##########################################################

    @app.route("/api/reset-movies", methods=["DELETE"])
    def reset_movies() -> Response:
        """Recreate the movies table to delete movies.

        Returns:
            JSON response indicating the success of recreating the Movies table.

        Raises:
            500 error if there is an issue recreating the Movies table.
        """
        try:
            app.logger.info("Received request to recreate Movies table")
            with app.app_context():
                Movies.__table__.drop(db.engine)
                Movies.__table__.create(db.engine)
            app.logger.info("Movies table recreated successfully")
            return make_response(
                jsonify(
                    {
                        "status": "success",
                        "message": f"Movies table recreated successfully",
                    }
                ),
                200,
            )

        except Exception as e:
            app.logger.error(f"Movies table recreation failed: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while deleting users",
                        "details": str(e),
                    }
                ),
                500,
            )

    ############################################################
    #
    # Watchlist Add / Remove
    #
    ############################################################

    @app.route("/api/add-movie-to-watchlist", methods=["POST"])
    @login_required
    def add_movie_to_watchlist() -> Response:
        try:
            app.logger.info("Received request to add movie to watchlist")

            data = request.get_json()
            required_fields = ["title"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Missing required fields: {', '.join(missing_fields)}",
                        }
                    ),
                    400,
                )

            title = data["title"]

            app.logger.info(f"Looking up movie: '{title}'")
            movie = Movies.get_movie_by_title(title)

            if not movie:
                app.logger.warning(f"Movie not found: '{title}'")
                return make_response(
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Movie called '{title}' not found in DB",
                        }
                    ),
                    400,
                )

            watchlist_model.add_movie_to_watchlist(movie.title)  # <-- Fixed here
            app.logger.info(f"Successfully added movie to watchlist: '{title}'")

            return make_response(
                jsonify(
                    {
                        "status": "success",
                        "message": f"Movie called '{title}' added to watchlist",
                    }
                ),
                201,
            )

        except Exception as e:
            app.logger.error(f"Failed to add movie to watchlist: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while adding the movie to the watchlist",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/remove-movie-from-watchlist", methods=["DELETE"])
    @login_required
    def remove_movie_by_title() -> Response:
        try:
            app.logger.info("Received request to remove movie from watchlist")

            data = request.get_json()
            required_fields = ["title"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Missing required fields: {', '.join(missing_fields)}",
                        }
                    ),
                    400,
                )

            title = data["title"]

            app.logger.info(f"Looking up movie to remove: '{title}'")
            movie = Movies.get_movie_by_title(title)

            if not movie:
                app.logger.warning(f"Movie not found in DB: '{title}'")
                return make_response(
                    jsonify(
                        {
                            "status": "error",
                            "message": f"Movie called '{title}' not found in DB",
                        }
                    ),
                    400,
                )

            watchlist_model.remove_movie_from_watchlist(movie.title)  # <-- Fixed here
            app.logger.info(f"Successfully removed movie from watchlist: '{title}'")

            return make_response(
                jsonify(
                    {
                        "status": "success",
                        "message": f"Movie called '{title}' removed from watchlist",
                    }
                ),
                200,
            )

        except Exception as e:
            app.logger.error(f"Failed to remove movie from watchlist: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while removing the movie from the watchlist",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/clear-watchlist", methods=["POST"])
    @login_required
    def clear_watchlist() -> Response:
        """Route to clear all movies from the watchlist.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            500 error if there is an issue clearing the watchlist.

        """
        try:
            app.logger.info("Received request to clear the watchlist")

            watchlist_model.clear_watchlist()

            app.logger.info("Successfully cleared the watchlist")
            return make_response(
                jsonify({"status": "success", "message": "Watchlist cleared"}), 200
            )

        except Exception as e:
            app.logger.error(f"Failed to clear watchlist: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while clearing the watchlist",
                        "details": str(e),
                    }
                ),
                500,
            )

    ############################################################
    #
    # View Watchlist
    #
    ############################################################

    @app.route("/api/get-all-movies-from-watchlist", methods=["GET"])
    @login_required
    def get_all_movies_from_watchlist() -> Response:
        try:
            app.logger.info(
                "Received request to retrieve all movies from the watchlist."
            )

            movies = watchlist_model.get_all_movies()

            app.logger.info(
                f"Successfully retrieved {len(movies)} movies from the watchlist."
            )
            return make_response(
                jsonify(
                    {
                        "status": "success",
                        "movies": [
                            {
                                "title": movie.title,
                                "release_year": movie.release_year,
                                "runtime": movie.runtime,
                                "popularity": movie.popularity,
                                "average_rating": movie.average_rating,
                            }
                            for movie in movies
                        ],
                    }
                ),
                200,
            )

        except Exception as e:
            app.logger.error(f"Failed to retrieve movies from watchlist: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while retrieving the watchlist",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/get-movie-from-watchlist-by-title/<title>", methods=["GET"])
    @login_required
    def get_movie_by_title(title: str) -> Response:
        """Retrieve a song from the playlist by its title.

        Path Parameter:
            - title (str): The name of the movie.

        Returns:
            JSON response containing movie details.

        Raises:
            404 error if the movie is not found.
            500 error if there is an issue retrieving the movie.

        """
        try:
            app.logger.info(f"Received request to retrieve movie called '{title}'")

            movie = watchlist_model.get_movie_by_title(title)

            app.logger.info(
                f"Successfully retrieved movie: {movie.title} ({movie.release_year})"
            )
            return make_response(jsonify({"status": "success", "movie": movie}), 200)

        except ValueError as e:
            app.logger.warning(f"Movie called '{title}' not found: {e}")
            return make_response(jsonify({"status": "error", "message": str(e)}), 404)

        except Exception as e:
            app.logger.error(f"Failed to retrieve movie called '{title}': {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while retrieving the movie",
                        "details": str(e),
                    }
                ),
                500,
            )

    @app.route("/api/get-watchlist-length-and-duration", methods=["GET"])
    @login_required
    def get_watchlist_length() -> Response:
        """Retrieve the length (number of movies) of the watchlist, and total duration (in hours)

        Returns:
            JSON response containing the watchlist length and total duration.

        Raises:
            500 error if there is an issue retrieving watchlist information.

        """
        try:
            app.logger.info("Received request to retrieve watchlist length & total duration.")

            watchlist_length = watchlist_model.get_watchlist_length()
            watchlist_duration = watchlist_model.get_watchlist_duration()

            app.logger.info(f"Watchlist contains {watchlist_length} movies with a total duration of {watchlist_duration} hours")
            return make_response(jsonify({
                "status": "success",
                "watchlist_length": watchlist_length,
                "watchlist_duration": watchlist_duration
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve watchlist length and duration: {e}")
            return make_response(
                jsonify(
                    {
                        "status": "error",
                        "message": "An internal error occurred while retrieving watchlist details",
                        "details": str(e),
                    }
                ),
                500,
            )

    return app


if __name__ == "__main__":
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")

# Watchlist Application

## Overview

This project is a Flask application for managing a personal movie watchlist.
Users can register, log in securely, add movies to their watchlist by fetching information from The Movie Database (TMDB) API, view or delete movies from their watchlist, and clear it entirely. Random movie selections and watchlist duration summaries are also supported.
The backend is fully containerized with Docker and  uses a SQLite database with SQLAlchemy ORM.


API: [The Movie Database API (TMDB)](https://developer.themoviedb.org/reference/overview)
     [Random Integer Generator API (RANDOM.ORG)] (https://www.random.org/integers/)

## Routes


| Route | Method | Purpose |
|:---|:---|:---|
| `/api/health` | GET | Healthcheck endpoint to verify app is running. |
| `/api/create-user` | PUT | Register a new user account. |
| `/api/login` | POST | Log in an existing user. |
| `/api/logout` | POST | Log out the current user. |
| `/api/change-password` | POST | Change the logged-in user's password. |
| `/api/add-movie-to-watchlist` | POST | Add a movie to your watchlist (by title). |
| `/api/remove-movie-from-watchlist` | DELETE | Remove a movie from your watchlist. |
| `/api/clear-watchlist` | POST | Clear all movies from your watchlist. |
| `/api/get-all-movies-from-watchlist` | GET | Retrieve all movies currently in your watchlist. |
| `/api/get-movie-from-watchlist-by-title/<title>` | GET | Retrieve specific movie details by title. |
| `/api/get-watchlist-length-and-duration` | GET | Get the total number and duration of movies in your watchlist. |

## Features

1. **Account Management**
   - Users can register, log in , update their password, and log out. Passwords are hashed in the database.

2. **Add Movies to Watchlist**
   - Users can add movies to their personal watchlist by searching a movie title, which fetches movie details such as release year, runtime, popularity, and rating from TMDB.

3. **Manage and View Watchlist**
   - Users can view all movies in their watchlist, delete movies, or clear their entire watchlist.

4. **Random Movie Recommendation**
   - Users can get a random movie suggestion from their current watchlist to help them decide what to watch.

5. **Watchlist Summary and Duration Tracking**
   - Users can retrieve the total number of movies and combined watchtime for their current watchlist.

6. **Healthcheck and Service Monitoring**
   - A healthcheck endpoint is available to verify that the service is running correctly.

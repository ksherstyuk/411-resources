#! /usr/bin/env python3

import pytest

from watchlist.models.watchlist_model import WatchlistModel
from watchlist.models.movie_model import Movies


@pytest.fixture()
def watchlist_model():
    """Fixture to provide a new instance of WatchlistModel for each test."""
    return WatchlistModel()

"""Fixtures providing sample movies for the tests."""
@pytest.fixture
def movie_clockwork_orange(session):
    """Fixture for the movie 'A Clockwork Orange'."""
    movie = Movies(
        title="A Clockwork Orange",
        release_year=1971,
        runtime=137,
        popularity=32.11, #arbitrary
        average_rating=8.2
    )
    session.add(movie)
    session.commit()
    return movie

@pytest.fixture
def movie_sonic(session):
    """Fixture for a the movie 'Sonic the Hedgehog 2'."""
    movie = Movies(
        title="Sonic the Hedgehog 2",
        release_year=2022,
        runtime=123,
        popularity=39.11, #arbitrary
        average_rating=7.5
    )
    session.add(movie)
    session.commit()
    return movie

@pytest.fixture
def sample_watchlist(movie_flow, movie_):
    """Fixture for a sample watchlist."""
    return [movie_clockwork_orange, movie_sonic]

##################################################
# Add / Remove Movie Management Test Cases
##################################################


def test_add_movie_to_watchlist(watchlist_model, movie_sonic, mocker):
    # Movies cannot be added via ID as they are not from catalog; 
    # Refine with adding movie by title from IMDB database.
    """Test adding a movie to the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Movies.get_movie_by_title", return_value=movie_sonic)
    watchlist_model.add_movie_to_watchlist(movie_sonic.title)
    assert len(watchlist_model.watchlist) == 1
    assert watchlist_model.watchlist[0] == 'Sonic the Hedgehog 2'


def test_add_duplicate_movie_to_watchlist(watchlist_model, movie_sonic, mocker):
    # Movies cannot be added via ID as they are not from catalog; 
    # Refine with adding movie by title from IMDB database.
    """Test error when adding a duplicate song to the watchlist by ID."""
    mocker.patch("watchlist.models.watchlist_model.Movies.get_movie_by_title", side_effect=[movie_sonic] * 2)
    watchlist_model.add_movie_to_watchlist(movie_sonic.title)
    with pytest.raises(ValueError, match="Movie called 'Sonic the Hedgehog 2' already exists in the watchlist"):
        watchlist_model.add_movie_to_watchlist(movie_sonic.title)


def test_remove_movie_from_watchlist(watchlist_model, mocker):
    """Test removing a movie from the watchlist by song_id."""
    mocker.patch("watchlist.models.watchlist_model.Movies.get_movie_by_title", return_value=movie_sonic)

    watchlist_model.watchlist = ["A Clockwork Orange","Sonic the Hedgehog 2"]

    watchlist_model.remove_movie_from_watchlist(movie_sonic.title)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 movie, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0] == "A Clockwork Orange", "Expected movie 'A Clockwork Orange' to remain"


def test_clear_watchlist(watchlist_model):
    """Test clearing the entire watchlist."""
    watchlist_model.watchlist.append('Sonic the Hedgehog 2')

    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0, "Watchlist should be empty after clearing"


##################################################
# Movie Retrieval Test Cases
##################################################


def test_get_all_movies(watchlist_model, sample_watchlist, mocker):
    """Test successfully retrieving all movies from the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.WatchlistModel._get_movie_from_tmdb", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend(["A Clockwork Orange","Sonic the Hedgehog 2"])

    all_movies = watchlist_model.get_all_movies()

    assert len(all_movies) == 2
    assert all_movies[0].title == 'A Clockwork Orange'
    assert all_movies[1].title == 'Sonic the Hedgehog 2'


def test_get_movie_by_title(watchlist_model, movie_sonic, mocker):
    """Test successfully retrieving a movie from the watchlist by title."""
    mocker.patch("watchlist.models.watchlist_model.Movies.get_movie_by_title", return_value=movie_sonic)
    watchlist_model.watchlist.append('Sonic the Hedgehog 2')

    retrieved_movie = watchlist_model.get_movie_by_title('Sonic the Hedgehog 2')

    assert retrieved_movie.title == 'Sonic the Hedgehog 2'
    assert retrieved_movie.release_year == 2022
    assert retrieved_movie.runtime == 123
    assert retrieved_movie.popularity == 39.11
    assert retrieved_movie.average_rating == 7.5


def test_get_watchlist_length(watchlist_model):
    """Test getting the length of the watchlist."""
    watchlist_model.watchlist.extend(["A Clockwork Orange","Sonic the Hedgehog 2"])
    assert watchlist_model.get_watchlist_length() == 2, "Expected watchlist length to be 2"


def test_get_watchlist_duration(watchlist_model, sample_watchlist, mocker):
    """Test getting the total duration of the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.WatchlistModel._get_movie_from_tmdb", side_effect=sample_watchlist)
    watchlist_model.watchlist.extend(["A Clockwork Orange","Sonic the Hedgehog 2"])
    assert watchlist_model.get_watchlist_duration() == 4.33, "Expected watchlist duration to be 4.33 hours"

def test_get_random_movie_from_watchlist(watchlist_model, mocker): #not too sure of this guy
    """Test getting the a random movie from the watchlist."""
    watchlist_model.watchlist.extend(["A Clockwork Orange","Sonic the Hedgehog 2"])
    mocker.patch("watchlist.models.watchlist_model.get_random", return_value=1)
    assert watchlist_model.get_random_movie_from_watchlist() == 'A Clockwork Orange', "Random index should correspond to first movie in list"


##################################################
# Utility Function Test Cases
##################################################


def test_check_if_empty_non_empty_watchlist(watchlist_model):
    """Test check_if_empty does not raise error if watchlist is not empty."""
    watchlist_model.watchlist.append('Sonic the Hedgehog 2')
    try:
        watchlist_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty watchlist")


def test_check_if_empty_empty_watchlist(watchlist_model):
    """Test check_if_empty raises error when watchlist is empty."""
    watchlist_model.clear_watchlist()
    with pytest.raises(ValueError, match="Watchlist is empty"):
        watchlist_model.check_if_empty()


def test_validate_movie_title(watchlist_model, mocker):
    """Test validate_movie_title does not raise error for valid movie title."""
    mocker.patch("watchlist.models.watchlist_model.WatchlistModel._get_movie_from_tmdb", return_value=True)

    watchlist_model.watchlist.append('Sonic the Hedgehog 2')
    try:
        watchlist_model.validate_movie_title('Sonic the Hedgehog 2')
    except ValueError:
        pytest.fail("validate_movie_title raised ValueError unexpectedly for valid movie title")


def test_validate_movie_title_invalid_title(watchlist_model):
    """Test validate_movie_title raises error for invalid movie title."""
    with pytest.raises(ValueError, match="Invalid movie title: 19999"):
        watchlist_model.validate_movie_title(19999)
import pytest

from watchlist.models.movie_model import Movies


# --- Fixtures ---

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


# --- Create Movie ---

def test_create_movie(session):
    """Test creating a new movie."""
    Movies.create_movie("A Clockwork Orange", 1971, 137, 32.11, 8.2)
    movie = session.query(Movies).filter_by(title="A Clockwork Orange").first()
    assert movie is not None
    assert movie.release_year == 1971


def test_create_duplicate_movie(session, movie_clockwork_orange):
    """Test creating a movie with a duplicate title."""
    with pytest.raises(ValueError, match="already exists"):
        Movies.create_movie("A Clockwork Orange", 1971, 137, 32.11, 8.2)


@pytest.mark.parametrize("title, release_year, runtime, popularity, average_rating", [
    ("", 2001, 156, 37.11, 8.9),
    ("Valid Title", 1888, 156, 37.11, 8.9),
    ("Valid Title", 2001, -10, 37.11, 8.9),
    ("Valid Title", 2001, 156, "", 8.9),
    ("Valid Title", 2001, 156, 37.11, 23.3),
])
def test_create_movie_invalid_data(title, release_year, runtime, popularity, average_rating):
    """Test validation errors when creating a movie."""
    with pytest.raises(ValueError):
        Movies.create_movie(title, release_year, runtime, popularity, average_rating)


# --- Get Movie ---

def get_movie_by_title(movie_sonic):
    """Test fetching a movie its title."""
    fetched = Movies.get_movie_by_title(movie_sonic.title)
    assert fetched.release_year == 2022

def test_get_movie_by_title_not_found(app):
    """Test error when fetching nonexistent movie by its title."""
    with pytest.raises(ValueError, match="not found"):
        Movies.get_movie_by_title("One two three testing this is a fake movie!!!")


# --- Delete Movie ---

def test_delete_movie(session, movie_sonic):
    """Test deleting a movie by its title."""
    Movies.delete_movie(movie_sonic.title)
    assert session.query(Movies).get(movie_sonic.title) is None

def test_delete_movie_not_found(app):
    """Test deleting a non-existent movie by its title."""
    with pytest.raises(ValueError, match="not found"):
        Movies.delete_movie("One two three testing this is a fake movie!!!")

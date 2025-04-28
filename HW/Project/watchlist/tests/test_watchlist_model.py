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
    # Refine with creating sample movie by title from IMDB database. 
    # Remove if not needed.
    # i think we just define a fake movie, since we're not testing API here
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

#stopped here
def test_remove_song_from_watchlist_by_song_id(watchlist_model, mocker):
    """Test removing a song from the watchlist by song_id."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", return_value=song_beatles)

    watchlist_model.watchlist = [1,2]

    watchlist_model.remove_song_by_song_id(1)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 song, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0] == 2, "Expected song with id 2 to remain"


def test_remove_song_by_track_number(watchlist_model):
    """Test removing a song from the watchlist by track number."""
    watchlist_model.watchlist = [1,2]
    assert len(watchlist_model.watchlist) == 2

    watchlist_model.remove_song_by_track_number(1)
    assert len(watchlist_model.watchlist) == 1, f"Expected 1 song, but got {len(watchlist_model.watchlist)}"
    assert watchlist_model.watchlist[0] == 2, "Expected song with id 2 to remain"


def test_clear_watchlist(watchlist_model):
    """Test clearing the entire watchlist."""
    watchlist_model.watchlist.append(1)

    watchlist_model.clear_watchlist()
    assert len(watchlist_model.watchlist) == 0, "watchlist should be empty after clearing"


# ##################################################
# # Tracklisting Management Test Cases
# ##################################################


def test_move_song_to_track_number(watchlist_model, sample_watchlist, mocker):
    """Test moving a song to a specific track number in the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])

    watchlist_model.move_song_to_track_number(2, 1)  # Move Song 2 to the first position
    assert watchlist_model.watchlist[0] == 2, "Expected Song 2 to be in the first position"
    assert watchlist_model.watchlist[1] == 1, "Expected Song 1 to be in the second position"


def test_swap_songs_in_watchlist(watchlist_model, sample_watchlist, mocker):
    """Test swapping the positions of two songs in the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])

    watchlist_model.swap_songs_in_watchlist(1, 2)  # Swap positions of Song 1 and Song 2
    assert watchlist_model.watchlist[0] == 2, "Expected Song 2 to be in the first position"
    assert watchlist_model.watchlist[1] == 1, "Expected Song 1 to be in the second position"


def test_swap_song_with_itself(watchlist_model, song_beatles, mocker):
    """Test swapping the position of a song with itself raises an error."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", side_effect=[song_beatles] * 2)
    watchlist_model.watchlist.append(1)

    with pytest.raises(ValueError, match="Cannot swap a song with itself"):
        watchlist_model.swap_songs_in_watchlist(1, 1)  # Swap positions of Song 1 with itself


def test_move_song_to_end(watchlist_model, sample_watchlist, mocker):
    """Test moving a song to the end of the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])

    watchlist_model.move_song_to_end(1)  # Move Song 1 to the end
    assert watchlist_model.watchlist[1] == 1, "Expected Song 1 to be at the end"


def test_move_song_to_beginning(watchlist_model, sample_watchlist, mocker):
    """Test moving a song to the beginning of the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])

    watchlist_model.move_song_to_beginning(2)  # Move Song 2 to the beginning
    assert watchlist_model.watchlist[0] == 2, "Expected Song 2 to be at the beginning"


##################################################
# Song Retrieval Test Cases
##################################################


def test_get_song_by_track_number(watchlist_model, song_beatles, mocker):
    """Test successfully retrieving a song from the watchlist by track number."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", return_value=song_beatles)
    watchlist_model.watchlist.append(1)

    retrieved_song = watchlist_model.get_song_by_track_number(1)
    assert retrieved_song.id == 1
    assert retrieved_song.title == 'Come Together'
    assert retrieved_song.artist == 'The Beatles'
    assert retrieved_song.year == 1969
    assert retrieved_song.duration == 259
    assert retrieved_song.genre == 'Rock'


def test_get_all_songs(watchlist_model, sample_watchlist, mocker):
    """Test successfully retrieving all songs from the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.watchlistModel._get_song_from_cache_or_db", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])

    all_songs = watchlist_model.get_all_songs()

    assert len(all_songs) == 2
    assert all_songs[0].id == 1
    assert all_songs[1].id == 2


def test_get_song_by_song_id(watchlist_model, song_beatles, mocker):
    """Test successfully retrieving a song from the watchlist by song ID."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", return_value=song_beatles)
    watchlist_model.watchlist.append(1)

    retrieved_song = watchlist_model.get_song_by_song_id(1)

    assert retrieved_song.id == 1
    assert retrieved_song.title == 'Come Together'
    assert retrieved_song.artist == 'The Beatles'
    assert retrieved_song.year == 1969
    assert retrieved_song.duration == 259
    assert retrieved_song.genre == 'Rock'


def test_get_current_song(watchlist_model, song_beatles, mocker):
    """Test successfully retrieving the current song from the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", return_value=song_beatles)

    watchlist_model.watchlist.append(1)

    current_song = watchlist_model.get_current_song()
    assert current_song.id == 1
    assert current_song.title == 'Come Together'
    assert current_song.artist == 'The Beatles'
    assert current_song.year == 1969
    assert current_song.duration == 259
    assert current_song.genre == 'Rock'


def test_get_watchlist_length(watchlist_model):
    """Test getting the length of the watchlist."""
    watchlist_model.watchlist.extend([1, 2])
    assert watchlist_model.get_watchlist_length() == 2, "Expected watchlist length to be 2"


def test_get_watchlist_duration(watchlist_model, sample_watchlist, mocker):
    """Test getting the total duration of the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.watchlistModel._get_song_from_cache_or_db", side_effect=sample_watchlist)
    watchlist_model.watchlist.extend([1, 2])
    assert watchlist_model.get_watchlist_duration() == 560, "Expected watchlist duration to be 560 seconds"


##################################################
# Utility Function Test Cases
##################################################


def test_check_if_empty_non_empty_watchlist(watchlist_model):
    """Test check_if_empty does not raise error if watchlist is not empty."""
    watchlist_model.watchlist.append(1)
    try:
        watchlist_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty watchlist")


def test_check_if_empty_empty_watchlist(watchlist_model):
    """Test check_if_empty raises error when watchlist is empty."""
    watchlist_model.clear_watchlist()
    with pytest.raises(ValueError, match="watchlist is empty"):
        watchlist_model.check_if_empty()


def test_validate_song_id(watchlist_model, mocker):
    """Test validate_song_id does not raise error for valid song ID."""
    mocker.patch("watchlist.models.watchlist_model.watchlistModel._get_song_from_cache_or_db", return_value=True)

    watchlist_model.watchlist.append(1)
    try:
        watchlist_model.validate_song_id(1)
    except ValueError:
        pytest.fail("validate_song_id raised ValueError unexpectedly for valid song ID")


def test_validate_song_id_no_check_in_watchlist(watchlist_model, mocker):
    """Test validate_song_id does not raise error for valid song ID when the id isn't in the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.watchlistModel._get_song_from_cache_or_db", return_value=True)
    try:
        watchlist_model.validate_song_id(1, check_in_watchlist=False)
    except ValueError:
        pytest.fail("validate_song_id raised ValueError unexpectedly for valid song ID")


def test_validate_song_id_invalid_id(watchlist_model):
    """Test validate_song_id raises error for invalid song ID."""
    with pytest.raises(ValueError, match="Invalid song id: -1"):
        watchlist_model.validate_song_id(-1)

    with pytest.raises(ValueError, match="Invalid song id: invalid"):
        watchlist_model.validate_song_id("invalid")


def test_validate_song_id_not_in_watchlist(watchlist_model, song_nirvana, mocker):
    """Test validate_song_id raises error for song ID not in the watchlist."""
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", return_value=song_nirvana)
    watchlist_model.watchlist.append(1)
    with pytest.raises(ValueError, match="Song with id 2 not found in watchlist"):
        watchlist_model.validate_song_id(2)


def test_validate_track_number(watchlist_model):
    """Test validate_track_number does not raise error for valid track number."""
    watchlist_model.watchlist.append(1)
    try:
        watchlist_model.validate_track_number(1)
    except ValueError:
        pytest.fail("validate_track_number raised ValueError unexpectedly for valid track number")

@pytest.mark.parametrize("track_number, expected_error", [
    (0, "Invalid track number: 0"),
    (2, "Invalid track number: 2"),
    ("invalid", "Invalid track number: invalid"),
])
def test_validate_track_number_invalid(watchlist_model, track_number, expected_error):
    """Test validate_track_number raises error for invalid track numbers."""
    watchlist_model.watchlist.append(1)

    with pytest.raises(ValueError, match=expected_error):
        watchlist_model.validate_track_number(track_number)



##################################################
# Playback Test Cases
##################################################


def test_play_current_song(watchlist_model, sample_watchlist, mocker):
    """Test playing the current song."""
    mock_update_play_count = mocker.patch("watchlist.models.watchlist_model.Songs.update_play_count")
    mocker.patch("watchlist.models.watchlist_model.Songs.get_song_by_id", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])

    watchlist_model.play_current_song()

    # Assert that CURRENT_TRACK_NUMBER has been updated to 2
    assert watchlist_model.current_track_number == 2, f"Expected track number to be 2, but got {watchlist_model.current_track_number}"

    # Assert that update_play_count was called with the id of the first song
    mock_update_play_count.assert_called_once_with()

    # Get the second song from the iterator (which will increment CURRENT_TRACK_NUMBER back to 1)
    watchlist_model.play_current_song()

    # Assert that CURRENT_TRACK_NUMBER has been updated back to 1
    assert watchlist_model.current_track_number == 1, f"Expected track number to be 1, but got {watchlist_model.current_track_number}"

    # Assert that update_play_count was called with the id of the second song
    mock_update_play_count.assert_called_with()


def test_rewind_watchlist(watchlist_model):
    """Test rewinding the iterator to the beginning of the watchlist."""
    watchlist_model.watchlist.extend([1, 2])
    watchlist_model.current_track_number = 2

    watchlist_model.rewind_watchlist()
    assert watchlist_model.current_track_number == 1, "Expected to rewind to the first track"


def test_go_to_track_number(watchlist_model):
    """Test moving the iterator to a specific track number in the watchlist."""
    watchlist_model.watchlist.extend([1, 2])

    watchlist_model.go_to_track_number(2)
    assert watchlist_model.current_track_number == 2, "Expected to be at track 2 after moving song"


def test_go_to_random_track(watchlist_model, mocker):
    """Test that go_to_random_track sets a valid random track number."""
    watchlist_model.watchlist.extend([1, 2])

    mocker.patch("watchlist.models.watchlist_model.get_random", return_value=2)

    watchlist_model.go_to_random_track()
    assert watchlist_model.current_track_number == 2, "Current track number should be set to the random value"


def test_play_entire_watchlist(watchlist_model, sample_watchlist, mocker):
    """Test playing the entire watchlist."""
    mock_update_play_count = mocker.patch("watchlist.models.watchlist_model.Songs.update_play_count")
    mocker.patch("watchlist.models.watchlist_model.watchlistModel._get_song_from_cache_or_db", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1,2])

    watchlist_model.play_entire_watchlist()

    # Check that all play counts were updated
    mock_update_play_count.assert_any_call()
    assert mock_update_play_count.call_count == len(watchlist_model.watchlist)

    # Check that the current track number was updated back to the first song
    assert watchlist_model.current_track_number == 1, "Expected to loop back to the beginning of the watchlist"


def test_play_rest_of_watchlist(watchlist_model, sample_watchlist, mocker):
    """Test playing from the current position to the end of the watchlist.

    """
    mock_update_play_count = mocker.patch("watchlist.models.watchlist_model.Songs.update_play_count")
    mocker.patch("watchlist.models.watchlist_model.watchlistModel._get_song_from_cache_or_db", side_effect=sample_watchlist)

    watchlist_model.watchlist.extend([1, 2])
    watchlist_model.current_track_number = 2

    watchlist_model.play_rest_of_watchlist()

    # Check that play counts were updated for the remaining songs
    mock_update_play_count.assert_any_call()
    assert mock_update_play_count.call_count == 1

    assert watchlist_model.current_track_number == 1, "Expected to loop back to the beginning of the watchlist"
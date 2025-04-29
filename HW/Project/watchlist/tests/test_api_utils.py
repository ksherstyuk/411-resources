import pytest
import requests

from watchlist.utils.api_utils import get_random

RANDOM_NUMBER = 4


@pytest.fixture
def mock_random_org(mocker):
    """Fixture to mock requests.get for random.org."""
    mock_response = mocker.Mock()
    mock_response.text = f"{RANDOM_NUMBER}"
    mock_response.raise_for_status.return_value = None  # Simulate successful response
    mock_get = mocker.patch("requests.get", return_value=mock_response)
    return mock_get  # Return the patched requests.get


def test_get_random(mock_random_org):
    """Test retrieving a random number from random.org."""
    result = get_random(10)

    # Assert that the result is the mocked random number
    assert (
        result == RANDOM_NUMBER
    ), f"Expected random number {RANDOM_NUMBER}, but got {result}"

    # Ensure that the correct URL was called
    mock_random_org.assert_called_once_with(
        "https://www.random.org/integers/?num=1&min=1&col=1&base=10&format=plain&rnd=new&max=10",
        timeout=5,
    )


def test_get_random_request_failure(mocker):
    """Test handling of a request failure when calling random.org."""
    mocker.patch(
        "requests.get",
        side_effect=requests.exceptions.RequestException("Connection error"),
    )

    with pytest.raises(
        RuntimeError, match="Request to random.org failed: Connection error"
    ):
        get_random(10)


def test_get_random_timeout(mocker):
    """Test handling of a timeout when calling random.org."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random(10)


def test_get_random_invalid_response(mocker):
    """Test handling of an invalid response from random.org."""
    mock_response = mocker.Mock()
    mock_response.text = "invalid_response"
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.get", return_value=mock_response)

    with pytest.raises(
        ValueError, match="Invalid response from random.org: invalid_response"
    ):
        get_random(10)


def test_validate_string_valid():
    """Test handling of a valid string. Should return true."""
    from watchlist.utils.api_utils import validate_string

    assert validate_string("hello") is True


def test_validate_string_invalid():
    """Test handling of a invalid string. Should return false."""
    from watchlist.utils.api_utils import validate_string

    assert validate_string(1234) is False
    assert validate_string(None) is False
    assert validate_string([]) is False


def test_api_get_movie_by_title_success(mocker):
    """Test successful retrieval of a movie by title from TMDB."""
    from watchlist.utils.api_utils import api_get_movie_by_title

    mocker.patch("watchlist.utils.api_utils.get_api_key", return_value="fake-api-key")
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "total_results": 2,
        "results": [{"title": "Fake Movie"}],
    }
    mocker.patch("watchlist.utils.api_utils.requests.get", return_value=mock_response)

    result = api_get_movie_by_title("Fake Movie")
    assert isinstance(result, dict)
    assert result["title"] == "Fake Movie"


def test_api_get_movie_by_title_invalid_type():
    """Test handling of invalid (non-string) movie title input."""
    from watchlist.utils.api_utils import api_get_movie_by_title

    with pytest.raises(ValueError, match="Movie title must be inputted as a String!"):
        api_get_movie_by_title(1234)


def test_api_get_movie_by_title_not_found(mocker):
    """Test handling of a case where the movie is not found in TMDB."""
    from watchlist.utils.api_utils import api_get_movie_by_title

    mocker.patch("watchlist.utils.api_utils.get_api_key", return_value="fake-api-key")
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"total_results": 0, "results": []}
    mocker.patch("watchlist.utils.api_utils.requests.get", return_value=mock_response)

    with pytest.raises(
        ValueError, match="Movie with entered title does not exist in the database."
    ):
        api_get_movie_by_title("Nonexistent Movie")

from contextlib import contextmanager
import re
import sqlite3

import pytest

from boxing.models.boxers_model import (
    Boxer,
    create_boxer,
    delete_boxer,
    get_leaderboard,
    get_boxer_by_id,
    get_boxer_by_name,
    get_weight_class,
    update_boxer_stats
)

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("boxing.models.boxer_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


######################################################
#
#    Add & Delete Boxers
#
######################################################


def test_create_boxer(mock_cursor):
    """Test creating a new boxer in the catalog.

    """
    create_boxer(name="Boxer Name", weight=126, height=77, reach=14.7, age=18)

    expected_query = normalize_whitespace("""
        INSERT INTO boxers (name, weight, height, reach, age)
        VALUES (?, ?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call (second element of call_args)
    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = ("Boxer Name", 126, 77, 14.7, 18)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_create_boxer_duplicate(mock_cursor):
    """Test creating a boxer with a duplicate name (should raise an error).

    """
    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: boxers.name")

    with pytest.raises(ValueError, match="Boxer with name 'Boxer Name' already exists."):
        create_boxer(name="Boxer Name", weight=126, height=77, reach=14.7, age=18)


def test_create_boxer_invalid_weight():
    """Test error when trying to create a boxer with an invalid weight (e.g., less than 125 lb)

    """
    with pytest.raises(ValueError, match=r"Invalid weight: 10 \(must be at least 125\)."):
        create_boxer(name="Boxer Name", weight=10, height=77, reach=14.7, age=18)

    with pytest.raises(ValueError, match=r"Invalid weight: invalid \(must be at least 125\)."):
        create_boxer(name="Boxer Name", weight=10, height=77, reach=14.7, age="invalid")

def test_create_boxer_invalid_height():
    """Test error when trying to create a boxer with an invalid height (e.g., less than 0 in)

    """
    with pytest.raises(ValueError, match=r"Invalid height: -5 \(must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight=126, height=-5, reach=14.7, age=18)

    with pytest.raises(ValueError, match=r"Invalid height: invalid \(must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight=126, height="invalid", reach=14.7, age=18)


def test_create_boxer_invalid_reach():
    """Test error when trying to create a boxer with an invalid reach (e.g., less than 0 in)

    """
    with pytest.raises(ValueError, match=r"Invalid reach: -5 \(must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight=126, height=77, reach=-5, age=18)

    with pytest.raises(ValueError, match=r"Invalid reach: invalid \(must be greater than 0\)."):
        create_boxer(name="Boxer Name", weight=126, height=77, reach="invalid", age=18)

def test_create_boxer_invalid_age():
    """Test error when trying to create a boxer with an invalid age (e.g., younger than 18 or older than 40)

    """
    with pytest.raises(ValueError, match=r"Invalid height: 8 \(must be between the ages of 18 and 40, inclusive\)."):
        create_boxer(name="Boxer Name", weight=126, height=77, reach=14.7, age=8)

    with pytest.raises(ValueError, match=r"Invalid height: 48 \(must be between the ages of 18 and 40, inclusive\)."):
        create_boxer(name="Boxer Name", weight=126, height=77, reach=14.7, age=48)

    with pytest.raises(ValueError, match=r"Invalid height: invalid \(must be between the ages of 18 and 40, inclusive\)."):
        create_boxer(name="Boxer Name", weight=126, height=77, reach=14.7, age="invalid")


def test_delete_boxer(mock_cursor):
    """Test deleting a boxer by boxer ID.

    """
    # Simulate the existence of a boxer w/ id=1
    # We can use any value other than None
    mock_cursor.fetchone.return_value = (True)

    delete_boxer(1)

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?")
    expected_delete_sql = normalize_whitespace("DELETE FROM boxers WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_delete_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_delete_sql == expected_delete_sql, "The DELETE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_delete_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_delete_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_delete_args == expected_delete_args, f"The UPDATE query arguments did not match. Expected {expected_delete_args}, got {actual_delete_args}."


def test_delete_boxer_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent boxer.

    """
    # Simulate that no boxer exists with the given ID
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        delete_boxer(999)


######################################################
#
#    Get Leaderboard & Boxer
#
######################################################


def test_get_leaderboard_by_win():
    """Test getting the boxer leaderboard (sorted by wins).

    """
    mock_cursor.fetchall.return_value = [
        (1, "Mark S", 126, 77, 14.7, 18, 12, 3, False),
        (2, "Helena E", 150, 78, 14.7, 18, 2, 2, False),
        (3, "Dylan G", 151, 79, 14.7, 18, 2, 0, False)
    ]

    leaderboard = get_leaderboard()

    expected_result = [
        {"id": 1, "name": "Mark S", "weight": 126, "height": 77, "reach": 14.7, "age": 18, "weight_class": "FEATHERWEIGHT", "fights": 12, "wins": 3, "win_pct": 25},
        {"id": 2, "name": "Helena E", "weight": 150, "height": 78, "reach": 14.7, "age": 18, "weight_class": "LIGHTWEIGHT", "fights": 2, "wins": 2, "win_pct": 100},
        {"id": 3, "name": "Dylan G", "weight": 151, "height": 79, "reach": 14.7, "age": 18, "weight_class": "LIGHTWEIGHT", "fights": 2, "wins": 0, "win_pct": 0},
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_by_winpct():
    """Test getting the boxer leaderboard (sorted by win percentage).

    """
    mock_cursor.fetchall.return_value = [
        (1, "Mark S", 126, 77, 14.7, 18, 12, 3, False),
        (2, "Helena E", 150, 78, 14.7, 18, 2, 2, False),
        (3, "Dylan G", 151, 79, 14.7, 18, 2, 0, False)
    ]

    leaderboard = get_leaderboard()

    expected_result = [
        {"id": 2, "name": "Helena E", "weight": 150, "height": 78, "reach": 14.7, "age": 18, "weight_class": "LIGHTWEIGHT", "fights": 2, "wins": 2, "win_pct": 100},
        {"id": 1, "name": "Mark S", "weight": 126, "height": 77, "reach": 14.7, "age": 18, "weight_class": "FEATHERWEIGHT", "fights": 12, "wins": 3, "win_pct": 25},
        {"id": 3, "name": "Dylan G", "weight": 151, "height": 79, "reach": 14.7, "age": 18, "weight_class": "LIGHTWEIGHT", "fights": 2, "wins": 0, "win_pct": 0},
    ]

    assert leaderboard == expected_result, f"Expected {expected_result}, but got {leaderboard}"

    expected_query = normalize_whitespace("""
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."


def test_get_leaderboard_bad_input():
    """Test error if invalid sorting parameter provided.

    """
    with pytest.raises(ValueError, match="Invalid sort_by parameter: hi"):
        get_leaderboard("hi")


def test_get_boxer_by_id(mock_cursor):
    """Test getting a boxer by id.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 126, 77, 14.7, 18, False)

    result = get_boxer_by_id(1)

    expected_result = Boxer(1, "Boxer Name", 126, 77, 14.7, 18)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE id = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_id_bad_id(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        get_boxer_by_id(999)


def test_get_boxer_by_name(mock_cursor):
    """Test getting a boxer by name.

    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 126, 77, 14.7, 18, False)

    result = get_boxer_by_name("Boxer Name")

    expected_result = Boxer(1, "Boxer Name", 126, 77, 14.7, 18)

    assert result == expected_result, f"Expected {expected_result}, got {result}"

    expected_query = normalize_whitespace("SELECT id, name, weight, height, reach, age FROM boxers WHERE name = ?")
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    actual_arguments = mock_cursor.execute.call_args[0][1]
    expected_arguments = (1,)

    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_get_boxer_by_name_bad_name(mock_cursor):
    """Test error when getting a non-existent boxer.

    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer named Johnny not found"):
        get_boxer_by_name("Johnny")


def test_get_weight_class():
    """Test getting a weight class output.

    """
    result = get_weight_class(130)

    expected_result = 'FEATHERWEIGHT'

    assert result == expected_result, f"Expected {expected_result}, got {result}"


def test_get_weight_class_invalid_input():
    """Test error when trying to get a weight class corresponsing to invalid weight.

    """
    with pytest.raises(ValueError, match="Invalid weight: 10. Weight must be at least 125."):
        get_weight_class(10)


######################################################
#
#    Changing Boxer Stats
#
######################################################


def test_update_boxer_stats(mock_cursor):
    """Testing updating the status of a boxer's game to reflect if they won or lost.
    
    """
    mock_cursor.fetchone.return_value = (1, "Boxer Name", 126, 77, 14.7, 18, False)

    update_boxer_stats(1, 'win')

    expected_select_sql = normalize_whitespace("SELECT id FROM boxers WHERE id = ?",)
    expected_update_sql = normalize_whitespace("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?")

    # Access both calls to `execute()` using `call_args_list`
    actual_select_sql = normalize_whitespace(mock_cursor.execute.call_args_list[0][0][0])
    actual_update_sql = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    assert actual_select_sql == expected_select_sql, "The SELECT query did not match the expected structure."
    assert actual_update_sql == expected_update_sql, "The UPDATE query did not match the expected structure."

    # Ensure the correct arguments were used in both SQL queries
    expected_select_args = (1,)
    expected_update_args = (1,)

    actual_select_args = mock_cursor.execute.call_args_list[0][0][1]
    actual_update_args = mock_cursor.execute.call_args_list[1][0][1]

    assert actual_select_args == expected_select_args, f"The SELECT query arguments did not match. Expected {expected_select_args}, got {actual_select_args}."
    assert actual_update_args == expected_update_args, f"The UPDATE query arguments did not match. Expected {expected_update_args}, got {actual_update_args}."


def test_update_boxer_stats_bad_result(mock_cursor):
    """Testing error when inputting a non-win/loss result
    
    """
    mock_cursor.fetchone.return_value = True

    with pytest.raises(ValueError, match="Invalid result: hey. Expected 'win' or 'loss'."):
        update_boxer_stats(999, 'hey')


def test_update_boxer_stats_bad_id(mock_cursor):
    """Testing error when inputting a nonexistent boxer
    
    """
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Boxer with ID 999 not found"):
        update_boxer_stats(999, 'win')
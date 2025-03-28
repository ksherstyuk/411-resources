from dataclasses import dataclass
import logging
import sqlite3
from typing import Any, List

from boxing.utils.sql_utils import get_db_connection
from boxing.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Boxer:
    id: int
    name: str
    weight: int
    height: int
    reach: float
    age: int
    weight_class: str = None

    def __post_init__(self):
        self.weight_class = get_weight_class(self.weight)  # Automatically assign weight class


def create_boxer(name: str, weight: int, height: int, reach: float, age: int) -> None:
    """Creates a new boxer in the boxers table.

    Args:
        name (str): The boxer's name.
        weight (int): The boxer's weight (in lb).
        height (int): The boxer's height (in inches).
        reach (float): The boxer's reach (in inches).
        age (int): The boxer's age (in years).

    Raises:
        ValueError: If any field is invalid.
        sqlite3.IntegrityError: If a boxer with the same name already exists.
        sqlite3.Error: For any other database errors.

    """
    logger.info(f"Received request to create a boxer: {name} - ({weight})")

    if weight < 125:
        logger.warning("Invalid weight provided.")
        raise ValueError(f"Invalid weight: {weight}. Must be at least 125.")
    if height <= 0:
        logger.warning("Invalid height provided.")
        raise ValueError(f"Invalid height: {height}. Must be greater than 0.")
    if reach <= 0:
        logger.warning("Invalid reach provided.")
        raise ValueError(f"Invalid reach: {reach}. Must be greater than 0.")
    if not (18 <= age <= 40):
        logger.warning(f"Invalid age provided: {age}")
        raise ValueError(f"Invalid age: {age}. Must be between 18 and 40.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Check if the boxer already exists (name must be unique)
            cursor.execute("SELECT 1 FROM boxers WHERE name = ?", (name,))
            if cursor.fetchone():
                logger.warning(f"Invalid name provided (boxer already exists): {name}")
                raise ValueError(f"Boxer with name '{name}' already exists")

            cursor.execute("""
                INSERT INTO boxers (name, weight, height, reach, age)
                VALUES (?, ?, ?, ?, ?)
            """, (name, weight, height, reach, age))
            conn.commit()

            logger.info(f"Boxer successfully added: {name} - ({weight})")

    except sqlite3.IntegrityError:
        logger.error(f"Invalid name provided (boxer already exists): {name}")
        raise ValueError(f"Boxer with name '{name}' already exists")

    except sqlite3.Error as e:
        logger.error(f"Database error while creating boxer: {e}")
        raise e


def delete_boxer(boxer_id: int) -> None:
    """Permanently deletes a boxer from the catalog.

    Args:
        boxer_id (int): The ID of the boxer to delete.

    Raises:
        ValueError: If the boxer with the given ID does not exist.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.warning(f"Attempted to delete non-existent boxer with ID {boxer_id}")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            cursor.execute("DELETE FROM boxers WHERE id = ?", (boxer_id,))
            conn.commit()

            logger.info(f"Successfully deleted boxer with ID {boxer_id}")

    except sqlite3.Error as e:
        logger.error(f"Database error while deleting boxer: {e}")
        raise e


def get_leaderboard(sort_by: str = "wins") -> List[dict[str, Any]]: 
    """Returns a leaderboard containing all boxers sorted by an inputted success parameter.

    Args:
        sort_by (str): By default, "wins" (valid inputs "wins" or "win_pct"); indicates sorting parameter

    Returns:
        An list ordered by wins containing dictionaries corresponding to each existing boxer (containing their information).

    Raises:
        ValueError: If an invalid sorting parameter is provided.
        sqlite3.Error: If any database error occurs.

    """
    query = """
        SELECT id, name, weight, height, reach, age, fights, wins,
               (wins * 1.0 / fights) AS win_pct
        FROM boxers
        WHERE fights > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error(f"Invalid sorting parameter: {sort_by})")
        raise ValueError(f"Invalid sort_by parameter: {sort_by}")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to get leaderboard, sorted by: {sort_by}")
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            boxer = {
                'id': row[0],
                'name': row[1],
                'weight': row[2],
                'height': row[3],
                'reach': row[4],
                'age': row[5],
                'weight_class': get_weight_class(row[2]),  # Calculate weight class
                'fights': row[6],
                'wins': row[7],
                'win_pct': round(row[8] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(boxer)

        logger.info(f"Leaderboard sorted by {sort_by} successfully retrieved")
        return leaderboard

    except sqlite3.Error as e:
        logger.error(f"Database error while getting leaderboard: {e}")
        raise e


def get_boxer_by_id(boxer_id: int) -> Boxer:
    """Retrieves a boxer from the catalog by their boxer ID.

    Args:
        boxer_id (int): The ID of the boxer to retrieve.

    Returns:
        Boxer: The Boxer object corresponding to the boxer_id.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer with ID {boxer_id}")
            
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE id = ?
            """, (boxer_id,))

            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                return boxer
            else:
                logger.warning(f"Boxer with ID {boxer_id} not found.")
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer with ID '{boxer_ID}': {e}")
        raise e


def get_boxer_by_name(boxer_name: str) -> Boxer:
    """Retrieves a boxer from the catalog by their boxer ID.

    Args:
        boxer_name (int): The name of the boxer to retrieve.

    Returns:
        Boxer: The Boxer object corresponding to the name provided.

    Raises:
        ValueError: If the boxer is not found.
        sqlite3.Error: If any database error occurs.

    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            logger.info(f"Attempting to retrieve boxer named {boxer_name}")
            
            cursor.execute("""
                SELECT id, name, weight, height, reach, age
                FROM boxers WHERE name = ?
            """, (boxer_name,))
            row = cursor.fetchone()

            if row:
                boxer = Boxer(
                    id=row[0], name=row[1], weight=row[2], height=row[3],
                    reach=row[4], age=row[5]
                )
                logger.info(f"Boxer '{boxer_name}' found")
                return boxer
            else:
                logger.warning(f"Boxer '{boxer_name}' not found")
                raise ValueError(f"Boxer '{boxer_name}' not found.")

    except sqlite3.Error as e:
        logger.error(f"Database error while retrieving boxer '{boxer_name}': {e}")
        raise e


def get_weight_class(weight: int) -> str:
    """Retrieves appropriate weight class corresponding to a given weight.

    Args:
        weight (int): The boxer's weight (in lb).
    
    Returns:
        str: The weight class corresponding to the weight input.

    Raises:
        ValueError: If the provided weight is below 125 lb.

    """
    logger.info(f"Received request to identify weight class corresponding to {weight} lbs")

    if weight >= 203:
        weight_class = 'HEAVYWEIGHT'
    elif weight >= 166:
        weight_class = 'MIDDLEWEIGHT'
    elif weight >= 133:
        weight_class = 'LIGHTWEIGHT'
    elif weight >= 125:
        weight_class = 'FEATHERWEIGHT'
    else:
        logger.error(f"Invalid weight: {weight}. Weight must be at least 125 lbs")
        raise ValueError(f"Invalid weight: {weight}. Weight must be at least 125.")
    
    logger.info(f"Weight class successfully identified as {weight_class}")
    return weight_class


def update_boxer_stats(boxer_id: int, result: str) -> None:
    """Update's the status of a boxer's game to reflect if they won or lost.

    Args:
        boxer_id (int): The ID corresponding to the boxer.
        result (str): The outcome of the game (win/loss)
    
    Raises:
        ValueError: If the the provided result is not a win/loss, or if the boxer with the provided ID does not exist.
        sqlite3.Error: If any database error occurs.

    """
    logger.info(f"Received request to identify update boxer with ID '{boxer_id}' to reflect result: '{result}'")

    if result not in {'win', 'loss'}:
        logger.error(f"Invalid result: {result}. Expected 'win' or 'loss'.")
        raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM boxers WHERE id = ?", (boxer_id,))
            if cursor.fetchone() is None:
                logger.error(f"Boxer '{boxer_id}' not found") #should halt execution
                raise ValueError(f"Boxer with ID {boxer_id} not found.")

            if result == 'win':
                cursor.execute("UPDATE boxers SET fights = fights + 1, wins = wins + 1 WHERE id = ?", (boxer_id,))
            else:  # result == 'loss'
                cursor.execute("UPDATE boxers SET fights = fights + 1 WHERE id = ?", (boxer_id,))

            logger.info(f"Successfully updated boxer's status to: {result}")
            conn.commit()

    except sqlite3.Error as e:
        logger.error(f"Database error while updating boxer status: {e}")
        raise e

import logging
import math
from typing import List

from boxing.models.boxers_model import Boxer, update_boxer_stats
from boxing.utils.logger import configure_logger
from boxing.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)


class RingModel:
    def __init__(self):
        """Initializes an empty RingModel instance with no boxers in the ring.
        """
        self.ring: List[Boxer] = []
        logger.info("Initialized empty ring")

    def fight(self) -> str:
        """Simulates a fight between the two boxers in the ring.

        The winner is determined based on a skill-based probability using a logistic function
        and a random number generator. The loser and winner stats are updated accordingly.

        Returns:
            str: The name of the winning boxer.

        Raises:
            ValueError: If fewer than two boxers are in the ring.
        """
        logger.info("Starting a fight between two boxers")
        if len(self.ring) < 2:
            logger.warning("Cannot start fight — fewer than two boxers in ring")
            raise ValueError("There must be two boxers to start a fight.")

        boxer_1, boxer_2 = self.get_boxers()
        logger.info(f"Boxers in ring: {boxer_1.name} vs {boxer_2.name}")

        skill_1 = self.get_fighting_skill(boxer_1)
        skill_2 = self.get_fighting_skill(boxer_2)

        # Compute the absolute skill difference
        # And normalize using a logistic function for better probability scaling
        delta = abs(skill_1 - skill_2)
        normalized_delta = 1 / (1 + math.e ** (-delta))

        random_number = get_random()
        logger.debug(f"Skill delta: {delta}, Normalized delta: {normalized_delta}, Random: {random_number}")

        if random_number < normalized_delta:
            winner = boxer_1
            loser = boxer_2
        else:
            winner = boxer_2
            loser = boxer_1
        logger.info(f"{winner.name} wins the fight")

        update_boxer_stats(winner.id, 'win')
        update_boxer_stats(loser.id, 'loss')

        self.clear_ring()
        logger.info("Ring cleared after fight")

        return winner.name

    def clear_ring(self):
        """Clears all boxers from the ring.
        """
        logger.info("Clearing the ring")
        if not self.ring:
            return
        self.ring.clear()

    def enter_ring(self, boxer: Boxer):
        """Adds a boxer to the ring if there is space and the input is valid.

        Args:
            boxer (Boxer): The boxer to enter the ring.

        Raises:
            TypeError: If the input is not an instance of Boxer.
            ValueError: If the ring already has two boxers.
        """
        logger.info(f"Attempting to enter boxer: {boxer}")
        if not isinstance(boxer, Boxer):
            logger.error(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")
            raise TypeError(f"Invalid type: Expected 'Boxer', got '{type(boxer).__name__}'")

        if len(self.ring) >= 2:
            logger.warning("Ring is full. Cannot add more boxers")
            raise ValueError("Ring is full, cannot add more boxers.")

        self.ring.append(boxer)

    def get_boxers(self) -> List[Boxer]:
        """Returns the list of current boxers in the ring.

        Returns:
            List[Boxer]: A list of Boxer objects currently in the ring.
        """
        if not self.ring:
            pass
        else:
            pass
        
        logger.debug(f"Returning boxers in ring: {[b.name for b in self.ring]}")
        return self.ring

    def get_fighting_skill(self, boxer: Boxer) -> float:
        """Calculates the fighting skill of a boxer based on weight, name length, reach, and age.

        Args:
            boxer (Boxer): The boxer for whom to calculate the skill.

        Returns:
            float: The computed fighting skill score.
        """
        logger.debug(f"Calculating skill for boxer {boxer.name}: weight={boxer.weight}, reach={boxer.reach}, age={boxer.age}")
        # Arbitrary calculations
        age_modifier = -1 if boxer.age < 25 else (-2 if boxer.age > 35 else 0)
        skill = (boxer.weight * len(boxer.name)) + (boxer.reach / 10) + age_modifier

        logger.debug(f"Skill computed: {skill}")
        return skill

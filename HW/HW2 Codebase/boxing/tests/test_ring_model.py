from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer
from unittest.mock import patch
import pytest

def test_enter_ring_success():
    """
    Test that a boxer can enter the ring successfully
    """
    ring = RingModel()
    boxer = Boxer(1, "Ali", 160, 70, 75.0, 28)
    ring.enter_ring(boxer)
    assert len(ring.ring) == 1   #Ring should contain 1 boxer if successful

def test_enter_ring_type_error():
    """
    Test that a non-boxer cannot enter the ring
    """
    ring = RingModel()
    with pytest.raises(TypeError):
        ring.enter_ring("NotABoxer")  #Should fail due to invalid type of instance unless it is a boxer

def test_enter_ring_full():
    """
    Test to see that only two boxers are in the ring at a time
    and throws an error if mor etry to enter
    """
    ring = RingModel()
    ring.enter_ring(Boxer(1, "A", 160, 70, 75.0, 28))
    ring.enter_ring(Boxer(2, "B", 160, 70, 75.0, 28))
    with pytest.raises(ValueError):
        ring.enter_ring(Boxer(3, "C", 160, 70, 75.0, 28))  #Exceeds the capacity of the ring

def test_clear_ring():
    """
    Tests that clear_ring() successfully clears the ring of all boxers
    """
    ring = RingModel()
    ring.enter_ring(Boxer(1, "Ali", 160, 70, 75.0, 28))
    ring.clear_ring()
    assert ring.ring == []  #Should be empty if clear_ring is successful

def test_get_boxers():
    """
    Tests that get_boxers() returns the current boxers in the ring
    """
    ring = RingModel()
    boxer = Boxer(1, "Ali", 160, 70, 75.0, 28)
    ring.enter_ring(boxer)
    assert ring.get_boxers() == [boxer]  #List of boxers in the ring

def test_get_fighting_skill():
    """
    Tests that get_fighting_skill() returns the fighting skill of the boxers in the ring
    """
    ring = RingModel()
    boxer = Boxer(1, "Ali", 160, 70, 75.0, 28)
    skill = ring.get_fighting_skill(boxer)
    assert isinstance(skill, float)  #Raises assertation error if returned value(here, skill) is not a float


@patch("boxing.models.ring_model.get_random", return_value=0.3)
@patch("boxing.models.ring_model.update_boxer_stats")
def test_fight_success(mock_update, mock_random):
    """
    Test the fight method to ensure it returns a valid winner and updates stats
    Mocks out randomness and stat update DB calls.
    """
    ring = RingModel()
    ring.enter_ring(Boxer(1, "Ali", 160, 70, 75.0, 28))
    ring.enter_ring(Boxer(2, "Tyson", 190, 72, 76.0, 30))

    winner = ring.fight()
    assert winner in ["Ali", "Tyson"]  #Winner should be either "Ali" or "Tyson"
    assert mock_update.call_count == 2 #Both winner and loser stats should be updated


def test_fight_with_insufficient_boxers():
    """
    Test that fight() raises a ValueError when fewer than 2 boxers are in the ring.
    """
    ring = RingModel()
    ring.enter_ring(Boxer(1, "Solo", 160, 70, 75.0, 28))

    with pytest.raises(ValueError, match="There must be two boxers to start a fight."):   #Should raise error if attempting to fight with less than 2 boxers
        ring.fight()


@patch("boxing.models.ring_model.get_random", return_value=0.5)
@patch("boxing.models.ring_model.update_boxer_stats")
def test_fight_with_equal_skills(mock_update, mock_random):
    """
    Tests the fight method when both boxers have equal fighting skills
    Ensures that a winner is selected and both winner and loser stats are updated.
    """
    ring = RingModel()

    #Identical boxer stats
    boxer1 = Boxer(1, "Twin1", 160, 70, 75.0, 28)
    boxer2 = Boxer(2, "Twin2", 160, 70, 75.0, 28)

    ring.enter_ring(boxer1)
    ring.enter_ring(boxer2)

    winner = ring.fight()

    assert winner in ["Twin1", "Twin2"]   #Should be 1 winner and 1 loser
    assert mock_update.call_count == 2    #Both stats should be updated
from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer
import pytest

def test_enter_ring_success():
    ring = RingModel()
    boxer = Boxer(1, "Ali", 160, 70, 75.0, 28)
    ring.enter_ring(boxer)
    assert len(ring.ring) == 1
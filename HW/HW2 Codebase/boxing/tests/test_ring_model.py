from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer
import pytest

def test_enter_ring_success():
    ring = RingModel()
    boxer = Boxer(1, "Ali", 160, 70, 75.0, 28)
    ring.enter_ring(boxer)
    assert len(ring.ring) == 1

def test_enter_ring_type_error():
    ring = RingModel()
    with pytest.raises(TypeError):
        ring.enter_ring("NotABoxer")

def test_enter_ring_full():
    ring = RingModel()
    ring.enter_ring(Boxer(1, "A", 160, 70, 75.0, 28))
    ring.enter_ring(Boxer(2, "B", 160, 70, 75.0, 28))
    with pytest.raises(ValueError):
        ring.enter_ring(Boxer(3, "C", 160, 70, 75.0, 28))
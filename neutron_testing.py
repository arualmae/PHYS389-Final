import pytest

from neutron import Neutron

"""
This file is used to perform unit tests on key functions in the neutron class. Ensure all files are run in the same directory; perform the test (function on VSCode) by writing in the terminal:

pythom -m pytest neutron_testing.py
"""

neutron = Neutron()

def test_energy_Speed():
    neutron.energy = 1    
    assert neutron.energySpeed() == 1.38e6

def test_fission_Event():
    neutron.fissionEvent()
    assert neutron.absorbed == True

def test_capture_Event():
    neutron.captureEvent()
    assert neutron.absorbed == True

def test_scatter_event_U():
    neutron.energy = 1
    neutron.scatterEventU()
    assert neutron.energy < 1

def test_up_Scatter_Event_H():
    neutron.energy = 0.025
    neutron.scatterEventH()
    assert neutron.energy > 0.025

def test_down_Scatter_Event_H():
    neutron.energy = 1
    neutron.scatterEventH()

    assert neutron.energy < 1


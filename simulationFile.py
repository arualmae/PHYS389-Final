import numpy as np
import matplotlib.pyplot as plt
import pickle

from neutron import Neutron
from reactor import Reactor
import copy

"""
This file takes in the desired starting parameters and runs and instance of the simulation. We create two reactors to create appropriate data ranges for different graphs.

The data for the given parameters take approximately 60 seconds to collect for a Ryzen-7 Processor laptop with 16G RAM.
"""

# This data set characterises the random walk graph. Weere the variable thermal is set to True (its default is False) neutrons produced in a fission event will be given an energy 0.025. The report decsribed why this is appropriate here.

# This will store the parameters of data collected, passing this list to the plotting file.
parameters = []

# These are the recommended parameters for the random walk graph: 
neutronCount = 30
stepCount = 10
neutronList = []

parameters.append([neutronCount, stepCount])

reactor = Reactor(neutronCount, stepCount, thermal=True)
reactor.startUp()

neutrons = reactor.neutronData()

np.save(F"neutronData_{neutronCount}_{stepCount}", neutrons, allow_pickle = True)

filehandler = open(F"reactor_{neutronCount}_{stepCount}.obj", 'wb') 
pickle.dump(reactor, filehandler)



# These are the recommended parameters for: the thermal energy distribution (2.); neutron energy as a function of steps (3.); average neutron energy for a given step (4.); k_eff and reactivity plot as function of step count (5.) 

# The variable names are redundance once a file has been saved; we used the same ones and overwrite them
neutronCount = 100
stepCount = 400
neutronList = []

parameters.append([neutronCount, stepCount])

reactor = Reactor(neutronCount, stepCount)
reactor.startUp()

neutrons = reactor.neutronData()

# We save the data with names corresponding to initialNeutron and stepCounts. 
np.save(F"neutronData_{neutronCount}_{stepCount}", neutrons, allow_pickle = True)

filehandler = open(F"reactor_{neutronCount}_{stepCount}.obj", 'wb') 
pickle.dump(reactor, filehandler)

# Addition data files may be created by copy-pasting this save format and adjusting the neutron/step count as desired. The names will automatically adjust.
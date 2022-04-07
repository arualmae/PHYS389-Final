import numpy as np
import copy

from sympy import true

"""This class creates an instance of the reactor, characterised by an initial neutron count, and desired step count. Neutron motion triggered by the .startUp() method: this generates a list of the desired initial neutrons and iterates over them for as many steps as requested. Neutrons are added or removed from this list as fission and absorbtion events demand.

We model the reactor as a homogeneous mixture of 61% light water and 39% U02 fuel; the latter is enriched to 4% U235 content.

The reactor takes in a parameter 'thermal' which is a boolean value indicating whether neutrons produced in a fission event have a properly distributed energy, or whether they are uniformly themal (given E = 0.025)
"""

# Importing the neutron class
from neutron import Neutron

class Reactor():
    def __init__(

        self,
        neutronStart = 1,
        stepCount = 100,
        k_eff = 1,
        dimensions = [10,10],
        thermal = False
        ):

        self.neutronStart = neutronStart
        self.stepCount = stepCount
        self.neutronList = []
        self.newNeutronList = []
        self.k_eff = k_eff
        self.energyList = []
        self.k_effData = [1]
    
        self.thermal = thermal
        self.dimensions = dimensions

    def generateList(self):
        # This generates a list of the starting neutrons in the reactor, also storing their initial energy and speed. energyHolder is used to contain all the information about a single step in one list, such that the energyList can be indexed by the step in the simulation.
        energyHolder = []

        for i in range(self.neutronStart):

            neutron = Neutron(name = F"neutron{i+1}")
            neutron.setPosition(self.dimensions[0], self.dimensions[1])
            
            self.neutronList.append(neutron)

            energyHolder.append([neutron.energy, neutron.energySpeed()])  

        self.energyList.append(energyHolder) 

            
            

    def startUp(self):

        # This function generates the intial list of neutrons and sends them off on their random walk. Data corresponding to the speed and energy of the neutrons in a given step is stored in the same manner as generatList (i.e. with an energyHolder collating the energies of neutrons in a given step, before this is appended to the total list).
        
        self.generateList()

        for i in range(self.stepCount):

            # In each step we want to check how many neutrons are added to the system from fission, only adding them to the reactor neutron list after all neutrons in original list have had their steps evaluated. That is, a fission-produced neutron only begin's its random walk in the count index after it has been generated. We hold the new neutron information in the new_neutrons list.
            new_neutrons = []
            energyHolder = []

            # These parameters are used to calculate the reactivity of the system, corresponding to gain in neutrons and loss of neutrons through a given step, respectiely.
            nGain = 0
            nLoss = 0
            oldnLoss = 0

            # We begin iterating over the neutron list; if a neutron is absorbed, it is passed over; if not, it is allowed to take a step in its walk.
            for neutron in self.neutronList:               
                
                if not neutron.absorbed: 

                    neutron.randomStep() 
                    
                    energyHolder.append([neutron.energy, neutron.energySpeed()])   

                    # This checks if a neutron has fissioned, collecting the new neutron data if True.
                    if neutron.eventType == "fission":

                        # We lose the incident fission neutron and gain however many are produced in the fission event.
                        nGain += len(neutron.newNeutronEnergies)
                        nLoss += 1

                        # Here we create the neutron objects produced in the fission; the hashed-out statement would create the particles with equal, thermal energy 0.025eV. The correspodning implement statement creates them with distributed energies. It is left in to be able to produced the graph given in the report.

                        for j in neutron.newNeutronEnergies:
                            if self.thermal == True:
                                new_neutrons.append(Neutron(startPos = np.array(neutron.pos, dtype=float), name = F"neutron{len(self.neutronList) + len(new_neutrons) + 1}"))
                            else:
                                new_neutrons.append(Neutron(startPos = np.array(neutron.pos, dtype=float), energy=j ,name = F"neutron{len(self.neutronList) + len(new_neutrons) + 1}"))
                    
                    elif neutron.eventType == "capture":
                        nLoss += 1

                
            # This adds the new neutrons produced in a given fission event to the total new neutrons added to the reactor after a step is fully evaluated.
            for newNeutron in new_neutrons:
                self.neutronList.append(newNeutron)


            oldnLoss = copy.copy(nLoss) 

            self.calcCrit(nGain, oldnLoss)
            self.k_effData.append(self.k_eff)

            self.energyList.append(energyHolder)   

    
    
    # Calculate values of k_eff; the if statement mitigates against division by zero
    def calcCrit(self, gain, loss):
        if gain and loss != 0:
            self.k_eff = gain/loss

    # Returns the a list of neutrons which have existed at any point in the simulation. Each neutron has a memory of its path.
    def neutronData(self):
        return self.neutronList
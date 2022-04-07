from random import seed
import numpy as np
import math 


"""This class creates an instance of the neutron, with a randomised starting position and fixed thermal energy (0.025) to ensure the recactor is super-critcal for low initial neutron counts. Neutron motion is characterised by a random walk, under the assumption that the particles are perfectly point like and moving in a homogeneous medium."""


# Importing the distributions for prompt neutron energy, cross sections, and moderation energy.
from creatingDistribution import newPromptNeutronCDF, crossSections, moderation

# All values are intialised in SI units, with energy in eV. Position is tracked in cm and hence velocities and speeds are given in cm/s, as is convention for reactor physics.
class Neutron():
    def __init__(
        self,       
        name = "neutron",
        parent = "reactor",
        energy = 0.025,
        time = 0, 
        
        startPos = np.array([0,0], dtype=float),
        startVel = np.array([0,0], dtype=float),

        eventCount = 0,
        absorbed = False
        ):

        self.name = name
        self.parent = parent
        self.energy = energy
        self.time = time
        self.speed = self.energySpeed() 
        
        self.eventType = None
        self.eventCount = eventCount
        
        self.pos = np.array(startPos, dtype=float)
        self.vel = np.array(startVel, dtype=float)

        self.posDataX = [self.pos[0]]
        self.posDataY = [self.pos[1]]
    
        self.energyData = []
        self.absorbed = absorbed

        self.sample = 0
        self.angle = 0


    # Sets a random seed
    np.random.seed(3)


# Sets the position of a neutron within set of dimensions. This is determined in the reactor class and called through this function during initialisation.
    def setPosition(self, dimensionX = 10, dimensionY = 10):
        self.pos[0] = np.random.uniform(0, dimensionX)
        self.pos[1] = np.random.uniform(0, dimensionY)
        #self.vel[0] = np.random.uniform(0,10)
        #self.vel[1] = np.random.uniform(0,10)
        self.posDataX = [self.pos[0]]
        self.posDataY = [self.pos[1]]


    # The functions which follow sample a random angle, and calculate the speed of a neutron. The speed conversion takes energies in eV and outputs speeds in cm/s.
    def randomDirection(self):
        return np.random.uniform(0, 2*math.pi)

    def energySpeed(self):
        return 1.38e6*self.energy**(1/2)


    # This function initialises a random step, and triggers the corresponding event.
    def randomStep(self):
    
        # We first check that our neutron is in the computational range; if its energy falls too low it may no longer participate in the random walk. 
        if self.energy > 1e-5:

            # We calculate the total macroscopic cross-section corresponding to a neutrons energy: the sum of total U235 and H-1 cross-sections scaled to desired proportions.
            sigma = crossSections[3](self.energy) + crossSections[4](self.energy)

            # If a neutron's previous step was a scatter, it will already have a new angle characterising its next step since this is required to define the change in energy brought about by the scattering.
            if self.eventType != "scatterU":
                self.angle = self.randomDirection()
            
            self.sample = np.random.exponential(scale = (1/sigma))
            self.speed = self.energySpeed()

            # The neutron's position and velocity is updated and so are the corresponding histories.
            self.pos[0] = self.pos[0] + self.sample*np.cos(self.angle) 
            self.pos[1] = self.pos[1] + self.sample*np.sin(self.angle)
        
            self.vel[0] = self.speed*np.cos(self.angle) 
            self.vel[1] = self.speed*np.sin(self.angle)

            self.posDataX.append(self.pos[0])
            self.posDataY.append(self.pos[1])

            # Since a particle's energy is characterised by its previous step, we only now update it's energy list.
            self.energyData.append(self.energy)
    
            self.time += self.sample/self.speed
            
            # This takes our new parameters and 
            self.chooseEvent()
        
        else:
            self.absorbed = True


    def setCrossSection(self):
        # This function iterates over the list of cross-section functions corresponding to different reactor events, calculating the values for a given energy.

        tempCrossSections = []

        for function in crossSections:
            tempCrossSections.append(function(self.energy))
        
        return tempCrossSections    


    def chooseEvent(self):
        # This method is triggered following a random step; it chooses a neutron event based on probabilties created by a neutron's cross-section.
        
        self.eventCount += 1
        
        num = np.random.random()

        # Unpacking the calculated cross-section values: fission, capture, U-scattering, total U and H-scattering respectively. A random number decides the event based upon weighted probabilties given by these cross-sectopms. A method correspondong to the chosen event is triggered.
        F,C,S,T,H = self.setCrossSection() 

        if 0 <= num < F/(T+H):
            self.eventType = "fission"

            self.fissionEvent()

        elif F/(T+H) <= num < (F+C)/(T+H):
            self.eventType = "capture"

            self.captureEvent()

        elif (F+C)/(T+H) <= num < (F+C+S)/(T+H):
            self.eventType = "scatterU"

            self.scatterEventU()

        # We coose else rather than a final elif here to ensure the probabilities of each event occuring sum to one, accounting for rounding errors.
        else: 
            self.eventType = "scatterH"
            self.scatterEventH()
        

    def captureEvent(self):
        self.absorbed = True    
        
    def fissionEvent(self):
        
        # This function chooses the number of prompt neutrons produced in a fission event and assigns them an energy, characterised by the prompt neutron distribution.
        self.absorbed = True  
        self.newNeutronEnergies = []

        # We create a list of new neutron energies as ab object variable, so we can assign the correct parent and position to these new neutrons.
        for i in range(np.random.randint(1,3)):
            rand = np.random.random()
            self.newNeutronEnergies.append(newPromptNeutronCDF(rand))


    def scatterEventU(self):
        # In order to know the energy of the neutron as a consequence of scattering, we must preemptively set a new, randomly generated angle. This angle will characterise its next step in the walk: it will NOT be regenerated at the next step.

        self.angle = self.randomDirection()
        alpha = (234/236)**2
        ratio = (1/2)*(1 + alpha + (1-alpha)*np.cos(self.angle))
        self.energy = ratio*self.energy


    def scatterEventH(self):

        # moderation gives a list of four functions characterising interpolated down and up-scattering. We enact function corresponding to a particle's energy: for lower-energy neutrons in the thermal range we implement up-scattering; for high-energy neutrons we implement downscattering. We assume the reactor T = 600 and take the threshold energy to be approx kT.
        rand = np.random.random()
    
        if self.energy < 0.05:
            ratio = moderation[1](rand) 
        else:
            ratio = moderation[0](rand)

        self.energy = ratio*self.energy

        
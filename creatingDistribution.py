import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate, special
from scipy.stats import norm
import csv
import matplotlib.colors as mcolors

"""
This file will serve to create any distributions, or deal with any data files required for the neutron class. This involves:

1. Prompt neutron distribution and CDF interpolation
2. Cross Section interpolation
3. Neutron Moderator CDF interpolation

It is not required to run this file prior to simulationFile.py; the simulation will be generated as necessary by neutron class objects.
"""


### 1. Prompt Neutron Distribution ###

# Given a distribution which characterises the probability of the production of a variety of energies, we define corresponding conversion factors and energies to calculate the distribuiton over

MeV = 1e6
energies = np.arange(0, 12e6, 1e2)

# The method choices correpsond to "Watt" or "Cranberg", enacting the corresponding distribution. These are very similar, only differing in choices of constants

method = "Watt"

def promptNeutronPDF(E):
    if method == "Watt":
        return 0.484*np.sinh((2*E/MeV)**(1/2))*np.exp(-E/MeV)
    elif method == "Cranberg":
        return 0.4527*np.sinh((2.29*E/(MeV))**(1/2))*np.exp(-E/(0.965*MeV))

def calcPromptNeutronCDF(energies):
    
    probs = []
    
    for energy in energies:
        probs.append(promptNeutronPDF(energy))

    sumProbs = sum(probs)
    promptNeutronCDF = np.cumsum([x/sumProbs for x in probs])

    return promptNeutronCDF

# Where the cdf is by definition a one-to-one function, we may invert the interpolation such that inputting a random number [0,1) to the resulting function will return an energy.

def interPromptNeutronCDF(energies):
    func = interpolate.interp1d(calcPromptNeutronCDF(energies), energies)
    return func

newPromptNeutronCDF = interPromptNeutronCDF(energies)

"""
plt.figure(1)
plt.plot(energies, calcPromptNeutronCDF(energies))
plt.show()
"""


### 2. Cross Section Calculations

# We define values to convert microscopic cross sections (stored in the csv files read into the paper), to macroscopic cross sections in cm^-2. Hence, all lengths in the reactor are measured in these units.

# It is convenient in this case to hold the function in a single place; the crossSections list is iterated over, with the string held at each index overwritten by its corresponding interpolated function. Here, we maintain the interpolation order, since we want to input an energy (x-axis) and recieve a cross-section (y-axis).

def makeCrossSections():
    
    N_U = 9.48e20 * .39
    N_H = 66.7e21 * .61
    
    barnCm = 1e-24

    crossSections = ["F","C","S","T","H"]
    
    NumDensity = [N_U, N_U, N_U, N_U, N_H]


    for i in range(len(crossSections)):
        energies=[]
        crossSection = []
        
        with open(F"crossSection{crossSections[i]}.csv", "r") as file:
            read = csv.reader(file, quoting=csv.QUOTE_NONNUMERIC)
            
            for row in read:
                energies.append(row[0]*MeV)
                crossSection.append(row[1]*barnCm*NumDensity[i])
        
        crossSections[i]= interpolate.interp1d(energies, crossSection)
    
    return crossSections

crossSections = makeCrossSections()



### Neutron Moderator Interpolation

# We implment four scattering distributions: one up-scattering and three down-scattering.

# Details of each of these are given in the report.

#Defining the Boltzmann constant (in eV)
k = 8.617333262e-5


def moderatorFuncDown(ePrime, temp):
    return special.erf((ePrime/(k*temp))**(1/2))

def moderatorFuncUp(e, ePrime, temp):
    return (np.exp((e-ePrime)/(k*temp)))*special.erf((e/(k*temp))**(1/2))


def calcModeratorCDF(temp, method):

    en = 1e-3
    # Here en denotes incident energy, and enPrime denotes the outgoing energy. The distribution is characterised by the ratio of these values, where one is held constant (en) and the other is varied (enPrime), to get a range of x-values (0,1].
    if method == "upScatter":
        
        enPrime = np.arange(1e-3, 4e-3, 1e-7)

        ratio = []
        enDensity = []

        for energy in enPrime:
            
            ratio.append(energy/en)
            enDensity.append(moderatorFuncUp(en, energy, temp))

        # The energy densities are normalised and the corresponing cdf is created.

        normalEnDensity = np.array(enDensity)/sum(enDensity)

    else:
        en = 1e-3
        enPrime = np.arange(1e-7, 1e-3, 1e-7)

        ratio = []
        enDensity = []

        for energy in enPrime:
            
            ratio.append(energy/en)
            enDensity.append(moderatorFuncDown(energy, temp))

        # The energy densities are normalised and the corresponing cdf is created.

        normalEnDensity = np.array(enDensity)/sum(enDensity)
    
    return ratio, normalEnDensity.cumsum(), enDensity

# This function holds a redundant random number variable to mitigate argument errors when implemented in the neutron class; the corresponding interpolate function requires this parameter.
def averageMod(randNo = 0):
    return (0.9)

def logAvgMod(randNo = 0):
    return np.exp(-0.927)

def runModeratorCDF(temp=600, E=None):

    downScatter = interpolate.interp1d(calcModeratorCDF(temp, "downScatter")[1], calcModeratorCDF(temp, "downScatter")[0], fill_value="extrapolate")
    
    upScatter = interpolate.interp1d(calcModeratorCDF(temp, "upScatter")[1], calcModeratorCDF(temp, "upScatter")[0], fill_value="extrapolate")
   
    avg = averageMod
    
    logAvg = logAvgMod
    
    return  downScatter, upScatter, avg, logAvg

moderation = runModeratorCDF()



# This graph is not necessary to the simulation; it just shows the behaviour of the moderator distribution for a variety of temperatures. Extensions to the project would have me test this but time was up!! We assume a fixed reactor temperature, however the dependence we see here opens to the doors to implmeneting a moderator-temperature dependence, recreating the negative temperature coefficient which characterises the PWR.

"""
temperatures = np.linspace(300, 750, 10)
tempColours = ["brown","red", "orange", "gold", "green", "deepskyblue", "navy", "blueviolet", "violet", "deeppink"]
#temperatures = np.logspace(-1,4, num=5, endpoint=False)

#x1 = np.arange(1, 1.99, 0.01)
x = np.arange(0.01, 0.99, 0.01)
plt.figure(2)

for temperature in temperatures:
    
    plt.plot(x, runModeratorCDF(temperature)[1](x), color=tempColours[np.where(temperatures == temperature)[0][0]])
    plt.plot(x, runModeratorCDF(temperature)[0](x), color=tempColours[np.where(temperatures == temperature)[0][0]])
plt.legend()
plt.show()

#label = F"{temperature}K"
"""
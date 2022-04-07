
import numpy as np
import matplotlib.pyplot as plt
import pickle
import scipy.stats, scipy.optimize


"""
This file plots the graphs of interest for the simulation:

1. The random walk of neutrons in the reactor

2. and 3. The energy distribution of thermal neutrons in the reactor (allowing thermal = (0.01eV, 1eV]) and the corresponding flux distribution.

4. Plotting average energy of neutron as a funtion of steps taken

5. and 6. k_eff and reactivity of reactor as a funcition of stepCount.

7. Distances from a neutron's point of production as a function of step count

All data plotted and printed is given to 3sf.

The data for the given parameters takes approx 60 seconds to run for a AMD Ryzen 7 4800H laptop.
"""

# This was initially brought into the file using "from simulationFile import parameters" however this would cause the simulation file to be run again; hence it is added here for convenience. I had a workaround planned; i didnt have time to implement it!!
parameters = [[30,10],[100,400]]

# Loading in the data created in simulation file
neutronList1 = np.load(F"neutronData_{parameters[0][0]}_{parameters[0][1]}.npy", allow_pickle= True)
neutronList2 = np.load(F"neutronData_{parameters[1][0]}_{parameters[1][1]}.npy", allow_pickle= True)
filehandler1 = open(F"reactor_{parameters[0][0]}_{parameters[0][1]}.obj", 'rb')
filehandler2 = open(F"reactor_{parameters[1][0]}_{parameters[1][1]}.obj", 'rb')  
reactor1 = pickle.load(filehandler1)
reactor2 = pickle.load(filehandler2)


### Plotting 1. Random walk using first set of data

plt.figure(1)
# This line iterates over all neutrons and plots their paths; each colour denotes a single neutron's motion (conceding repetitions).
for neutron in neutronList1:
    plt.plot(neutron.posDataX, neutron.posDataY)

# This line highlights the positon of the starting neutrons in the simulation, to see from where the random walk evolves.
for i in range(reactor1.neutronStart):
    plt.scatter(neutronList1[i].posDataX[0], neutronList1[i].posDataY[0], s=10)

plt.xlabel("x direction (cm)")
plt.ylabel("y direction (cm)")
#plt.savefig(F"randomWalk_{parameters[0][0]}_{parameters[0][1]}.png")
plt.show()



### Plotting 2 and 3. Thermal neutron energy distribution and thermal flux.

# This sets the appropriate range for the *thermal* energy distribution (allowing thermal = (0.01eV, 1eV])
therm_en = []
for i in reactor2.energyList[reactor2.stepCount - 1]:

    if 0.01 < i[0] < 1:
        therm_en.append(i[0])

def maxDistribution(x, a, b):
    return (x**(1/2))*a*np.exp(-b*x)

# Creating the normalised histogram for the energy data
hist, bins = np.histogram(therm_en, bins = "auto", density = True)

# Finding the parameters a and b defined in maxDistribution()
x = np.linspace(0, 1, len(bins)-1)
fitEnergy, pcov = scipy.optimize.curve_fit(maxDistribution, x, hist)

plt.figure(2)
plt.hist(therm_en, bins = "auto", density = True)
plt.plot(x, maxDistribution(x, *fitEnergy), label=F"a = {fitEnergy[0]:.3f}, b = {fitEnergy[1]:.3f} ")
plt.legend()
plt.xlabel("Thermal energy range eV")
plt.ylabel("Normalised histogram data")
#plt.savefig(F"thermalEnergies_{parameters[1][0]}_{parameters[1][1]}.png")
plt.show()

# We carry out the same process for the flux, where flux = nv (n, number of neutrons; v velocity of neutron)
def maxDistribution2(x, a, b):
    return a*np.exp(-b*x)

flux = []
for value in reactor2.energyList[reactor2.stepCount - 1]:
    if 0.01 < value[0] < 1:
        flux.append(value[0]*value[1])

scaledFlux = 1e-6*np.array(flux)

hist, bins = np.histogram(scaledFlux, bins = "auto", density = True)

x = np.linspace(0, 1, len(bins)-1)
fitFlux, pcov = scipy.optimize.curve_fit(maxDistribution2, x, hist)


plt.figure(3)
plt.hist(scaledFlux, bins = 100, density = True)
plt.plot(x, maxDistribution2(x, *fitFlux), label=F"a = {fitFlux[0]:.3f}, b = {fitFlux[1]:.3f} ")
plt.legend()
plt.xlabel("Thermal flux (cm-2 s-1)")
plt.ylabel("Normalised histogram data")

#plt.savefig(F"thermalFlux_{parameters[1][0]}_{parameters[1][1]}.png")
plt.show()


### 4. Plotting average energy of neutron as a funtion of steps taken
stepCount = []
avgEnergy = []

for step in range(len(reactor2.energyList)):
    stepCount.append(step)
    tempEnergies = []

    for neutron in reactor2.energyList[step]:
        tempEnergies.append(neutron[0])

    avgEnergy.append(np.average(tempEnergies))


mean1, std1 = np.mean(avgEnergy), np.std(avgEnergy)

plt.figure(4)
plt.plot(stepCount, avgEnergy)
plt.hlines(y=mean1, xmin=[0], xmax=[len(stepCount)], color="k", label=F"mean = {mean1:.2E}", lw=1)
plt.hlines(y=[mean1-std1, mean1+std1], xmin=[0], xmax=[len(stepCount)], colors='red', linestyles='--', lw=1, label=F"std = {std1:.2E}")
plt.xlabel("Step count")
plt.ylabel("Avg neutron energy (eV)")
plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
plt.legend()
#plt.savefig(F"avgEnergy_{parameters[1][0]}_{parameters[1][1]}.png")
plt.show()
    
### plotting 5 and 6. k_eff and reactivity of reactor as a funcition of stepCount

def reactivity(k):
    return (k-1)/k

reactivityDat = []
for k in reactor2.k_effData:
    if k == 0:
        reactivityDat.append(None)
    else:
        reactivityDat.append(reactivity(k))

mean2, std2 = np.mean(reactor2.k_effData), np.std(reactor2.k_effData)
mean3, std3 = np.mean(reactivityDat), np.std(reactivityDat)

plt.figure(5)
plt.plot(stepCount, reactor2.k_effData)
plt.hlines(y=mean2, xmin=[0], xmax=[len(stepCount)], color="k", label=F"mean = {mean2:.3}", lw=1)
plt.hlines(y=[mean2-std2, mean2+std2], xmin=[0], xmax=[len(stepCount)], colors='red', linestyles='--', lw=1, label=F"std = {std2:.3}")
plt.xlabel("Step count")
plt.ylabel("value of k_eff")
plt.legend()
#plt.savefig(F"k_eff_{parameters[1][0]}_{parameters[1][1]}.png")
plt.show()

plt.figure(6)
plt.plot(stepCount, reactivityDat)
plt.hlines(y=mean3, xmin=[0], xmax=[len(stepCount)], color="k", label=F"mean = {mean3:.3}", lw=1)
plt.hlines(y=[mean3-std3, mean3+std3], xmin=[0], xmax=[len(stepCount)], colors='red', linestyles='--', lw=1, label=F"std = {std3:.3}")
plt.xlabel("Step count")
plt.ylabel("Reactivity")
plt.legend()
#plt.savefig(F"reactivity_{parameters[1][0]}_{parameters[1][1]}.png")
plt.show()

### Plotting 7. Neutron's change in position as a function of steps in its random walk

# This plot places a scatter point corresponding to the number of steps a neutron undergoes, and the magnitude of its displacement from its initial position. It is currently commented out as it take >5 mins to run.

"""
plt.figure()
for neutron in neutronList2:
    dX = neutron.posDataX[-1] - neutron.posDataX[0]  
    dY = neutron.posDataY[-1] - neutron.posDataX[0] 
    avg = (dX**2 + dY**2)**(1/2)

    plt.scatter(neutron.eventCount, avg, s=1, color="purple")

plt.xlabel("Number of steps")
plt.ylabel("Magnitude of displacement")
plt.show()
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

from neutron import Neutron
from reactor import Reactor

from creatingDistribution import crossSections

"""
This file serves as a testing location for all the distributions implemented in the simulation. We first test the numpy-implemented uniform and exponential distributions given in the neutron class. The remaining distributions are taken from creatingDistirbutions.py. Parameters for the testing are given above each group of tests, with recommended values for key results.
"""

### Testing random walk: exponential distribution of step length and uniform distribution of angles respectively. ###

# Setting up parameters for the testing
testCount = 20000

neutronList = []

angleData = []
lengthData = []


# Creating the neutron list to be iterated over
for i in range(testCount):
    neutron = Neutron(name = F"neutron{i+1}")
    neutronList.append(neutron)


# Preparing the data lists and calculating corresponding statistical values
for neutron in neutronList:
    neutron.randomStep()
    angleData.append(neutron.angle)
    lengthData.append(neutron.sample)


lenMean, lenStd = np.mean(lengthData), np.std(lengthData)
angMean, angStd = np.mean(angleData), np.std(angleData)


# Defining functions characterising the expected distributions, with fitting parameters. The latter function is not implemented here but included for completeness.
def expDistribution(x, a):
    return a*np.exp(-a*x)

def uniformDistribution(a, b):
    return 1/(b-a)


# Plotting uniform distribution
unifX = np.linspace(min(angleData), max(angleData), testCount)
unifY = scipy.stats.uniform.pdf(unifX, scale = 2*angMean)

plt.figure(1)
plt.hist(angleData, bins = "auto", density = True, label = F"Mean = {angMean:.3f}; Std Dev {angStd:.3f}")
plt.plot(unifX, unifY)
plt.xlabel("angle (rads)")
plt.ylabel("normalised histogram")
plt.legend(loc = "lower center")
plt.savefig("angDistribution.png")
plt.show()



# Plotting exponential distribution of step length
expX = np.linspace(min(lengthData), max(lengthData), testCount)
expY = scipy.stats.expon.pdf(expX, scale = lenMean)

# Calculating the macroscopic cross-section used to create the distribution (sigma) to compare against the value taken from the data (dataSigma). 
sigma = crossSections[3](0.025) + crossSections[4](0.025)
dataSigma = 1/lenMean

# Plotting exponential distribution. The hashed out plot line is an alternate plot of the predicted exponenrial distribution; it gives the same output as the previous line.
plt.figure(2)
plt.hist(lengthData, bins = "auto", density=True, label = F"Mean = {lenMean:.3f}; Std Dev {lenStd:.3f}")
plt.plot(expX, expY)
#plt.plot(expX, expDistribution(expX, sigma))

plt.xlabel("step length (cm)")
plt.ylabel("normalised histogram")
plt.legend()
plt.savefig("stepLength.png")
plt.show()



def percentError(obsv, exp):
    return 100 * abs((obsv - exp))/(exp)


print(F"For the step-length distribution, the data-calculated mean is {lenMean:.3f} which corresponds to a rate-parameter/macroscopic cross sections of {dataSigma:.3f}. Comparing to the simulation cross section of {sigma:.3f}, this gives a percentage error of {percentError(dataSigma, sigma):.3f}% for a sample of {testCount} steps.")

print(F"For the angular distribution, the data-calculated mean is {angMean:.3f}, compared to the simulation paramaters of {np.pi:.3f}. This gives a percentage error of {percentError(np.pi, angMean):.3f}% for a sample of {testCount} steps.")

#FIN
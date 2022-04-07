PHYS389 - Laura Ellis

A simple python simulation of the processes in a pressurised water reactor (PWR)

The intention for this code is to simulate two-dimensional neutron motion in a pwr, as a Monte Carlo random walk. Each step in the walk terminates with an event determined by a neutron's energy and corresponding set of cross-sections; these events are fission, neutron-capture, uranium scattering and hydrogen scattering, where the latter acts as the pwr moderator.

The packages required for this simulation are: random, csv, numpy, math, copy, matplotlib, pickle and scipy

The files include:

## neutron.py
## reactor.py

## creatingDistribution.py
## 5 x CSV files of the format crossSectionData{}.csv 

## simulationFile.py
## simulationPlot.py

## distributionTesting.py
## neutron_testing

Because of how the docstrings format on my VSCode, I would recommend alt + z before reading through the simulation


A brief overview of the content of each file.

## The first two files act as the centre of the simulation: classes defining neutron and reactor objects. 

The former contains all of the methods required for a neutron to take its random walk, with a step length characterised by an exponential distribution and angle characterised by a uniform one. For a given energy, the neutron object determines a set of cross-sections which will determine the event that terminates a step. The latter object performs the simulation. It takes in two key parameters: initial neutron count and step count. When the reactor.startUP() method is called a list of initial neutrons are generated and their random walk is triggered. For the range of the step count, the list is iterated over and each neutron will take a step, with neutrons being added or removed as fission and capture events demand.


## creatingDistribution.py and the CSV files of the format crossSectionData{}.csv work together to produce distributions

These files must be in the same folder the simulation is run from.

Given by the ENDF, the latter files are automatically read into the simulation by the creatingDistributions.py file, in order to create a set of functions characterising the cross-section of a neutron, for a variety of processes, interpolated across our energy spectrum.

The former file also creates a prompt neutron distribution and a moderator energy distribution. For the latter four methods are given: three defining down-scattering and one defining up. All of these are returned and read by the neutron class, however only the interpolation methods are run. While intentional - these give the best results, they may be changed by changing the index of down-scattering in neutron.py's scatterEventH method.


## simulationFile.py and simulationPlot.py

These two files collect data and plot the graphs of interest for the simulation, respectively:

simulationFile is set up to collect two sets of data: one corresponding to recommended parameters for the random walk graph; the other collecting data for the remainder. Additional data can be collected by copy-pasting the structure of the save file and changing the initial neutron and step-count parameters.

The graphs produced in simulationPlot.py are:

1. The random walk of neutrons in the reactor
2. and 3. The energy distribution of thermal neutrons in the reactor (allowing thermal = (0.01eV, 1eV]) and the corresponding flux distribution.
4. Plotting average energy of neutron as a function of steps taken
5. and 6. k_eff and reactivity of reactor as a function of stepCount.
7. Distances from a neutron's point of production as a function of step count

The code includes save lines, however these are hashed out to prevent spamming your computer!


## distributionTesting.py
## neutron_testing

These files seek to test the efficacy of the code. The first file performs checks on the random walk to ensure the distribution of step-length and angle are as expected. The latter performs unit tests on methods in the neutron class. It is run from the terminal by inputting the line:

pythom -m pytest neutron_testing.py


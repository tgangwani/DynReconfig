#!/usr/bin/env python3

# Script to generate features for the machine learning model!

# This script runs the pinball (application phase) with the different possible 
# micro-arch parameters, and selects the 'good' configurations. 'Good'
# configurations include the following - 1) the best  one, overall 2) the best
# one, by fixing (turn-by-turn) each parameter to a constant value and varying
# the rest 

import launcher, stats, selection, featureGeneration
import itertools
import sys
import globalvars
from multiprocessing import Process

parameters = list()
parameterNames = list()
binsForRD = globalvars.binsForRD
binsForRob = globalvars.binsForRob
maxChildren = globalvars.maxChildren
# for managing parallelism
processes = list()

# list of all permutations of parameters
permutations = list()
# names of all entries in feature vector
featureNames = list()
# dictionary of appName and goodConfigs for that app 
goodConfigDict = dict()

def addParameter(arg):
  parameters.append(arg)

# define parameters here
addParameter(["perf_model/core/interval_timer/window_size", 48, 64, 96]) #RobSize
addParameter(["perf_model/l1_dcache/cache_size", 16, 32, 64]) #L1-DCache
addParameter(["perf_model/l2_dcache/cache_size", 64, 128, 256]) #L2-DCache
addParameter(["perf_model/core/interval_timer/dispatch_width", 1, 2, 4]) #DispatchWidth
addParameter(["perf_model/branch_predictor/size", 128, 256, 512]) #BranchPredictor
# ...

def waitForProcesses():
  for process in processes:
    process.join()
  del processes[:]

def init():
  # output labels
  labels = ['WindowSize', 'L1DSize', 'L2DSize', 'DWidth', 'BPSize']
  # add names of the features
  featureNames.extend(labels)
  featureNames.extend(['Branch Misprediction Rate', 'L1D-mpki', 'L2D-mpki',
    'IPC'])
  featureNames.extend(['ROBbin'+str(i) for i in range(1, binsForRob+1)])
  featureNames.extend(['RDbin'+str(i) for i in range(1, binsForRD+1)])
  
  permutations.extend(list(itertools.product(*list(l[1:] for l in parameters))))
  parameterNames.extend(list(l[0] for l in parameters))

def sequentialStep():
  print('Starting with ', globalvars.appName)

  # creates child processes, each is a sniper run. sim.out is saved in
  # individual directories
  print('++Launcher++')
  launcher.run(permutations, parameterNames, False, True)

  # iterates over the sim.out and macpat files in the relevant directories to
  # collect stats. Stats are logged in a file 'efficiency.txt' in app directory
  print('++Stat-Collection++')
  stats.collectStats(permutations)

  # now that we have data for all the  configurations, we can select the 'good' ones
  print('++Selection++')
  goodConfigs = selection.pickGood([x[1:] for x in parameters])
  goodConfigDict[globalvars.appName] = goodConfigs

# detailed run done in parallel for various apps
def parallelDetailed(appName, pinballLoc, outputDirBase):
  # log the output of the process to a specific file
  sys.stdout = open(outputDirBase+"plog.out", "w")
  appfeatures = list(list())
   
  #append the names of the features 
  appfeatures.append(featureNames)

  goodConfigs = goodConfigDict[appName]

  # now that we have the good configs, we need to launch sniper runs again for
  # these configs with detailed stat (counter-data) collection enabled
  #print('++Detailed-Run++')
  launcher.run(goodConfigs, parameterNames, True, False, pinballLoc, outputDirBase)

  # from the detailed runs, we now extract the feature vectors - this forms the
  # training data. Feature vectors are logged to a file
  #print('++Extraction++')
  featureGeneration.extract(goodConfigs, appfeatures, outputDirBase)

def regression():
  appList = []
  # filelist.txt contains path to .address app-phase files (SPEC-Simpoints)
  for line in open('filelist.txt'):
    appList.append(str(line.rsplit('\n')[0]))

  for app in appList:
    globalvars.appName = "app" + str(appList.index(app) + 25)
    globalvars.pinballLoc = str(app)
    globalvars.outputDirBase = "/home/gangwan2/workdir1/cs446/outputs/"+globalvars.appName+"/"
    sequentialStep()

  print('Starting with parallel detailed run for multiple apps')

  for app in appList:
    globalvars.appName = "app" + str(appList.index(app) + 25)
    globalvars.pinballLoc = str(app)
    globalvars.outputDirBase = "/home/gangwan2/workdir1/cs446/outputs/"+globalvars.appName+"/"
    p = Process(target=parallelDetailed, args=(globalvars.appName,
      globalvars.pinballLoc, globalvars.outputDirBase,))
    processes.append(p)
    p.start()
    
    if len(processes) == maxChildren:
      waitForProcesses()

  waitForProcesses()

if __name__=="__main__":
  init()
  regression()

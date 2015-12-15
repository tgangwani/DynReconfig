#!/usr/bin/env python3

import os, sys
import globalvars

metric = globalvars.metric

# function that return a subset of dictionary from the original dictionary based
# on match of a particular parameter value
def filterEfficiencyVal(index, val, efficiencyVal):
  prunedDict = dict()
  for k in efficiencyVal.keys():
    if k[index] == val:
      prunedDict[k] = efficiencyVal[k]

  return prunedDict

def pickGood(params):
  efficiencyVal = dict()
  goodConfigs = list()
  outputDirBase = globalvars.outputDirBase

  if not os.path.isfile(outputDirBase+"efficiency.txt"):
    print('Error-  efficiency.txt not found in location- ' + outputDirBase)
    sys.exit(1)

  # fill the efficiency dictionary from the output file
  for line in open(outputDirBase+'efficiency.txt', 'r'):
    permutation = tuple([int(x) for x in line.split(':')[0].split()])
    value = float(line.rstrip('\n').split(':')[1].split()[metric])
    efficiencyVal[permutation] = value

  # overall best configuration
  #goodConfigs.append(max(efficiencyVal.items(), key=lambda x : x[1])[0])

  # adding 'good' configurations now. The overall best is also added as part of
  # this process
  for parameterList in params:
    for parameter in parameterList:
      prunedDict = filterEfficiencyVal(params.index(parameterList), parameter,
          efficiencyVal)
      goodConfigs.append(max(prunedDict.items(), key=lambda x : x[1])[0])

  # removing duplications
  return list(set(goodConfigs))

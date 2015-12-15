#!/usr/bin/env python3

import os, subprocess, sys
import globalvars
import re, math, functools

sniperRoot = globalvars.sniperRoot
binsForRob = globalvars.binsForRob

def robOccupancy(featureVec):
  occupancy = dict()
  grepCmd = sniperRoot+"/tools/dumpstats.py | grep -i 'roboccupancy'"
  rawData = str(subprocess.Popen(grepCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])
  rawData = rawData.split('\\n')[:-1]
 
  # pattern for extracting the size out of robOccupancy data
  pattern = re.compile("\[([0-9]+)\]")
  for data in rawData:
    obj = pattern.search(data)
    if obj == None:
      print('Error in sqlite data parsing - robOccupancy')
      sys.exit(1)
     
    size = int(obj.group(0)[1:][:-1])
    value = int(data.rstrip('\n').split('=')[1])
    occupancy[size] = value
  
  totalValues = sum(occupancy.values())
  for k, v in occupancy.items():
    occupancy[k] = round((v*100.0)/totalValues, 2)

  robSize = max(occupancy.keys())
  binValues = []
  binValues.extend([float(0) for i in range(binsForRob)])

  # here we put the values into {binsForRob} number of bins
  for k,v in occupancy.items():
    index = math.floor((k*binsForRob*1.0)/robSize) if k < robSize else (binsForRob-1)
    binValues[index] += v

  binValues = list(map(lambda x:round(x,2), binValues))
  featureVec.extend(binValues)

# the sniper script tools/dumpstats.py already parses the sqlite database. We don't need to re-invent the wheel
def getSqliteData(outputDir):
  # list that is returned 
  featureVec = list()
  os.chdir(outputDir)
  
  # right now we only grep for rob-occupancy. We could add more features here
  robOccupancy(featureVec)  

  return featureVec

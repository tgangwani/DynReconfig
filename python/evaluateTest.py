#!/usr/bin/env python3

# this script goes over the apps in the test folder (used for the testing phase of ML). It produces one feature vector for each application with the base configuration (max resources). It then waits for the predicted configuration file, which contains predictions for all the apps in test/. Then it goes over the efficiency.txt files in each app folder and produces a result file with the structure - [predicted, base, best] for each app

import subprocess, os, sys
import linecache
import globalvars

metric = globalvars.metric

base = "/home/gangwan2/workdir1/cs446/test/"
apps = list()
outFile = "/home/gangwan2/workdir1/cs446/featuresTest.txt"
tmpFile = "/home/gangwan2/workdir1/cs446/tmp.txt"
resultsFile = "/home/gangwan2/workdir1/cs446/results.txt"
handle = None 

def addNames():
  for app in apps:
    appFeatures = base+app+"/featuresTest.txt"
    if os.path.isfile(appFeatures):
      with open(appFeatures) as f:
        for line in f:
          handle.write(line)
          return

def produceFeatures():
  global handle
  handle = open(tmpFile, 'wt')
  addNames()
  
  # now add features
  for app in apps:
    appFeatures = base+app+"/featuresTest.txt"
    if os.path.isfile(appFeatures):
      with open(appFeatures) as f:
        next(f)
        for line in f:
          handle.write(line)
        f.close()

  handle.close()

  # command to remove the labels from the feature files
  rmCmd = "cut -d ',' -f6- " + tmpFile + " | cut -d ' ' -f2- " + "> " + outFile
  subprocess.call(rmCmd, shell=True)
  os.remove(tmpFile)

def getResultsForApp(app, predictedConf):
  efficiencyVal = dict()
  outputDir = base+app
  impConfs = [predictedConf]
  impConfs.append(tuple([96, 64, 256, 4, 512])) # max value of all resources (baseConf)
  
  if not os.path.isfile(outputDir+"/efficiency.txt"):
    print('Error-  efficiency.txt not found in location- ' + outputDir)
    sys.exit(1)

  # fill the efficiency dictionary from the output file
  for line in open(outputDir+'/efficiency.txt', 'r'):
    permutation = tuple([int(x) for x in line.split(':')[0].split()])
    value = float(line.rstrip('\n').split(':')[1].split()[metric])
    efficiencyVal[permutation] = value

  # overall best configuration
  best = max(efficiencyVal.items(), key=lambda x : x[1])[0]
  impConfs.append(best)
  
  # structure of the output is [predictedConf-efficiency baseConf-efficiency bestConf-efficiency]
  m_string = ','.join([str(efficiencyVal[i]) for i in impConfs]) + "\n"
  handle.write(m_string)
  #m_string = ','.join([str(i) for i in impConfs]) + "\n"
  #handle.write(m_string)

def getResults():
  global handle
  handle = open(resultsFile, 'wt')
  for app in apps:
    # read the predicted configuration for this app
    line = str(linecache.getline("/home/gangwan2/workdir1/cs446/predictedConf.txt", apps.index(app)+1))
    predictedConf = tuple([int(x) for x in line.rstrip('\n').split()])
    getResultsForApp(app, predictedConf)
  
  handle.close()

if __name__=="__main__":
  apps.extend(os.listdir(base))
  produceFeatures()
  input("Place predictedConf.txt in /home/gangwan2/workdir1/cs446, and press ENTER")
  getResults()

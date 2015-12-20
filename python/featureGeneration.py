#!/usr/bin/env python3

import os, subprocess, sys
import functools, re, math, glob
import db, globalvars
from shutil import copytree

sniperRoot = globalvars.sniperRoot
rdBinary = globalvars.rdBinary
binsForRD = globalvars.binsForRD
maxChildren = globalvars.maxChildren
childProcesses = list()

# fill the RD features from the reusedistance.txt files created in different directories
def fillRDFeatures(features):
  # leave out the first one since it only contains names
  for featureVec in features[1:]:
    for val in featureVec:
      if isinstance(val, str):
        # currently, the only instance of string in the feature vector should be the pointer to the relevant reusedistance.txt file
        assert val.__contains__("reusedistance.txt")
        rd = dict()

        # pattern for extracting distance value from reusedistance.txt
        pattern = re.compile("\[([0-9]+)\]")
        for line in open(val, 'r'):
          obj = pattern.search(line)
          if obj == None:
            print('Error in parsing reusedistance.txt')
            sys.exit(1)
  
          distance = int(obj.group(0)[1:][:-1])
          value = float(line.rstrip('\n').split(':')[1])
          rd[distance] = value

        maxRd = max(rd.keys())
        binValues = []
        binValues.extend([float(0) for i in range(binsForRD)])

        # here we put the values into {binsForRD} number of bins
        for k,v in rd.items():
          index = math.floor((k*binsForRD*1.0)/maxRd) if k < maxRd else (binsForRD-1)
          binValues[index] += v

        binValues = list(map(lambda x:round(x,2), binValues))
        
        # now that we have the bin values, we can overwrite the -1 entries in the feature list
        position = featureVec.index(val)
        featureVec[position] = -1 
        for i in range(len(binValues)):
          # make sure we are not overwriting any useful data
          assert featureVec[position+i] == -1
          featureVec[position+i] = binValues[i]  
    
        # OPTIMIZATION: Since the RD values are same for different permutations of the  configurations for one same application(phase), we can simply use the above calculated binValues to fill the feature vectors corresponding to different permutations
        for fVec in features[2:]:
          fVec[position] = -1
          for i in range(len(binValues)):
            assert fVec[position+i] == -1
            fVec[position+i] = binValues[i]  
    
        return    
  
def waitOnChildren():
  # wait for all subprocesses to complete, get the exit codes
  exit_codes = [p.wait() for p in childProcesses]
  del childProcesses[:]   # reset the list

def extract(permutations, features, outputDirBase, test=False):
  calculateRD = False

  for permutation in permutations:
    outputDir = outputDirBase + "detailed/" + functools.reduce(lambda p,q:str(p)+"_"+str(q),
        permutation)

    if not os.path.exists(outputDir):
      # the detailed directory should always exist unless we are in test-mode
      # create one in that case, by copying material from the non-detailed directory
      assert test==True
      nonDetailed = outputDirBase + functools.reduce(lambda p,q:str(p)+"_"+str(q), permutation)
      # copy directory from non-detailed to detailed
      copytree(nonDetailed, outputDir)

    os.chdir(outputDir)

    # create feature vector for this permutation
    featureVec = list()
    # add the labels
    featureVec.extend([p for p in permutation])

    # Check for existance of sim.out file
    if not os.path.isfile(outputDir+"/sim.out"):
      print('Error- sim.out not found in location- ' + outputDir)
      sys.exit(1)

    ipcCmd = "grep 'IPC' sim.out"
    branchCmd = "grep 'misprediction rate' sim.out"
    mpkiCmd = "grep 'mpki' sim.out"
    rdCmd = rdBinary + outputDir + "/memorytrace.txt"
    
    # extract the branch misprediction rate from sim.out
    branch = str(subprocess.Popen(branchCmd, shell=True, stdout=subprocess.PIPE).communicate()[0])
    branch = float(branch.rstrip('\n').split('|')[1].lstrip()[:-3][:-1])
    featureVec.append(branch)    

    # extract mpki values from sim.out
    mpki = str(subprocess.Popen(mpkiCmd, shell=True, stdout=subprocess.PIPE).communicate()[0])
    mpki = mpki.rstrip('\n').split('\\n')
    l1mpki = float(mpki[-4].rstrip('\n').split('|')[1].lstrip())
    l2mpki = float(mpki[-3].rstrip('\n').split('|')[1].lstrip())
    featureVec.append(l1mpki)    
    featureVec.append(l2mpki)    
    
    # extract the ipc from sim.out
    ipc = str(subprocess.Popen(ipcCmd, shell=True, stdout=subprocess.PIPE).communicate()[0])
    ipc = float(ipc.rstrip('\n').split('|')[1].lstrip()[:-3])
    featureVec.append(ipc)    

    # get all the features from the stats-db 
    featureVec.extend(db.getSqliteData(outputDir))

    # we can't put the RD bins values right now since the RD code (cpp) takes time to execute and we want to parallelize it. The exact values are put in before this function returns
    if not test:
      featureVec.append(outputDir+"/reusedistance.txt")
    # if we are generating the featureTest.txt for the test-apps of the ML
    # model, we need to pick RD file from another pre-existing location
    else:
      rdLoc = glob.glob(outputDirBase+"detailed/*/reusedistance.txt")[0]
      featureVec.append(rdLoc)

    featureVec.extend([-1 for i in range(binsForRD-1)])

    # add the featureVec created for this permutation to overall features list
    features.append(featureVec)

    # create reusedistance code in parallel
    # OPTIMIZATION: we just need to calculate RD once for all the permutations
    if calculateRD == False:
      calculateRD = True
      # only start the RD calculation if it has not been pre-computed
      if not os.path.isfile(outputDir+"/reusedistance.txt") and not test:
        print("Starting RD calculation for permutation ", permutation)
        with open(outputDir+"/reusedistance.txt","wt") as out, open(outputDir+"/stderr.txt","wt") as err:
          childProcesses.append(subprocess.Popen(rdCmd, shell=True, stdout=out,
            stderr=err))  # push back 'Popen' objects
    
    if len(childProcesses) == maxChildren:
      waitOnChildren()

  waitOnChildren()
  # fill RD features before returning
  fillRDFeatures(features)
  
  # write the features to a file
  featureFileName = "features.txt" if test==False else "featuresTest.txt"
  with open(outputDirBase+featureFileName,"wt") as out:
    for feature in features:
      out.write(str(feature)[1:][:-1])  # leave out the '[' ']'
      out.write('\n')
    out.close()

#!/usr/bin/env python3

import os, subprocess, sys
import itertools, functools
import globalvars
from shutil import copytree, rmtree

sniperRoot = globalvars.sniperRoot
sniperCmdCommon = globalvars.sniperCmdCommon
maxChildren = globalvars.maxChildren
childProcesses = list()

def waitOnChildren():
  # wait for all subprocesses to complete, get the exit codes
  exit_codes = [p.wait() for p in childProcesses]
  del childProcesses[:]

# if detailed=True, Sniper is run with detailed data-collection enabled.
# initialLaunch is true when 'run' is called for the very first time from the
# main script
def run(permutations, parameterNames, detailed=False, initialLaunch=False,
    e_pinballLoc=None, e_outputDirBase=None):
  outputDirBase = globalvars.outputDirBase if e_outputDirBase==None else e_outputDirBase
  pinballLoc = globalvars.pinballLoc if e_pinballLoc==None else e_pinballLoc
  
  calculateRD = False
  os.chdir(sniperRoot)
  
  if detailed:
    if not os.path.exists(outputDirBase+"detailed/"):
      os.makedirs(outputDirBase+"detailed/") 

  for permutation in permutations:

    # prepare the additions to the sniper command line
    cmdLineAppend = ""
    for parameterName in parameterNames:
      cmdLineAppend += "-g %s=%s "%(parameterName, 
          permutation[parameterNames.index(parameterName)])

    outputDir = outputDirBase + ["detailed/" if detailed else ""][0] + functools.reduce(lambda p,q:str(p)+"_"+str(q), permutation)

    if not os.path.exists(outputDir):
      os.makedirs(outputDir)

    # the extra flags passed right now for the detailed run include --ml-stats
    # to enable the recording of the cache accesses in memorytrace.txt, and rd_loc to
    # provide the location where memorytrace.txt should be stored
    detailedFlags = " --ml-stats -g log/rd_loc=%s "%(outputDir+"/memorytrace.txt") if detailed and calculateRD == False else ""

    # we just need to calculate RD once for all the permutations. Hence, the
    # detailedFlags are switched off for all permutations except the first. This
    # may need to changed if more detailedFlags (apart from RD) are added in
    # future
    if detailed:
      calculateRD = True                                      
    sniperCmdLine = sniperCmdCommon + detailedFlags + cmdLineAppend + "-d " + outputDir + " --pinballs " + pinballLoc 

    # now launch sniper runs in parallel. If, however, we don't have any
    # detailedFlags, then no need the permutation again. We can simply copy from
    # the non-detailed run
    if detailedFlags == "" and initialLaunch == False:
      print("Detailed run not required for permutation ", permutation)
      cutLoc = outputDir.find("detailed/")-1
      # copy directory from non-detailed to detailed
      rmtree(outputDir)
      copytree(outputDir[0:cutLoc]+outputDir[cutLoc+9:len(outputDir)], outputDir)

    else:
      print("Starting app with parameters-", permutation)
      with open(outputDir+"/stdout.txt","wt") as out, open(outputDir+"/stderr.txt","wt") as err:
        childProcesses.append(subprocess.Popen(sniperCmdLine, shell=True, stdout=out, stderr=err))    # push back 'Popen' objects
    
    if len(childProcesses) == maxChildren:
      waitOnChildren()

  # let all remaining children processes complete before the function returns
  waitOnChildren()

#!/usr/bin/env python3

import os, subprocess, sys
import functools
import globalvars

sniperRoot = globalvars.sniperRoot

def collectStats(permutations):
  efficiencyVals = dict()
  outputDirBase = globalvars.outputDirBase

  for permutation in permutations:
    outputDir = outputDirBase + functools.reduce(lambda p,q:str(p)+"_"+str(q), permutation)
    os.chdir(outputDir)

    # Check for existance of sim.out file
    if not os.path.isfile(outputDir+"/sim.out"):
      print('Error- sim.out not found in location- ' + outputDir)
      sys.exit(1)

    ipcCmd = "grep 'IPC' sim.out"
    powerCmd = "%s/tools/mcpat.py"%(sniperRoot)
    
    # extract the ipc from sim.out
    ipc = str(subprocess.Popen(ipcCmd, shell=True, stdout=subprocess.PIPE).communicate()[0])
    ipc = float(ipc.rstrip('\n').split('|')[1].lstrip()[:-3])
    
    # extract the total power number (W) from mcpat output  
    power = str(subprocess.Popen(powerCmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])
    power = float(power.rstrip('\n').split('\\n')[-2].split()[1])

    # add tuple to dictionary
    efficiencyVals[permutation] = (ipc/power, pow(ipc,2)/power, pow(ipc,3)/power)

  # write the efficiency dictionary to a file
  with open(outputDirBase+"efficiency.txt","wt") as out:
    for k,v in efficiencyVals.items():
      line = ""
      for kt in k:
        line += str(kt) + " "
      line += ':'
      for vt in v:
        line += str(vt) + " "
      out.write(line)
      out.write('\n')
    out.close()

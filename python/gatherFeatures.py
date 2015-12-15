#!/usr/bin/env python3

# this crawler goes over all the app-outfile files and accumulates individual
# app features into one global feature-list

import os, sys

base = "/home/gangwan2/workdir1/cs446/outputs/"
apps = os.listdir(base)
outFile = "/home/gangwan2/workdir1/cs446/featuresFinal.txt"

# output file where all features are accumulated
handle = open(outFile, 'wt')

def addNames(apps):
  for app in apps:
    appFeatures = base+app+"/features.txt"
    if os.path.isfile(appFeatures):
      with open(appFeatures) as f:
        for line in f:
          handle.write(line)
          return

addNames(apps)
# now add features
for app in apps:
  appFeatures = base+app+"/features.txt"
  if os.path.isfile(appFeatures):
    with open(appFeatures) as f:
      next(f)
      for line in f:
        handle.write(line)
      f.close()

handle.close()

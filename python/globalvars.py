#!/usr/bin/env python3

# This file contains the global vars

# these 3 values are set from getTrainingData.py so that we can do a regression over multiple applications
appName=""
pinballLoc=""
outputDirBase=""

sniperRoot = "/home/gangwan2/workdir1/cs446/sniper6"
scriptsRoot = "/home/gangwan2/workdir1/cs446/scripts"
sniperCmdCommon = "./run-sniper -c gainestown --no-cache-warming -s roi-icount:0:100000000:30000000 --roi-script "

#appName = "app1"
#pinballLoc = "/home/gangwan2/workdir1/cs446/INTcpu2006-pinpoints-w100M-d30M-m10/cpu2006-astar_1-ref-1.pp/cpu2006-astar_1-ref-1_t0r1_warmup100001500_prolog0_region30000007_epilog0_001_0-31415.0 "
#outputDirBase = "/home/gangwan2/workdir1/cs446/outputs/"+appName+"/"

metric = 2  # currently we have 3 metrics [ipc/watt, ipc^2/watt, ipc^3/watt]
maxChildren = 32 # Parallelism control. Specify the maximum number of children to run in parallel
rdBinary = "/home/gangwan2/workdir1/cs446/cpp/rdplain "
binsForRD = 20  # 5% values go to each bin
binsForRob = 20  # 5% values go to each bin

## * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
##* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
##==============================================================================
##
## Copyright (C) 2018-2019 Leonardo A. Bautista Gomez (leobago@gmail.com)
## ShardSim - This is a Sharding Simulator to study blockchain scalability.
##
##==============================================================================
##* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
## * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


import datetime


class configuration():

    def __init__(self):
        self.nodesPerRank = 16
        self.maxNodesPerRank = 100
        self.simTime = 1000
        self.timeSpeed = 100
        self.verbosity = 1
        self.slotDuration = 16
        self.nbPeers = 4
        self.maxOutQueue = 50
        self.resultsDir = "results"
        now = datetime.datetime.now()
        self.simID = now.strftime("%Y-%m-%d_%H-%M-%S")
        self.simDir = self.resultsDir+"/"+self.simID



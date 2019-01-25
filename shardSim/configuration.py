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


import datetime, time
from mpi4py import MPI


class configuration():

    def __init__(self):
        # Topology settings
        self.nodesPerRank = 16
        self.maxNodesPerRank = 100

        # Time settings
        self.simTime = 1000
        self.timeSpeed = 100

        # Main chain settings
        self.slotDuration = 16
        self.nbPeers = 4
        self.minerRatio = 90
        self.maxBroadcast = 4

        # Beacon chain settings
        self.validatorRatio = 10
        self.epochLength = 64

        # Shards settings
        self.nbShards = 4
        self.committeeSize = 8

        # MPI settings
        self.maxOutQueue = 50

        # Post-processing setting
        self.verbosity = 1
        self.resultsDir = "data"
        self.browser = "google-chrome"
        now = datetime.datetime.now()
        simID = now.strftime("%Y-%m-%d_%H-%M-%S")
        SID = [simID] * MPI.COMM_WORLD.Get_size()
        simID = MPI.COMM_WORLD.scatter(SID, root=0)
        self.simID = simID
        self.simDir = self.resultsDir+"/"+self.simID

    def verify(self):
        if self.nodesPerRank > self.maxNodesPerRank:
            print("WARNING : nodes per rank higher than max nodes per rank")

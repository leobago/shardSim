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
        self.nodesPerRank = 8
        self.maxNodesPerRank = 10

        # Time settings
        self.simTime = 4000
        self.timeSpeed = 100
        self.syncTime = 5

        # Main chain settings
        self.minerSlot = 16
        self.nbPeers = 4
        self.minerRatio = 90
        self.maxBroadcast = 8
        self.maxReceive = 32

        # Beacon chain settings
        self.validatorRatio = 80
        self.epochLength = 16
        self.slotDuration = 6

        # Shards settings
        self.nbShards = 2
        self.committeeSize = 4

        # MPI settings
        self.maxOutQueue = 16

        # Post-processing setting
        self.verbosity = 1
        self.resultsDir = "data"
        now = datetime.datetime.now()
        simID = now.strftime("%Y-%m-%d_%H-%M-%S")
        SID = [simID] * MPI.COMM_WORLD.Get_size()
        simID = MPI.COMM_WORLD.scatter(SID, root=0)
        self.simID = simID
        self.simDir = self.resultsDir+"/"+self.simID

    def verify(self):
        if self.nodesPerRank > self.maxNodesPerRank:
            print("WARNING : nodes per rank higher than max nodes per rank")

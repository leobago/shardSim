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


import random, time, sys, os
from mpi4py import MPI


from .network import network
from .configuration import configuration
from .topology import topology
from .report import mainReport

class simulator():

    def __init__(self):
        config = configuration()
        topo = topology()
        self.config = config
        self.topo = topo
        self.timeResolution = 1.0/self.config.timeSpeed
        random.seed(topo.rank*time.time())
        self.log("Simulator initialized", 1)

    def log(self, msg, verbosity):
        if verbosity <= self.config.verbosity:
            if self.topo.rank == 0:
                print(msg)

    def bootstrap(self):
        self.net = network(self.config, self.topo)
        self.net.bootstrap()
        if self.topo.rank == 0:
            if not os.path.exists(self.config.resultsDir):
                os.makedirs(self.config.resultsDir)
            if not os.path.exists(self.config.simDir):
                os.makedirs(self.config.simDir)

    def run(self):
        start = time.time()
        for i in range(self.config.simTime):
            beforeTick = time.time()
            self.net.tick()
            afterTick = time.time()
            tickTime = afterTick - beforeTick
            self.log("Tick time took %f seconds" % (tickTime), 3)
            if (self.timeResolution > tickTime):
                time.sleep((1.0/self.config.timeSpeed) - (tickTime))
            else:
                self.log("WARNING! Tick time (%f) longer than time resolution (%f)" % (tickTime, self.timeResolution), 1)

        end = time.time()
        self.log("Simulation executed in %f seconds" % (end-start), 1)
        self.topo.comm.barrier()

    def postProcess(self):
        peerList = []
        for node in self.net.nodes:
            peerList.append([node.nodeID, node.peers])
            node.plotBlockDelays()
            node.report()
        globalPeers = self.topo.comm.gather(peerList, root=0)
        if self.topo.rank == 0:
            self.net.plotP2P(globalPeers)
            observer = random.randint(0, self.config.nodesPerRank-1)
            self.net.nodes[observer].plotBlockTimes()
            self.net.nodes[observer].plotUncleRate()
            htmlContent = mainReport(self.net, globalPeers)
            fileName = self.config.simDir+"/index.html"
            f =  open(fileName, "w")
            f.write(htmlContent)
            f.close()
            self.log("Complete report generated in "+fileName, 1)
            return fileName
        return None

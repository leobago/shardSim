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
from .plot import getFig, plotData

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
                print(" ** Sharding Simulator ** : " + msg)
                sys.stdout.flush()

    def bootstrap(self):
        self.net = network(self.config, self.topo)
        self.net.bootstrap()
        if self.topo.rank == 0:
            if not os.path.exists(self.config.resultsDir):
                os.makedirs(self.config.resultsDir)
            if not os.path.exists(self.config.simDir):
                os.makedirs(self.config.simDir)
        self.topo.comm.barrier()
        self.log("Simulator bootstrap executed", 1)


    def run(self):
        start = time.time()
        for i in range(self.config.simTime):
            beforeTick = time.time()
            self.net.tick()
            afterTick = time.time()
            tickTime = afterTick - beforeTick
            self.log("Tick time took %f seconds" % (tickTime), 3)
            if (i % self.config.syncTime) == 0:
                self.topo.comm.barrier()
            if (self.timeResolution > tickTime):
                time.sleep((1.0/self.config.timeSpeed) - (tickTime))
            else:
                pass
                #self.log("WARNING! Tick time (%f) longer than time resolution (%f)" % (tickTime, self.timeResolution), 1)

        end = time.time()
        self.topo.comm.barrier()
        self.log("Simulation executed in %f seconds" % (end-start), 1)

    def postProcess(self):
        peerList = []
        lastBlock = []
        lastBeacon = []
        for node in self.net.nodes:
            peerList.append([node.nodeID, node.peers])
            lastBlock.append(node.blockChain[-1].number - node.blockChain[0].number)
            lastBeacon.append(node.beaconChain[-1].number - node.beaconChain[0].number)
            if len(node.blockChain) > 1:
                node.plotBlockDelays()
            node.plotMsgs()
            node.report()
        globalPeers = self.topo.comm.gather(peerList, root=0)
        lb = self.topo.comm.gather(lastBlock, root=0)
        le = self.topo.comm.gather(lastBeacon, root=0)
        self.log("Nodes reports generated.", 1)
        if self.topo.rank == 0:
            self.net.plotP2P(globalPeers)
            lastBlock = [item for sublist in lb for item in sublist]
            lastBeacon = [item for sublist in le for item in sublist]
            self.plotLastBlock(lastBlock)
            self.plotLastBeacon(lastBeacon)
            observer = random.randint(0, self.config.nodesPerRank-1)
            self.net.nodes[observer].plotBlockTimes()
            self.net.nodes[observer].plotBeaconTimes()
            self.net.nodes[observer].plotBeaconMiners()
            self.net.nodes[observer].plotUncleRate()
            htmlContent = mainReport(self.net, globalPeers)
            fileName = self.config.simDir+"/index.html"
            f =  open(fileName, "w")
            f.write(htmlContent)
            f.close()
            self.log("Complete report generated in "+fileName, 1)
            return fileName
        return None

    def plotLastBlock(self, lastBlock):
        dataset = []
        dataset.append(range(len(lastBlock)))
        dataset.append(lastBlock)
        target = self.config.simDir+"/lastBlock.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Nodes"                           # Label of x axis
        figConf["yLabel"]       = "Last Block"                      # Label of y axis
        figConf["axis"]         = [0, len(lastBlock), 0, max(lastBlock)+1] # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["y", "b", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Last Block", "2", "3"]          # Labels
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["legLoc"]       = 3                                 # Legend location
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)

    def plotLastBeacon(self, lastBlock):
        dataset = []
        dataset.append(range(len(lastBlock)))
        dataset.append(lastBlock)
        target = self.config.simDir+"/lastBeacon.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Nodes"                           # Label of x axis
        figConf["yLabel"]       = "Last Beacon Block"               # Label of y axis
        figConf["axis"]         = [0, len(lastBlock), 0, max(lastBlock)+1] # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["y", "b", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Last Beacon Block", "2", "3"]   # Labels
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["legLoc"]       = 3                                 # Legend location
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)


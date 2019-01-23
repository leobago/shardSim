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


import os


from .plot import getFig, plotData, plotNetwork
from .node import node


class network():

    def __init__(self, config, topo):
        self.config = config
        self.topo = topo
        self.nodes = []
        self.nodeIDs = []

    def bootstrap(self):
        for i in range(self.config.nodesPerRank):
            nodeID = (self.topo.rank * self.config.maxNodesPerRank) + i
            n = node(self.config, self.topo, self, nodeID)
            n.bootstrap()
            self.nodes.append(n)
            self.nodeIDs.append(nodeID)

    def tick(self):
        for node in self.nodes:
            node.tick()

    def logNet(self):
        for node in self.nodes:
            node.writePeers()

    def plotP2P(self, globalPeers):
        nodes = []
        edges = []
        nodePeers = []
        for rank in globalPeers:
            for node in rank:
                nodeID = int(node[0])
                nodes.append(nodeID)
                peers = node[1]
                nbPeers = 0
                for peer in peers:
                    if nodeID == peer:
                        log("WARNING : Self Loop Edge %d - %d" % (nodeID, peer), 1)
                    else:
                        edges.append(sorted([nodeID, peer]))
                        nbPeers += 1
                nodePeers.append(nbPeers)
        nbNodes = self.topo.nbRanks * self.config.nodesPerRank
        dataset = []
        dataset.append(range(nbNodes))
        dataset.append(nodePeers)
        target = self.config.simDir+"/peers.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["xLabel"]       = "Nodes"                           # Label of x axis
        figConf["yLabel"]       = "Number of Peers"                 # Label of y axis
        figConf["axis"]         = [0, nbNodes, 0, max(nodePeers)+1] # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["g", "b", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Number of Peers", "2", "3"]     # Labels
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["hline"]        = sum(nodePeers)/len(nodePeers)     # Horizontal line for average
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)
        plotNetwork(nodes, edges, nodePeers, self.config.simDir+"/net.png")


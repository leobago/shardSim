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


import time, os, itertools
import matplotlib.pyplot as plt
import networkx as nx


from .plot import getFig, plotData
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

    def plotP2P(self):
        time.sleep(1) # Wait other processes finish writing
        nodes = []
        edges = []
        nodePeers = []
        for file in sorted(os.listdir(self.config.simDir)):
            if file.endswith(".txt") and file.startswith("peers-"):
                node = file.split("-")[1].split(".")[0]
                #print(node)
                nodes.append(int(node))
                #g.add_node(int(node), alias=node)
                f = open(self.config.simDir+"/"+file)
                nbPeers = 0
                for peer in f.readlines():
                    if int(node) == int (peer):
                        log("WARNING : Self Loop Edge %d - %d" % (int(node), int(peer)), 1)
                    else:
                        edges.append(sorted([int(node), int(peer)]))
                        nbPeers += 1
                nodePeers.append(nbPeers)
        minPeers = min(nodePeers)
        maxPeers = max(nodePeers)

        g = nx.Graph()
        for node in nodes:
            g.add_node(node, alias=str(node))
        edges.sort()
        edges = list(edges for edges,_ in itertools.groupby(edges)) # Remove repeated edges
        for edge in edges:
                g.add_edge(edge[0], edge[1])
        pos = nx.spring_layout(g)
        plt.figure(figsize=(25,25))
        plt.axis('off')
        node_labels = nx.get_node_attributes(g, 'alias')
        nodes = g.nodes
        edges = g.edges
        n = nx.draw_networkx_nodes(g, pos, nodes, node_size=250, node_color=nodePeers, cmap="winter", vmin=minPeers, vmax=maxPeers, alpha=0.9)
        n.set_edgecolor("black")
        nx.draw_networkx_edges(g, pos, edges, alpha=1.0)
        nx.draw_networkx_labels(g, pos, node_labels, font_size=8)
        plt.savefig(self.config.simDir+"/net.png")

        nbNodes = self.topo.nbRanks * self.config.nodesPerRank
        dataset = []
        dataset.append(range(nbNodes))
        dataset.append(nodePeers)
        plt.clf()
        target = self.config.simDir+"/peers.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["xLabel"]       = "Nodes"                           # Label of x axis
        figConf["yLabel"]       = "Number of Peers"                 # Label of y axis
        figConf["axis"]         = [0, nbNodes, 0, maxPeers+1]       # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["b", "b", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["", "2", "3", "4", "5", "6+"]    # Labels
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)



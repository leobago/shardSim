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


from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import itertools, warnings
from operator import add
import networkx as nx
import numpy as np


def getFig(type):
    if (type != "plot" and type != "logmap" and type != "map" and type != "sbar" and type != "subplot"):
        return {}
    figConf = {}
    figConf["fileName"]     = "figure.png"                      # Figure file name
    figConf["figType"]      = type                              # plot or map
    figConf["figSize"]      = (6,3)                             # Figure size in inches
    figConf["xScale"]       = "linear"                          # Linear or log
    figConf["yScale"]       = "linear"                          # Linear or log
    figConf["xInver"]       = 0                                 # 1 to invert
    figConf["yInver"]       = 0                                 # 1 to invert
    figConf["xLabel"]       = "x axis"                          # Label of x axis
    figConf["yLabel"]       = "y axis"                          # Label of y axis
    figConf["xLabelSize"]   = 14                                # Size of x label text
    figConf["yLabelSize"]   = 14                                # Size of y label text
    figConf["mapMin"]       = 0                                 # Map minimum value
    figConf["mapMax"]       = 120                               # Map maximum value
    figConf["cmap"]         = "jet"                             # jet, bwr, hot ...
    figConf["orientation"]  = "horizontal"                      # horizontal or vertical
    figConf["xTsize"]       = 9                                 # Size of x axis ticks
    figConf["yTsize"]       = 9                                 # Size of y axis ticks
    figConf["lineWidth"]    = 1                                 # Border line width
    figConf["fit"]          = []                                # Fit to the histogram
    figConf["hline"]        = []                                # Horizontal line
    figConf["xGrid"]        = False                             # Enable x axis grid lines
    figConf["yGrid"]        = False                             # Enable y axis grid lines
    figConf["labels"]       = []                                # List of labels
    figConf["axis"]         = [0,100,0,100]                     # Axis limits
    figConf["legLoc"]       = 1                                 # Legend location
    figConf["legCol"]       = 4                                 # Columns in the legend
    figConf["legSize"]      = 9                                 # Legend font size
    figConf["nbDatasets"]   = 1                                 # Number of datasets
    return figConf

def getData(file, nbColumns, columns, dividors, labeled):
    d = []
    for i in range(nbColumns):
        d.append([])
    with open(file) as f:
        m = map(lambda l: l.split(","), f.readlines())
    f.close()
    if (labeled != 0):
        init = 1
    else:
        init = 0
    for j in range(init, len(m)):
        for i in range(nbColumns):
            if dividors[i] != 0:
                d[i].append(float(m[j][columns[i]])/dividors[i])
            else:
                d[i].append(m[j][columns[i]])
    return d

def plotData(figConf):
    plt.clf()
    fig = plt.figure(figsize=figConf["figSize"])
    plt.xscale(figConf["xScale"])
    plt.yscale(figConf["yScale"])
    plt.xlabel(figConf["xLabel"],size=figConf["xLabelSize"])
    plt.ylabel(figConf["yLabel"],size=figConf["yLabelSize"])
    if "xTpos" in figConf and "xTlab" in figConf:
        plt.xticks(figConf["xTpos"], figConf["xTlab"])
    if "yTpos" in figConf and "yTlab" in figConf:
        plt.yticks(figConf["yTpos"], figConf["yTlab"])
    plt.tick_params(axis="x", labelsize=figConf["xTsize"])
    plt.tick_params(axis="y", labelsize=figConf["yTsize"])
    if "title" in figConf:
        plt.title(figConf["title"])
    if figConf["xInver"]:
        plt.gca().invert_xaxis()
    if figConf["yInver"]:
        plt.gca().invert_yaxis()
    if figConf["xGrid"]:
        plt.gca().xaxis.grid(True)
    if figConf["yGrid"]:
        plt.gca().yaxis.grid(True)
    if figConf["figType"] == "plot":
        plt.axis(figConf["axis"])
        for i in range(figConf["nbDatasets"]):
            plt.plot(figConf["datasets"][0], figConf["datasets"][i+1], figConf["markers"][i], label=figConf["labels"][i])
        plt.legend(loc=figConf["legLoc"], ncol=figConf["legCol"], prop={'size':figConf["legSize"]})
        plt.axis(figConf["axis"])
    if figConf["figType"] == "subplot":
        f, axr = plt.subplots(figConf["nbDatasets"], 1, sharex=True, sharey=True)
        for i in range(figConf["nbDatasets"]):
            ax = plt.subplot(figConf["nbDatasets"], 1, i+1)
            plt.plot(figConf["datasets"][0], figConf["datasets"][i+1], figConf["markers"][i], label=figConf["labels"][i])
            plt.legend(loc=figConf["legLoc"], ncol=figConf["legCol"], prop={'size':figConf["legSize"]})
            plt.axis(figConf["axis"])
            if "yTpos" in figConf and "yTlab" in figConf:
                plt.yticks(figConf["yTpos"], figConf["yTlab"])
            if (i == figConf["nbDatasets"]-1):
                plt.tick_params(axis="x", labelsize=figConf["xTsize"])
            else:
                plt.tick_params(axis="x", labelsize=0)
            plt.tick_params(axis="y", labelsize=figConf["yTsize"])
        ax = plt.subplot(figConf["nbDatasets"], 1, (figConf["nbDatasets"]+1)/2)
        plt.ylabel(figConf["yLabel"],size=figConf["yLabelSize"])
        ax = plt.subplot(figConf["nbDatasets"], 1, figConf["nbDatasets"])
        plt.xlabel(figConf["xLabel"],size=figConf["xLabelSize"])
    if figConf["figType"] == "sbar":
        bottoms = [0] * len(figConf["datasets"][0])
        #colW = figConf["datasets"][0][1] - figConf["datasets"][0][0]
        for i in range(figConf["nbDatasets"]):
            plt.bar(figConf["datasets"][0], figConf["datasets"][i+1], align="center", bottom=bottoms, color=figConf["colors"][i], label=figConf["labels"][i], linewidth=figConf["lineWidth"])
            bottoms = map(add, bottoms, figConf["datasets"][i+1])
        plt.legend(loc=figConf["legLoc"], ncol=figConf["legCol"], prop={'size':figConf["legSize"]})
        plt.axis(figConf["axis"])
        if figConf["fit"] != []:
            plt.plot(figConf["fit"][0], figConf["fit"][1], "g--", label="")
        if figConf["hline"] != []:
            #ax = fig.add_subplot(111)
            plt.hlines(figConf["hline"], figConf["datasets"][0][0], figConf["datasets"][0][len(figConf["datasets"][0])-1]+1, colors="red")
        #jump = (figConf["axis"][1]-figConf["axis"][0])/8
        #plt.xticks(np.arange(figConf["axis"][0]-1, figConf["axis"][1], jump))
        #plt.locator_params(axis='x', nbins=4)
    if figConf["figType"] == "map":
        plt.xlabel(figConf["xLabel"],size=figConf["xLabelSize"], labelpad=-2)
        plt.imshow(figConf["datasets"], interpolation="nearest",
                    vmin=figConf["mapMin"], vmax=figConf["mapMax"], origin="lower", cmap=figConf["cmap"])
        plt.colorbar(orientation=figConf["orientation"])
        plt.axis(figConf["axis"])
        #plt.yticks(np.arange(figConf["axis"][2], figConf["axis"][3]+1, jump))
    if figConf["figType"] == "logmap":
        plt.xlabel(figConf["xLabel"],size=figConf["xLabelSize"], labelpad=-2)
        plt.imshow(figConf["datasets"], interpolation="nearest", origin="lower",
                    norm=LogNorm(vmin=figConf["mapMin"], vmax=figConf["mapMax"]), cmap=figConf["cmap"])
        plt.colorbar(orientation=figConf["orientation"])
        plt.axis(figConf["axis"])
    if figConf["figType"] == "scatter":
        sizes = [e+2 for e in figConf["datasets"][2]]
        plt.scatter(figConf["datasets"][0], figConf["datasets"][1],
                    c=figConf["datasets"][2], s=sizes, cmap=figConf["cmap"], edgecolors='None', alpha=0.75)
        plt.colorbar(orientation=figConf["orientation"])
    plt.savefig(figConf["fileName"], bbox_inches='tight')
    plt.close(fig)
    #print("Figure "+figConf["fileName"]+" generated.")

def plotNetwork(nodes, edges, nodePeers, fileName):
    g = nx.Graph()
    plt.figure(figsize=(25,25))
    plt.axis('off')
    for node in nodes:
        g.add_node(node, alias=str(node))
    edges.sort()
    edges = list(edges for edges,_ in itertools.groupby(edges)) # Remove repeated edges
    for edge in edges:
            g.add_edge(edge[0], edge[1])
    pos = nx.spring_layout(g)
    node_labels = nx.get_node_attributes(g, 'alias')
    nodes = g.nodes
    edges = g.edges
    minPeers = min(nodePeers)
    maxPeers = max(nodePeers)
    n = nx.draw_networkx_nodes(g, pos, nodes, node_size=250, node_color=nodePeers, cmap="winter", vmin=minPeers, vmax=maxPeers, alpha=0.9)
    n.set_edgecolor("black")
    warnings.filterwarnings("ignore") # To avoid annoying deprecated message from networkx
    nx.draw_networkx_edges(g, pos, edges, alpha=1.0)
    warnings.resetwarnings()
    nx.draw_networkx_labels(g, pos, node_labels, font_size=8)
    plt.savefig(fileName)
    #print("Figure "+fileName+" generated.")



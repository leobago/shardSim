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
from shutil import copyfile
from yattag import Doc, indent


def mainReport(net, globalPeers):
    cssPath = os.path.dirname(os.path.abspath(__file__))+"/styles.css"
    copyfile(cssPath, net.config.simDir+"/styles.css")
    doc, tag, text, line = Doc().ttl()
    with tag('html'):
        with tag('head'):
            doc.stag("link", rel="stylesheet", href="styles.css")
        with tag('body'):
            with tag('table', width="1000", border="1"):
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h1'):
                            text("Sharding Simulation "+net.config.simID)
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h2'):
                            text("P2P Network")
                        nbNodes = net.topo.nbRanks * net.config.nodesPerRank
                        line("p", "The simulation ran with a total of "+str(net.topo.nbRanks)+" MPIR ranks.")
                        line("p", "Each rank simulated "+str(net.config.nodesPerRank)+" simNodes.")
                        line("p", "In total, the execution simulated "+str(nbNodes)+" simNodes.")
                        line("p", "Visualization of the P2P network:")
                        with tag("a", href="net.png"):
                            doc.stag('img', src="net.png", width="900")
                        line("p", "Number of peers per node:")
                        with tag("a", href="peers.png"):
                            doc.stag('img', src="peers.png")
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h2'):
                            text("List of nodes")
                        for rank in globalPeers:
                            for node in rank:
                                nodeID = node[0]
                                with tag("a", href=str(nodeID)+".html"):
                                    text(str(nodeID))
                        doc.stag('br')
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h6'):
                            text("Trace generated with Sharding Simulator ")
                            with tag("a", href="https://github.com/leobago/shardSim"):
                                text("shardSim")

    return indent(doc.getvalue())

def nodeReport(node):
    doc, tag, text, line = Doc().ttl()
    with tag('html'):
        with tag('head'):
            doc.stag("link", rel="stylesheet", href="styles.css")
        with tag('body'):
            with tag('table', width="1000"):
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h1'):
                            with tag('a', href="index.html"):
                                text("Sharding Simulation "+node.config.simID+" - Node "+str(node.nodeID))
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h3'):
                            line("p", "Address : "+node.address)
                            line("p", "Ether : "+str(node.ether))
                            line("p", "Miner : "+str(node.miner))
                        with tag('h2'):
                            text("Main chain")
                        if node.blockChain:
                            with tag('table', width="900", klass="chain"):
                                with tag('tr'):
                                    line("td", "Number", klass="header")
                                    line("td", "Hash", klass="header")
                                    line("td", "Parent", klass="header")
                                    line("td", "Miner", klass="header")
                                    line("td", "Time", klass="header")
                                for block in node.blockChain[::-1]:
                                    with tag('tr'):
                                        line("td", str(block.number), klass="chain")
                                        line("td", str(block.hash[-16:]), klass="chain")
                                        line("td", str(block.parent[-16:]), klass="chain")
                                        line("td", str(block.miner), klass="chain")
                                        line("td", str(block.time), klass="chain")
                        else:
                            text("Blockchain empty.")
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h2'):
                            text("Uncle blocks")
                        if node.uncles:
                            with tag('table', width="900", klass="chain"):
                                with tag('tr'):
                                    line("td", "Number", klass="header")
                                    line("td", "Hash", klass="header")
                                    line("td", "Parent", klass="header")
                                    line("td", "Miner", klass="header")
                                    line("td", "Time", klass="header")
                                for block in node.uncles[::-1]:
                                    with tag('tr'):
                                        line("td", str(block.number), klass="chain")
                                        line("td", str(block.hash[-16:]), klass="chain")
                                        line("td", str(block.parent[-16:]), klass="chain")
                                        line("td", str(block.miner), klass="chain")
                                        line("td", str(block.time), klass="chain")
                        else:
                            text("No uncle blocks.")
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h2'):
                            text("Peers")
                        for peer in node.peers:
                            with tag("a", href=str(peer)+".html"):
                                    text(str(peer))
                        doc.stag('br')
                with tag('tr'):
                    with tag('td', align="center"):
                        with tag('h6'):
                            text("Trace generated with Sharding Simulator ")
                            with tag("a", href="https://github.com/leobago/shardSim"):
                                text("shardSim")

    return indent(doc.getvalue())


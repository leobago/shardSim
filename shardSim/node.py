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


import random
from mpi4py import MPI


from .report import nodeReport
from .plot import getFig, plotData
from .block import block


class node():

    def __init__(self, config, topo, net, nodeID):
        self.config = config
        self.topo = topo
        self.net = net
        self.nodeID = nodeID
        self.address = '0x%040x' % random.getrandbits(40 * 4)
        self.time = 0
        self.peers = []
        self.outQueue = []
        self.uncles = []
        self.blockChain = []
        b = block(None, 0, 0)
        self.blockChain.append(b)
        self.ether = random.randint(0, 100)
        if random.randint(0, 100) < self.config.minerRatio:
            self.miner = True
        else:
            self.miner = False
        self.log(str(self.miner), 1)

    def log(self, msg, verbosity):
        if verbosity <= self.config.verbosity:
            idmsg = "[%04d] : " % self.nodeID
            print(idmsg + msg)

    def bootstrap(self):
        for i in range(self.config.nbPeers):
            message = {}
            message["header"] = "New peer"
            message["source"] = self.nodeID
            target = self.nodeID
            while target == self.nodeID and target not in self.peers:
                target = random.randint(0, self.topo.nbRanks-1) * self.config.maxNodesPerRank
                target = target + random.randint(0, self.config.nodesPerRank-1)
            self.send(target, message)
            self.peers.append(target) # This assumes the petition will be received AND accepted
        self.id = 0

    def tick(self):
        self.listen()
        if self.miner:
            self.mine()
        self.cleanOutQueue()
        self.time += 1

    def cleanOutQueue(self):
        if len(self.outQueue) > self.config.maxOutQueue:
            sReq = self.outQueue.pop(0)
            sReq.wait()

    def send(self, target, message):
        targetRank = int(target/100)
        self.log("Message sent to node %d in rank %d" % (target, targetRank), 3)
        sReq = self.topo.comm.isend(message, dest=targetRank, tag=target)
        self.outQueue.append(sReq)

    def broadcast(self, message):
        for peer in self.peers:
            self.send(peer, message)

    def listen(self):
        status = MPI.Status()
        flag = self.topo.comm.iprobe(source=MPI.ANY_SOURCE, tag=self.nodeID, status=status)
        if flag:
            source = status.Get_source()
            message = self.topo.comm.recv(source=source, tag=self.nodeID)
            self.log("Message %s received from %d" % (str(message), source), 3)
            self.classifyMessage(message)

    def checkChain(self):
        last = len(self.blockChain) - 1
        while last > 0:
            if (self.blockChain[last].parent != self.blockChain[last-1].hash):
                self.log("Chain needs to be reorganized", 2)
                found = False
                for index, uncle in enumerate(self.uncles):
                    if uncle.hash == self.blockChain[last].parent:
                        tempBlock = self.blockChain[last-1] #Swap them
                        self.blockChain[last-1] = uncle
                        self.uncles[index] = tempBlock
                        found = True
                if found:
                    self.log("Blockchain reorganized with block %s" % (self.blockChain[last-1].hash[-4:]), 2)
                else:
                    self.log("WARNING : Blockchain could not be reorganized for block number %d" % self.blockChain[last].number, 1)
            last = last -1

    def classifyMessage(self, message):
        if message["header"] == "New peer":
            source = message["source"]
            if source not in self.peers:
                self.peers.append(source)
                self.log("Adding %d as peer" % source, 3)
                message = {}
                message["header"] = "New peer"
                message["source"] = self.nodeID
                target = source
                self.send(target, message)
        elif message["header"] == "New block":
            source = message["source"]
            newBlock = message["block"]
            if next((b for b in self.blockChain if b.hash == newBlock.hash), None) != None:
                self.log("Block %s already in the chain" % newBlock.hash[-4:], 3)
            else: # If new block not in the blockchain
                if newBlock.number ==  (self.blockChain[-1].number + 1): # If it is the next block
                    self.blockChain.append(newBlock) # Add it to the main chain
                    self.log("New block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 3)
                    message["source"] = self.nodeID
                    self.broadcast(message)
                    self.checkChain()
                else:
                    if newBlock.number <= self.blockChain[-1].number: # If it is the same height
                        if next((b for b in self.uncles if b.hash == newBlock.hash), None) == None: # and not in uncles
                            self.uncles.append(newBlock)
                            self.log("Uncle block %s number %d received at time %d" % (newBlock.hash[-4:], newBlock.number, self.time), 2)
                            self.broadcast(message)
                        else:
                            self.log("Block %s already in the uncles list" % newBlock.hash[-4:], 3)
                    else:
                        self.log("WARNING : Node seems out of sync", 3)

    def mine(self):
        r = random.randint(0, int((self.topo.nbRanks * self.config.nodesPerRank * (self.config.minerRatio/100.0) * self.config.slotDuration) - 1))
        if (r == 0):
            b = block(self.blockChain[-1], self.nodeID, self.time)
            self.blockChain.append(b)
            self.log("I have mined block %s number %d at time %d" % (b.hash[-4:], b.number, self.time), 1)
            message = {}
            message["header"] = "New block"
            message["source"] = self.nodeID
            message["block"] = b
            self.broadcast(message)

        else:
            self.log("Random number was %d" % r, 4)

    def report(self):
        htmlContent = nodeReport(self)
        fileName = self.config.simDir+"/"+str(self.nodeID)+".html"
        f =  open(fileName, "w")
        f.write(htmlContent)
        f.close()

    def plotBlockTimes(self):
        bt = []
        blockTimes = []
        lastBlockTime = self.blockChain[0].time
        for block in self.blockChain[1:]:
            if block.time >= lastBlockTime:
                blockTimes.append(block.time - lastBlockTime)
            else:
                blockTimes.append(0)
            lastBlockTime = block.time
        dataset = []
        dataset.append(range(len(blockTimes)))
        dataset.append(blockTimes)
        target = self.config.simDir+"/blockTimes.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["xLabel"]       = "Block number"                    # Label of x axis
        figConf["yLabel"]       = "Time to Block (s)"               # Label of y axis
        figConf["axis"]         = [0, len(blockTimes), 0, (max(blockTimes))+1]       # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["b", "b", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["BlockTime", "4", "5", "6"]      # Labels
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)


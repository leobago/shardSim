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


import random, sys
from mpi4py import MPI


from .report import nodeReport, nodeLogReport, nullReport
from .plot import getFig, plotData
from .block import block
from .tools import getShuffle, splitCommittees


##  This class represents a node in the peer to peer network. It includes
#   miners as well as validators; good or bad actors in the network.
class node():

    ##  This method listen for messages from other nodes
    #   @param  self    Pointer to this node.
    #   @param  config  Configuration for the current execution.
    #   @param  topo    MPI topology in number of ranks and nodes per rank.
    #   @param  net     The entire peer to perr network with the list of nodes.
    #   @param  nodeID  This node ID. An integer.
    def __init__(self, config, topo, net, nodeID):
        self.config = config
        self.topo = topo
        self.net = net
        self.nodeID = nodeID
        self.address = '0x%040x' % random.getrandbits(40 * 4)
        se = [int(s) for s in self.config.simID.split("_")[1].split("-")]
        self.seed = sum(se)%100
        self.time = 0
        self.slot = 0
        self.epoch = 0
        self.logs = []
        self.nodes = []
        self.peers = []
        self.uncles = []
        self.msgSent = []
        self.msgRecv = []
        self.outQueue = []
        self.lostMsgs = []
        self.proposers = []
        self.blockChain = []
        self.beaconChain = []
        self.validators = []
        self.beaconPending = {}
        self.epochCommittees = []
        self.currentCommittee = []
        self.blockArrival = []
        b = block(None, 0, 0)
        self.blockChain.append(b)
        self.ether = random.randint(0, 100)
        self.val = False
        if random.randint(0, 100) < self.config.minerRatio:
            self.miner = True
        else:
            self.miner = False

    def log(self, msg, verbosity, nodeID=-1):
        if nodeID == -1:
            if verbosity <= self.config.verbosity:
                idmsg = "[%05d] : " % self.nodeID
                print(idmsg + msg)
                sys.stdout.flush()
            if verbosity <= self.config.verbosity + 2:
                timsg = "[%05d] : " % self.time
                self.logs.append(timsg + msg)
        else:
            if self.nodeID == nodeID:
                idmsg = "[%05d] : " % self.nodeID
                timsg = "[%05d] : " % self.time
                print(idmsg + timsg + msg)
                sys.stdout.flush()

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
        self.listen()
        self.cleanOutQueue()
        self.log("List of peers created.", 2)
        for r in range(self.topo.nbRanks):
            for n in range(self.config.nodesPerRank):
                self.nodes.append((r * self.config.maxNodesPerRank) + n)
                if (self.seed % self.config.nodesPerRank) != n:
                    self.validators.append((r * self.config.maxNodesPerRank) + n)
                    self.val = 1
        self.log("Node bootstrap executed.", 2)

    def validate(self):
        if (self.time > 0) and (self.time % self.config.slotDuration == 0):
            self.slot = self.slot + 1
            if self.slot % self.config.epochLength == 0:
                self.epoch = self.epoch + 1
                if self.epoch > 0:
                    if len(self.validators) < self.config.epochLength:
                        self.log("WARNING : Not enough validators", 1)
                    vl = getShuffle(self.validators, self.seed)
                    self.epochCommittees = splitCommittees(vl, self.config.epochLength)
                    self.seed = (self.seed * self.epoch) % 100
                    #if self.nodeID == 0:
                        #print(self.epochCommittees)
                        #print(self.seed)
                        #print(str(self.time) + " - " + str(self.slot) + " - " + str(self.epoch) )
            if self.epoch > 0:
                self.currentCommittee = self.epochCommittees[self.slot%self.config.epochLength]
                self.proposers.append(self.currentCommittee[0])
                #print(self.proposers[-1])
                if self.proposers[-1] == self.nodeID:
                    if len(self.beaconChain) > 0:
                        b = block(self.beaconChain[-1], self.nodeID, self.time)
                        bp = self.beaconChain[-1]
                        self.log("Beacon : %d" % bp.number, 2)
                        self.log("Beacon : %s" % bp.hash, 2)
                        self.log("Beacon : %s" % bp.parent, 2)
                        self.log("Beacon : %d" % bp.time, 2)
                    else:
                        b = block(None, 0, 0)
                        b.miner = self.nodeID
                        b.time = self.time
                    b.arrivalTime = self.time
                    self.beaconChain.append(b)
                    self.log("I have mined beacon block %s number %d at time %d" % (b.hash[-4:], b.number, self.time), 1)
                    #print(self.currentCommittee)
                    message = {}
                    message["header"] = "New beacon block"
                    message["source"] = self.nodeID
                    message["block"] = b
                    self.broadcast(message)
                else: # Adding beacon block place holder
                    if len(self.beaconChain) > 0:
                        b = block(self.beaconChain[-1], -1, -1)
                    else:
                        b = block(None, -1, -1)
                        b.miner = -1
                    #self.beaconChain.append(b)
                    #self.log("Appending place holder", 2)

    def tick(self):
        self.listen()
        if self.miner:
            self.mine()
        if self.val:
            self.validate()
        self.cleanOutQueue()
        self.time += 1

    def cleanOutQueue(self):
        #self.log("Out queue length: "+str(len(self.outQueue)), 5, 34)
        cnt = self.config.maxOutQueue
        while (len(self.outQueue) > self.config.maxOutQueue) and (cnt > 0):
            sReq = self.outQueue.pop(0)
            if sReq.test()[0] != True:
                self.lostMsgs.append(sReq)
                cnt = cnt - 1
        if (cnt <= 0):
            self.log("TOO MANY FAILED MESSAGES!!! Out queue length: "+str(len(self.outQueue)), 1)
            self.log("TOO MANY FAILED MESSAGES!!! Out queue length: "+str(len(self.lostMsgs)), 1)
        #self.log("Out queue length: "+str(len(self.outQueue)), 5, 34)

    def send(self, target, message):
        targetRank = int(target/self.config.maxNodesPerRank)
        self.log("Message sent to node %d in rank %d" % (target, targetRank), 3)
        sReq = self.topo.comm.isend(message, dest=targetRank, tag=target)
        self.outQueue.append(sReq)
        while self.time >= len(self.msgSent):
            self.msgSent.append(0)
        self.msgSent[self.time] = self.msgSent[self.time] + 1

    def broadcast(self, message):
        nbMessages = self.config.maxBroadcast
        if nbMessages > len(self.peers):
            nbMessages = len(self.peers)
        bcList = random.sample(self.peers, nbMessages)
        for peer in bcList:
            self.send(peer, message)

    def listen(self):
        status = MPI.Status()
        listening = self.config.maxReceive
        while listening > 0:
            listening = listening - 1
            flag = self.topo.comm.iprobe(source=MPI.ANY_SOURCE, tag=self.nodeID, status=status)
            if flag:
                source = status.Get_source()
                message = self.topo.comm.recv(source=source, tag=self.nodeID)
                self.log("Message %s received from %d" % (str(message), source), 3)
                self.classifyMessage(message)
                while self.time >= len(self.msgRecv):
                    self.msgRecv.append(0)
                self.msgRecv[self.time] = self.msgRecv[self.time] + 1


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
                    # TODO: When this happens the node should ask for the blocks to a peer
                    message = {}
                    message["header"] = "Need main block"
                    message["source"] = self.nodeID
                    message["number"] = self.blockChain[last].number
                    self.send(self.peers[random.randint(0,(len(self.peers)-1))], message)

            last = last - 1

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
        if message["header"] == "Need main block":
            source = message["source"]
            number = message["number"]
            self.log("Block %d was requested by peer %d" % (number, source), 1)
            index = number - self.blockChain[0].number
            if len(self.blockChain) > index:
                message = {}
                message["header"] = "New main block"
                message["source"] = self.nodeID
                message["block"] = self.blockChain[index]
                self.send(source, message)
        elif message["header"] == "New main block":
            source = message["source"]
            newBlock = message["block"]
            if next((b for b in self.blockChain if b.hash == newBlock.hash), None) != None:
                self.log("Block %s already in the chain" % newBlock.hash[-4:], 3)
            else: # If new block not in the blockchain
                if newBlock.number ==  (self.blockChain[-1].number + 1): # If it is the next block
                    newBlock.arrivalTime = self.time
                    self.blockChain.append(newBlock) # Add it to the main chain
                    self.log("New main block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 2)
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
                    else: # If the block is ahead of the next block
                        nbMissingBlocks = newBlock.number - self.blockChain[-1].number
                        self.log("WARNING : Node seems out of sync", 1)
                        for i in range(nbMissingBlocks-1):
                            b = block(None, 0, 0)
                            b.arrivalTime = self.time
                            b.time = self.time
                            b.number = self.blockChain[-1].number + 1
                            self.blockChain.append(b)
                        newBlock.arrivalTime = self.time
                        self.blockChain.append(newBlock) # Add it to the main chain
                        self.log("New block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 3)
                        message["source"] = self.nodeID
                        self.broadcast(message)
                        self.checkChain()
        elif message["header"] == "New beacon block":
            source = message["source"]
            newBlock = message["block"]
            if next((b for b in self.beaconChain if b.hash == newBlock.hash), None) != None:
                self.log("Block %s already in the beacon chain" % newBlock.hash[-4:], 3)
            else: # If new block not in the beacon chain
                if len(self.beaconChain) == 0:
                    newBlock.arrivalTime = self.time
                    self.beaconChain.append(newBlock) # Add it to the main chain
                    self.log("New beacon block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 3)
                    message["source"] = self.nodeID
                    self.broadcast(message)
                else:
                    if newBlock.number ==  (self.beaconChain[-1].number + 1): # If it is the next block
                        newBlock.arrivalTime = self.time
                        self.beaconChain.append(newBlock) # Add it to the beacon chain
                        self.log("New beacon block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 3)
                        message["source"] = self.nodeID
                        self.broadcast(message)
                    else:
                        if newBlock.number <=  (self.beaconChain[-1].number): # If it is a past block
                            newBlock.arrivalTime = self.time
                            index = newBlock.number - self.beaconChain[0].number
                            if newBlock.miner > self.beaconChain[index].miner: #FIXME : Not the right fork choice rule
                                self.beaconChain[index].number = newBlock.number
                                self.beaconChain[index].miner = newBlock.miner
                                self.beaconChain[index].hash = newBlock.hash
                                self.beaconChain[index].time = newBlock.time
                                self.log("New beacon block %s number %d overwriting past block (or placeholder)" % (newBlock.hash[-4:], newBlock.number), 3)
                                message["source"] = self.nodeID
                                self.broadcast(message)
                                bp = self.beaconChain[-1]
                                self.log("Beacon : %d" % bp.number, 2)
                                self.log("Beacon : %s" % bp.hash, 2)
                                self.log("Beacon : %s" % bp.parent, 2)
                                self.log("Beacon : %d" % bp.time, 2)
                            else:
                                self.log("WARNING : Uncle beacon block received", 1)
                        else: # If the block is ahead of the next block
                            nbMissingBlocks = newBlock.number - self.beaconChain[-1].number
                            self.log("WARNING : Beacon chain seems out of sync", 2)
                            for i in range(nbMissingBlocks-1):
                                b = block(None, 0, 0)
                                b.arrivalTime = self.time
                                b.time = self.time
                                b.number = self.blockChain[-1].number + 1
                                self.beaconChain.append(b)
                            newBlock.arrivalTime = self.time
                            self.beaconChain.append(newBlock) # Add it to the beacon chain
                            self.beaconPending[str(newBlock.number)] = 0
                            self.log("New beacon block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 3)
                            message["source"] = self.nodeID
                            self.broadcast(message)
                            #self.checkChain()

        elif message["header"] == "New validator":
            source = message["source"]
            if source not in self.validators:
                self.validators.append(source)
                self.validators.sort()
                self.log("Adding %d as validator" % source, 3)
                self.broadcast(message)


    def mine(self):
        r = random.randint(0, int((self.topo.nbRanks * self.config.nodesPerRank * (self.config.minerRatio/100.0) * self.config.minerSlot) - 1))
        if (r == 0):
            b = block(self.blockChain[-1], self.nodeID, self.time)
            b.arrivalTime = self.time
            self.blockChain.append(b)
            self.log("I have mined block %s number %d at time %d" % (b.hash[-4:], b.number, self.time), 1)
            message = {}
            message["header"] = "New main block"
            message["source"] = self.nodeID
            message["block"] = b
            self.broadcast(message)
        else:
            self.log("Random number was %d" % r, 4)

    def report(self, short=False):
        if (short):
            htmlContent = nullReport(self)
            htmlLogContent = nullReport(self)
        else:
            htmlContent = nodeReport(self)
            htmlLogContent = nodeLogReport(self)
        fileName = self.config.simDir+"/"+str(self.nodeID)+".html"
        f =  open(fileName, "w")
        f.write(htmlContent)
        f.close()
        fileName = self.config.simDir+"/"+str(self.nodeID)+"-log.html"
        f =  open(fileName, "w")
        f.write(htmlLogContent)
        f.close()


    def plotBeaconMiners(self):
        beaconMiners = [0] * (self.topo.nbRanks * self.config.maxNodesPerRank)
        for block in self.beaconChain:
            m = block.miner
            beaconMiners[m] = beaconMiners[m] + 1
        vals = []
        for vi in range(len(beaconMiners)):
            if (vi in self.validators):
                vals.append(beaconMiners[vi])
        dataset = []
        dataset.append(range(len(vals)))
        dataset.append(vals)
        maxTime = max(vals) + 1
        target = self.config.simDir+"/beaconMiners.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Validators"                      # Label of x axis
        figConf["yLabel"]       = "Blocks Mined"                    # Label of y axis
        figConf["axis"]         = [0, len(vals), 0, maxTime]        # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["m", "c", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Beacon Blocks Mined", "6"]      # Labels
        figConf["hline"]        = sum(vals)/len(vals)               # Horizontal line for average
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)



    def plotBeaconTimes(self):
        bt = []
        blockTimes = []
        lastBlockTime = self.beaconChain[0].time
        for block in self.beaconChain[1:]:
            if block.time >= lastBlockTime:
                blockTimes.append(block.time - lastBlockTime)
            else:
                blockTimes.append(0)
            lastBlockTime = block.time
        dataset = []
        dataset.append(range(len(blockTimes)))
        dataset.append(blockTimes)
        maxTime = max(blockTimes) + 1
        target = self.config.simDir+"/beaconTimes.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Block number"                    # Label of x axis
        figConf["yLabel"]       = "Time to Block (s)"               # Label of y axis
        figConf["axis"]         = [0, len(blockTimes), 0, maxTime]  # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["b", "c", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Beacon Block Time", "6"]        # Labels
        figConf["hline"]        = sum(blockTimes)/len(blockTimes)   # Horizontal line for average
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)


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
        maxTime = max(blockTimes) + 1
        target = self.config.simDir+"/blockTimes.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Block number"                    # Label of x axis
        figConf["yLabel"]       = "Time to Block (s)"               # Label of y axis
        figConf["axis"]         = [0, len(blockTimes), 0, maxTime]  # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["b", "c", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["BlockTime", "4", "5", "6"]      # Labels
        figConf["hline"]        = sum(blockTimes)/len(blockTimes)   # Horizontal line for average
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)

    def plotBlockDelays(self):
        bt = []
        delays = []
        if len(self.blockChain) < 1:
            self.log("WARNING: No blocks in this chain", 1)
        for block in self.blockChain[1:]:
            if block.arrivalTime >= block.time:
                delays.append(block.arrivalTime - block.time)
            else:
                delays.append(0)
        if len(delays) < 1 and len(self.blockChain) > 0:
            self.log("WARNING: Block delays list is empty but not the blockChain", 1)
            #print(len(self.blockChain))
            #print(delays)
        dataset = []
        dataset.append(range(len(delays)))
        dataset.append(delays)
        maxTime = max(delays) + 1
        target = self.config.simDir+"/"+str(self.nodeID)+"-blockDelays.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Block number"                    # Label of x axis
        figConf["yLabel"]       = "Block Delay(s)"                  # Label of y axis
        figConf["axis"]         = [0, len(delays), 0, maxTime]      # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["c", "c", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Block Delay", "4", "5", "6"]    # Labels
        figConf["hline"]        = sum(delays)/len(delays)           # Horizontal line for average
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)


    def plotUncleRate(self):
        uncleGroup = 25
        if len(self.uncles) < 1:
            self.log("WARNING: No uncles to plot!", 1)
        nbBlocks = self.blockChain[-1].number - self.blockChain[0].number
        uncleRate = [0] * nbBlocks
        for uncle in self.uncles:
            un = uncle.number - self.blockChain[0].number
            if un < len(uncleRate): #FIXME : There seems to be a bug if this test is not performed
                uncleRate[un] = uncleRate[un] + 1
        ur = []
        sliceStart = 0
        while sliceStart < nbBlocks:
            ur.append(sum(uncleRate[sliceStart:sliceStart+uncleGroup]))
            sliceStart = sliceStart + uncleGroup
        dataset = []
        dataset.append(range(len(ur)))
        dataset.append(ur)
        target = self.config.simDir+"/uncleRate.png"
        figConf = getFig("sbar")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Blocks"                          # Label of x axis
        figConf["yLabel"]       = "Number of uncles"                # Label of y axis
        figConf["axis"]         = [0, len(ur), 0, (max(ur))+1]      # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["colors"]       = ["r", "b", "c", "g", "y", "r" ]   # Colors
        figConf["labels"]       = ["Uncle Rate (25 blocks per bar)"]# Labels
        figConf["hline"]        = sum(ur)/len(ur)                   # Horizontal line for average
        figConf["legLoc"]       = 1                                 # Legend location
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 1                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)

    def plotMsgs(self):
        last = min(len(self.msgSent), len(self.msgRecv))
        lmax = max(max(self.msgSent), max(self.msgRecv)) + 1
        del self.msgSent[last:]
        del self.msgRecv[last:]
        dataset = []
        dataset.append(range(last))
        dataset.append(self.msgSent)
        dataset.append(self.msgRecv)
        target = self.config.simDir+"/"+str(self.nodeID)+"-messages.png"
        figConf = getFig("plot")
        figConf["fileName"]     = target                            # Figure file name
        figConf["figSize"]      = (9,3)                             # Figure size in inches
        figConf["xLabel"]       = "Time (s)"                        # Label of x axis
        figConf["yLabel"]       = "Number of messages"              # Label of y axis
        figConf["axis"]         = [0, last, 0, lmax]                # Axis limits
        figConf["yGrid"]        = True                              # Enable x axis grid lines
        figConf["markers"]      = ["r-", "b-", "g", "y", "r" ]      # Colors
        figConf["labels"]       = ["Sent", "Received"]              # Labels
        figConf["legLoc"]       = 1                                 # Legend location
        figConf["legCol"]       = 1                                 # Columns in the legend
        figConf["nbDatasets"]   = 2                                 # Number of datasets
        figConf["datasets"]     = dataset                           # Datasets
        plotData(figConf)


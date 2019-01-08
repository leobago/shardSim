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


from .block import block


class node():

    def __init__(self, config, topo, net, nodeID):
        self.config = config
        self.topo = topo
        self.net = net
        self.nodeID = nodeID
        self.miner = True
        self.time = 0
        self.peers = []
        self.reqList = []
        self.blockChain = []
        b = block(None, 0)
        self.blockChain.append(b)

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
            self.peers.append(target) # This assumes the petition will be received and accepted
        self.id = 0

    def tick(self):
        self.listen()
        if self.miner:
            self.mine()
        self.time += 1

    def send(self, target, message):
        targetRank = int(target/100)
        self.log("Message sent to node %d in rank %d" % (target, targetRank), 3)
        req = self.topo.comm.isend(message, dest=targetRank, tag=target)

    def broadcast(self, message):
        for peer in self.peers:
            self.send(peer, message)

    def listen(self):
        status = MPI.Status()
        req = self.topo.comm.iprobe(source=MPI.ANY_SOURCE, tag=self.nodeID, status=status)
        source = status.Get_source()
        if source >= 0:
            rreq = self.topo.comm.irecv(source=source, tag=self.nodeID)
            message = rreq.wait()
            self.log("Message %s received from %d" % (str(message), source), 3)
            self.classifyMessage(message)

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
            else:
                if newBlock.number ==  (self.blockChain[-1].number + 1):
                    self.blockChain.append(newBlock)
                    self.log("New block %s number %d received" % (newBlock.hash, newBlock.number), 3)
                    message["source"] = self.nodeID
                    self.broadcast(message)
                elif newBlock.number == self.blockChain[-1].number:
                    if newBlock.miner < self.blockChain[-1].miner: # Consensus by ID
                        self.blockChain[-1] = newBlock
                        self.log("New block %s number %d overwriting previous uncle" % (newBlock.hash[-4:], newBlock.number), 3)
                        self.broadcast(message)
                    else:
                        self.log("Uncle block %s number %d received" % (newBlock.hash[-4:], newBlock.number), 3)
                elif newBlock.number < self.blockChain[-1].number:
                    if newBlock.miner < self.blockChain[(newBlock.number - 7000000)].miner: # Consensus by ID
                        self.blockChain[-1] = newBlock
                        self.log("New block %s number %d overwriting previous uncle" % (newBlock.hash[-4:], newBlock.number), 3)
                        self.broadcast(message)
                    else:
                        self.log("WARNING : Slow messages", 3)
                elif newBlock.number > self.blockChain[-1].number:
                    self.log("WARNING : Node seems out of sync", 3)
                else:
                    self.log("WARNING : We should never reach this point", 1)

    def mine(self):
        r = random.randint(0, (self.topo.nbRanks * self.config.nodesPerRank * self.config.slotDuration) - 1)
        if (r == 0):
            b = block(self.blockChain[-1], self.nodeID)
            self.blockChain.append(b)
            self.log("I have mine block %s number %d at time %d" % (b.hash[-4:], b.number, self.time), 1)
            message = {}
            message["header"] = "New block"
            message["source"] = self.nodeID
            message["block"] = b
            self.broadcast(message)

        else:
            self.log("Random number was %d" % r, 3)

    def writePeers(self):
        f = open(self.config.simDir+"/peers-"+str(self.nodeID)+".txt", "w")
        for peer in self.peers:
            f.write(str(peer)+"\n")
        f.close()



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


import random, time, os


from .network import network


class simulator():

    def __init__(self, config, topo):
        self.config = config
        self.topo = topo
        self.log("Simulator initialized", 1)
        self.timeResolution = 1.0/self.config.timeSpeed
        random.seed(topo.rank*time.time())

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
        self.log("Starting simulation", 1)
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

    def postProcess(self):
        self.log("Simulator postprocessing results", 1)
        self.net.logNet()

    def plot(self):
        self.log("Simulator plotting results", 1)
        if self.topo.rank == 0:
            self.net.plotP2P()



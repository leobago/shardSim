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


class block():

    def __init__(self, parent, miner, time):
        if parent != None:
            self.number = parent.number + 1
            self.hash = '0x%064x' % random.getrandbits(64 * 4)
            self.parent = parent.hash
            self.miner = miner
            self.time = time
        else:
            self.number = 7000000
            self.hash = "0x0000000000000000000000000000000000000000000000000000000000000000"
            self.parent = "0x1111111111111111111111111111111111111111111111111111111111111111"
            self.miner = 0
            self.time = 0



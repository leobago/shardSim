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





def getShuffle(list, seed):
    l = list.copy()
    new = []
    while (l):
        index = seed % len(l)
        new.append(l.pop(index))
    return new


def splitCommittees(list, epochLength):
    nbValPerSlot = len(list) // epochLength
    l = list.copy()
    new = []
    index = 0
    while index < len(l) and len(new) < epochLength:
        new.append(l[index:index+nbValPerSlot])
        index = index + nbValPerSlot
    return new

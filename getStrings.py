def getVCString(v, color):
    return "vertex %d has color %d" % (v, color)

def getPMEdgeString(e):
    return "edge " + repr(e[0]) + " and " + repr(e[1]) + " with color " + repr(e[2]) + " and " + repr(e[3]) + " is in PM"

def getEdgeFromString(s):
    split = s.split()
    return [int(split[1]), int(split[3]), int(split[6]), int(split[8])]

def getEdgeString(e):
    return "edge " + repr(e[0]) + " and " + repr(e[1]) + " with color " + repr(e[2]) + " and " + repr(e[3]) + " is in the graph"

def getTutteVariableString(v):
    return "vertex %d is in Tutte Set" % v

def getRestEdgeString(e):
    return "edge %d %d %d %d is in the subgraph of V-S" % (e[0], e[1], e[2], e[3])

def getMaximumMatchingEdgeString(e):
    return "edge %d %d %d %d is in the maximum matching" % (e[0], e[1], e[2], e[3])

def getConnectedComponentString(v,i):
    return "vertex %d is in component %i" % (v,i)

def getOddComponentString(i):
    return "component %d is an odd component" % i

def getExtraVariableString(index):
    return "an auxiliary variable with index %d" % index


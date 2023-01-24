import networkx as nx
import itertools
import random
"""def verifyByPMAlgorithm(graph, state):
    for coloring in allColorings(graph.n, graph.d):
        inducedGraph = getInducedGraph(graph, coloring)
        PMFlag = existencePM(inducedGraph, graph.n)
        legalFlag = testLegal(coloring,state)
        if (PMFlag and not legalFlag) or (not PMFlag and legalFlag):
            return False
    else: return True
"""

def FORALLPMVCByBlossom(graph, state, k = 0):
    allLegalColorings = []
    if state == "GHZ":
        for color in range(1, graph.d+1):
            allLegalColorings.append([color for i in range(graph.n)])
    #elif state == "W":
    #    for i in range(graph.n):
    #        coloring = [2 for i in range(graph.n)]
    #        coloring[i] = 1
    #        allLegalColorings.append(coloring)
    # W state can be obtained by set Dicke rhs to 1
    elif state == "Dicke":
        allColoringStrings = kbits(graph.n, k)
        for coloringStr in allColoringStrings:
            coloring = []
            for i in range(graph.n):
                coloring.append(2-int(coloringStr[i]))
            allLegalColorings.append(coloring)
        #print("Dicke has too many colorings to enumerate")
        #exit(0)
    elif state == "Empty":
        allLegalColorings.append(([1 for i in range(graph.n)]))
    else:
        print("illegal state for Blossom algorithm: %s" % state)
        exit(0)
    print("all colors = %d " % len(allLegalColorings))
    random.shuffle(allLegalColorings)
    for coloring in allLegalColorings:
        inducedGraph = getInducedGraph(graph, coloring)
        PMFlag = existencePM(inducedGraph, graph.n)
        if PMFlag == False:
            return False
    else: return True

def kbits(n, k):
    result = []
    for bits in itertools.combinations(range(n), k):
        s = ['0'] * n
        for bit in bits:
            s[bit] = '1'
        result.append(''.join(s))
    return result

def allColorings(n,d):
    res = list(itertools.product(list(range(1,d+1)), repeat = n))
    return res

def getInducedGraph(graph, coloring):
    G = nx.Graph()
    edges = []
    for e in graph.edges:
        if (e[2] == coloring[e[0]-1]) and (e[3] == coloring[e[1]-1]):
            edges.append((e[0],e[1]))
    G.add_edges_from(edges)
    return G

def testLegal(coloring,state):
    if state == "GHZ":
        for c in coloring:
            if c!=coloring[0]:  return False
        return True
    if state == "W":
        return (coloring.count(1) == 1)
    if state == "Dicke":
        return (coloring.count(1) == len(coloring) / 2)

def existencePM(graph, n):
    maxMatching = list(nx.max_weight_matching(graph))
    return (len(maxMatching) == n/2)

def checkPMByEnumeration(graph, state):
    if state == "GHZ":
        for color in range(1, graph.d+1):
            coloring = [color for i in range(graph.n)]
            inducedGraph = getInducedGraph(graph, coloring)
            if existencePM(inducedGraph, graph.n) == False: return False
        return True
    if state == "W":
        for hot in range(graph.d):
            coloring = [2 for i in range(graph.n)]
            coloring[hot] = 1
            inducedGraph = getInducedGraph(graph, coloring)
            if existencePM(inducedGraph, graph.n) == False: return False
        return True

import networkx as nx
from networkx.algorithms.approximation import treewidth_min_degree
from graph import *
from polynomialPM import allColorings
from itertools import product
import time

def getNxGraph(graph):
    G = nx.Graph()
    edges = []
    for e in graph.edges:
        edges.append((e[0],e[1]))
    G.add_edges_from(list(set(edges)))
    return G

def resNiceTD(niceTD, nodeID, niceTDDict):
    #print("nodeID = %d " % nodeID)
    #print(niceTDDict)
    #print(niceTD.edges)
    if nodeID == -1: return
    neighbors = list(niceTD.successors(nodeID))
    if len(neighbors) == 0:
        parentID = nodeID
        childID = -1
        s = set(niceTDDict[nodeID])
        for item in niceTDDict[nodeID]:
            parent = frozenset(s)
            s.remove(item)
            if len(s) == 0: return
            childID = len(niceTDDict) + 1
            niceTDDict[childID] = frozenset(s)
            niceTD.add_node(childID)
            niceTD.add_edge(parentID, childID)
            parentID = childID
    elif len(neighbors) == 1:
        originalChild = neighbors[0]
        niceTD.remove_edge(nodeID, originalChild)
        s = set(niceTDDict[nodeID])
        parentID = nodeID
        childID = -1
        # remove vertices
        for item in niceTDDict[nodeID]:
            if item not in niceTDDict[originalChild]:
                s.remove(item)
                if frozenset(s) == niceTDDict[originalChild]:
                    childID = originalChild
                else:
                    childID = len(niceTDDict) + 1
                    niceTDDict[childID] = frozenset(s)
                    niceTD.add_node(childID)
                niceTD.add_edge(parentID, childID)
                parentID = childID
           
        for item in niceTDDict[originalChild]:
            if item not in niceTDDict[nodeID]:
                s.add(item)
                if frozenset(s) == niceTDDict[originalChild]:
                    childID = originalChild
                else:
                    childID = len(niceTDDict) + 1
                    niceTDDict[childID] = frozenset(s)
                    niceTD.add_node(childID)
                niceTD.add_edge(parentID, childID)
                parentID = childID
        resNiceTD(niceTD, childID, niceTDDict)
    elif len(neighbors) > 1:
        child1ID = len(niceTDDict) + 1
        niceTDDict[child1ID] = niceTDDict[nodeID]
        child2ID = len(niceTDDict) + 1
        niceTDDict[child2ID] = niceTDDict[nodeID]
        niceTD.add_edge(nodeID, child1ID)
        niceTD.add_edge(nodeID, child2ID)
        index = 0
        for childID in neighbors:
            # break all edges from parent to children
            niceTD.remove_edge(nodeID, childID)
            if index == 0:
                niceTD.add_edge(child1ID, childID)
                resNiceTD(niceTD, child1ID, niceTDDict)
            else:
                niceTD.add_edge(child2ID, childID)
            index += 1 
        resNiceTD(niceTD, child2ID, niceTDDict)
        
def indexTD(TD, TDDict,root):
    res = nx.DiGraph()
    res.add_nodes_from(TD.nodes)
    res.add_edges_from(TD.edges)
    node2Index = {}
    for node in res.nodes:
        node2Index[node] = len(TDDict)
        TDDict[node2Index[node]] = node
    res = nx.relabel_nodes(res, node2Index)
    rootID = node2Index[root]
    return res, rootID

def getNiceTD(graph):
    start = time.time()
    width, decomposition = treewidth_min_degree(getNxGraph(graph))
    root = list(decomposition.nodes)[0]
    tree = nx.DiGraph(nx.bfs_tree(decomposition, list(decomposition.nodes)[0]))
    niceTDDict = {}
    IndexTD, rootID = indexTD(decomposition, niceTDDict, root)
    resNiceTD(IndexTD, rootID, niceTDDict)
    print("generate a nice tree decomposition with width %d in %f seconds" % (width, time.time()-start))
    return IndexTD, rootID, niceTDDict
    
def get_tuples(length, total):
    if total == 0:
        yield tuple([0 for i in range(length)]) 
        return
    if length == 1:
        yield (total,)
        return
    for i in range(total + 1):
        for t in get_tuples(length - 1, total - i):
            yield (i,) + t

def notEnough(coloring, distribution, d):
    colorCount = getColorCount(coloring, d)
    return min([distribution[i] - colorCount[i] for i in range(d)]) < 0

def DP(TD, node, Dict, distribution, bagColoring, Table, graph):
    stateTuple = tuple([node, tuple(distribution), tuple(bagColoring.keys()),tuple(bagColoring.values())]) 
    #print("now computing: ")
    #print(stateTuple)
    if stateTuple in Table.keys():
        return Table[stateTuple] 
    if min(distribution) < 0: return False # if the usage of any color is negative, return false
    if notEnough(bagColoring, distribution, graph.d):
        Table[stateTuple] = False
        return False
    neighbors = list(TD.successors(node))
    # node is a leaf
    if len(neighbors) == 0:
        if len(Dict[node]) != 1: 
            print("illegal nice tree decomposition!")
            exit(0)
        v = list(Dict[node])[0]
        if bagColoring[v] == 0 and sum(distribution) == 0:
            Table[stateTuple] = True
        else: 
            Table[stateTuple] = False
        return Table[stateTuple]

    elif len(neighbors) == 1:
        childID = neighbors[0]
        # node introduces a vertex from its child
        if len(Dict[childID]) == len(Dict[node]) - 1:
            v = list(Dict[childID].symmetric_difference(Dict[node]))[0]
            if bagColoring[v] == 0:
                childBagColoring = dict(bagColoring)
                childBagColoring.pop(v)
                Table[stateTuple] = DP(TD, childID, Dict, distribution, childBagColoring, Table, graph)
            else:
                for u in Dict[childID]: # for u in bag(Y)
                    if bagColoring[u] == 0: continue
                    if (u > v and [v,u,bagColoring[v], bagColoring[u]] in graph.edges) or (u < v and [u,v,bagColoring[u], bagColoring[v]] in graph.edges):
                        childBagColoring = dict(bagColoring)
                        childBagColoring.pop(v)
                        childBagColoring[u] = 0
                        childDistribution = list(distribution)
                        childDistribution[bagColoring[v]-1] -= 1
                        childDistribution[bagColoring[u]-1] -= 1
                        if DP(TD, childID, Dict, childDistribution, childBagColoring, Table, graph):
                            Table[stateTuple] = True
                            return True 
                Table[stateTuple] = False 
        # node forgets a vertex from its child
        elif len(Dict[childID]) == len(Dict[node]) + 1:
            v = list(Dict[childID].symmetric_difference(Dict[node]))[0]
            for color in range(1, graph.d+1):
                childBagColoring = dict(bagColoring)
                childBagColoring[v] = color
                if DP(TD, childID, Dict, distribution, childBagColoring, Table, graph):
                    Table[stateTuple] = True
                    return True
            Table[stateTuple] = False
        else: 
            print("illegal nice tree decomposition!")
            exit(0)
    # X joins its children Y and Z
    elif len(neighbors) == 2:
        child1ID = neighbors[0]
        child2ID = neighbors[1]
        #colorCount = getColorCount(bagColoring, graph.d)
        #totalDistribution = [distribution[i] - colorCount[i] for i in range(graph.d)]
        totalDistribution = [distribution[i] for i in range(graph.d)]
        ranges = [range(totalDistribution[i]+1) for i in range(graph.d)]
        allSplitWays = list(product(*ranges)) 
        allBagColoringSplitWays = list(product(list(range(2)), repeat = len(bagColoring)))
        #print(allBagColoringSplitWays)
        for splitWay in allSplitWays:
            bagVertexList = list(bagColoring.keys())
            for bagColoringSplitWay in allBagColoringSplitWays:
                child1BagColoring = {bagVertexList[i]: bagColoring[bagVertexList[i]] if bagColoringSplitWay[i] == 1 else 0 for i in range(len(bagVertexList))}
                child2BagColoring = {bagVertexList[i]: bagColoring[bagVertexList[i]] if bagColoringSplitWay[i] == 0 else 0 for i in range(len(bagVertexList))} 
                child1Distribution = [splitWay[i] for i in range(graph.d)]
                child2Distribution = [totalDistribution[i] - splitWay[i] for i in range(graph.d)]
                if DP(TD, child1ID, Dict, child1Distribution, child1BagColoring, Table, graph) and DP(TD, child2ID, Dict, child2Distribution, child2BagColoring, Table, graph):
                    Table[stateTuple] = True
                    return True
        Table[stateTuple] = False
    else: 
        print("illegal nice tree decomposition!")
        exit(0) 
    return Table[stateTuple]

def getColorCount(coloring, d):
    res = [0 for i in range(d)]
    for c in coloring.values():
        if c >= 1:
            res[c-1] += 1
    return res

def getAllRootBagColorings(bag, d):
    rootColoringList = allColorings(len(bag),d)
    res = []
    for rootColoring in rootColoringList:
        rootColoringDict = {}
        for index in range(len(bag)):
            rootColoringDict[list(bag)[index]] = rootColoring[index]
        res.append(rootColoringDict)
    return res
    
def verifyByDP(graph, state, k=0):
    niceTD, rootID, niceTDDict = getNiceTD(graph)
    #print(niceTD.edges) 
    #print(niceTDDict)
    start1 = time.time()
    legalDistributionList = list(get_tuples(graph.d, graph.n))
    if state == "GHZ":
        for d in range(graph.d):
            monoTuple = [0 for i in range(graph.d)]
            monoTuple[d] = graph.n
            legalDistributionList.remove(tuple(monoTuple))
    elif state == "Dicke":
        legalDistributionList.remove(tuple([k, graph.n - k]))
    elif state == "W":
        legalDistributionList.remove((1,graph.n-1))
    else:
        print("invalid state %s" % state)
        exit(0)
    rootBag = niceTDDict[rootID]
    allRootColorings = getAllRootBagColorings(rootBag, graph.d)
    start = time.time()
    #print("preparation takes %f seconds" % (time.time()-start1))
    #legalDistributionList = [[2,8]]
    #allRootColorings = [{8:2,5:2,7:2}]
    stateTable = {}
    for distribution in legalDistributionList:
        disstart = time.time()
        for rootColoring in allRootColorings:
            #print(rootColoring)
            #print("rootid = %d " % rootID)
            flag = DP(niceTD, rootID, niceTDDict, distribution, rootColoring, stateTable, graph)
            #for item in stateTable:
                #if stateTable[item] == True:
                    #print(item),
                    #print(stateTable[item])
            if flag:
                #print("PM found by DP") 
                #print(stateTable)
                #print(rootColoring)
                #print(distribution)
                print("root id: %d " % rootID)
                print("DP takes %f seconds" % (time.time()-start))
                return False
        #print("this distribution uses %f seconds. size of dict = %d" % ((time.time() - disstart), len(stateTable)))
    #print("no PM found by DP")
    #print("DP takes %f seconds" % (time.time()-start))
    return True

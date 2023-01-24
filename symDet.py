from sympy import *
import numpy as np
from dp import get_tuples 
#this function computes the determinant of the symbolic Tutte matrix
def checkBySymDet(graph, state, k=0):
    #d = MatrixSymbol("d", graph.d, 1)
    d = [symbols('d%d' % i, positive=True) for i in range(graph.d)]
    M = zeros(graph.n, graph.n) 
    for e in graph.edges:
        if e[0] != e[1]:
            if e[0] > e[1]:
                M[e[0]-1,e[1]-1] += d[e[2]-1] * d[e[3]-1]
                M[e[1]-1,e[0]-1] -= d[e[2]-1] * d[e[3]-1]
            else:
                M[e[0]-1,e[1]-1] -= d[e[2]-1] * d[e[3]-1]
                M[e[1]-1,e[0]-1] += d[e[2]-1] * d[e[3]-1]
    weightRange = 2 * len(graph.edges)
    for i in range(graph.n):
        for j in range(i+1, graph.n):
            edgeWeight = np.random.randint(low=1, high=weightRange)
            M[i,j] *= edgeWeight
            M[j,i] *= edgeWeight
    det = M.det()
    pfaffian = (sqrt(factor(det)).expand())
    pfaffianStr = repr(pfaffian)
    legalDistributionList = list(get_tuples(graph.d, graph.n))
    legalTerms = []
    SYMDET_RES_PATH = "res/FORALLNEPM_SYMDET.txt"
    f = open(SYMDET_RES_PATH, "w+")
    f.write(pfaffianStr)
    if state == "GHZ":
        for d in range(graph.d):
            monoTuple = [0 for i in range(graph.d)]
            monoTuple[d] = graph.n
            legalDistributionList.remove(tuple(monoTuple))
    elif state == "Dicke":
        legalDistributionList.remove(tuple([k, graph.n-k]))
    elif state == "W":
        legalDistributionList.remove((1,graph.n-1))
    for t in legalDistributionList:
        termStr = ""
        for i in range(len(t)):
            if t[i] == 1:
                termStr += ("d%d" % i)
            elif t[i] == 0: continue
            else:
                termStr += ("d%d**%d" % (i, t[i]))
            if i != len(t)-1: termStr += "*"
        legalTerms.append(termStr)
    for term in legalTerms:
        if term in pfaffianStr: 
            f.write("found illegal term %s" % term)
            return False
    return True

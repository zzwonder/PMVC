from util import *
from PBEncoding import *
from pysat.card import *
from TseytinEncoding import *
from main import Configuration
def generateFORALLPMQBFFormula(graph, formulaPath, varMap, state, k=0):
    for e in graph.edges:
        allocateVar(varMap, getPMEdgeString(e))
    for i in range(1, graph.n + 1):
        for j in range(1, graph.d + 1):
            allocateVar(varMap, getVCString(i, j))
    with open(formulaPath, 'w+') as f:
        # exact-one for ad-hoc color of each vertex
        cnfLC = []
        cnfLCList = []
        cnfLCNameList = []
        #f.write("c exact-one for ad-hoc color of each vertex\n")
        for i in range(1, graph.n + 1):
            lits = []
            for j in range(1, graph.d + 1):
                lits.append(varMap[getVCString(i, j)])
            cnfAM = CardEnc.atmost(lits=lits,bound=0, encoding=1,top_id=len(varMap))
            if cnfAM.nv > len(varMap):
                fillMap(varMap, cnfAM.nv)
            cnfAL = CardEnc.atleast(lits=lits,bound=2, encoding=1,top_id=len(varMap))
            if cnfAL.nv > len(varMap):
                fillMap(varMap, cnfAL.nv)
            cnfLCList.append(cnfAL.clauses)
            cnfLCNameList.append("LC_AL_%d" % (i))
            cnfLCList.append(cnfAM.clauses)
            cnfLCNameList.append("LC_AM_%d" % (i))

        _, cnfLC = multiLogicalOROfCNFByTseytinEncoding(varMap, cnfLCList, nameList=cnfLCNameList)

        # cnfPM includes clauses encoding the existence of a legal perfect matching 
        cnfPM = []
        for e in graph.edges:
            cnfPM.append([-varMap[getPMEdgeString(e)], varMap[getVCString(e[0], e[2])]])
            cnfPM.append([-varMap[getPMEdgeString(e)], varMap[getVCString(e[1], e[3])]])

        for i in range(1, graph.n + 1):
            edgeList = graph.getAdjacentEdges(i)
            lits = []
            for e in edgeList:
                lits.append(varMap[getPMEdgeString(e)])
            if len(lits) > 0:
                cnf = CardEnc.equals(lits=lits,bound=1,encoding=1,top_id=len(varMap))
                for c in cnf.clauses:
                    for l in c:
                        if abs(l) > len(varMap):
                            allocateVar(varMap, "var %d used in encoding cardinality in CNF" % abs(l))
                cnfPM += cnf.clauses

        # cnfCl includes clauses encoding the quantum states
        cnfCl = []
        cnfClList = []
        cnfClNameList = []
        if state == "GHZ":
            for c1 in range(1, graph.d + 1):
                lits1 = []
                for i in range(1,graph.n+1):
                    lits1.append((varMap[getVCString(i,c1)]))
                for c2 in range(c1 + 1, graph.d+1):
                    lits2 = []
                    for i in range(1,graph.n+1):
                        lits2.append((varMap[getVCString(i,c2)]))
                    cnfClList.append([lits1, lits2])
                    cnfClNameList.append("c1=%d_c2=%d" % (c1, c2))
            _, cnfCl = multiLogicalOROfCNFByTseytinEncoding(varMap, cnfClList, nameList=cnfClNameList)
        elif state == "Dicke":
            lits = []
            for i in range(1,graph.n+1):
                lits.append(varMap[getVCString(i,1)])
            cnfAM = CardEnc.atmost(lits=lits,bound=k-1, encoding=1, top_id=len(varMap))
            if cnfAM.nv > len(varMap):
                fillMap(varMap, cnfAM.nv)
            cnfAL = CardEnc.atleast(lits=lits,bound=k+1, encoding=1, top_id=len(varMap))
            if cnfAL.nv > len(varMap):
                fillMap(varMap, cnfAL.nv)
            cnfClList.append(cnfAL.clauses)
            cnfClNameList.append("cl_AL")
            cnfClList.append(cnfAM.clauses)
            cnfClNameList.append("cl_AM")
            _, cnfCl = multiLogicalOROfCNFByTseytinEncoding(varMap, cnfClList, nameList=cnfClNameList)


        allClauses = []
        if not Configuration.TseytinEncoding:
            for c1 in cnfLC:
                for c2 in cnfCl:
                    for c3 in cnfPM:
                        allClauses.append(c1+c2+c3)
            #print("not using Tseytin Encoding is too expensive! Turn TseytinEncoding on")
            #exit(0)
        else:
            _, allClauses = multiLogicalOROfCNFByTseytinEncoding(varMap, [cnfPM, cnfLC, cnfCl], nameList=["cnfPM", "cnfLC", "cnfCl"])
            allClauses.append([_])

        nv = max(map(max,allClauses))
        f.write("p cnf %d %d\n" % (nv, len(allClauses)))
        f.write("a ")
        forallVarList = []
        for i in range(1, graph.n + 1):
            for j in range(1, graph.d + 1):
                f.write("%d " % varMap[getVCString(i, j)])
                forallVarList.append(varMap[getVCString(i, j)])
        f.write("0\n")
        f.write("e ")
        for i in range(1, nv+1):
            if i not in forallVarList: f.write("%d " % i)
        f.write("0\n")
        writeConstraintsToFile(f, allClauses, isList = True, form="CNF")

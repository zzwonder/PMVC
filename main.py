import random
import os
import math
import argparse
from pysat.card import *
from polynomialPM import *
from getStrings import *
from PBEncoding import *
import time
from encodingCNF import *
from graph import *
from symDet import *
from dp import verifyByDP
from qbf import *
from util import *
import numpy as np

class Configuration:
    breakSymmetry = False
    QBFNEPM = False
    PMMethod = ""
    NEPMMethod = ""
    TseytinEncoding = False    
    #CNFSOLVER_PATH = 'solvers/clasp/clasp-3.3.2/clasp-3.3.2-x86-linux'
    CNFSOLVER_PATH = 'solvers/kissat-sc2022-bulky/bin/kissat'
    CNFSOLVER_OPTIONS = ''
    PBXORSOLVER_PATH = 'solvers/linpb/build/linpb'
    PBXORSOLVER_OPTIONS = '--print-sol=1'

def configurate(BF=False, SB=False,CN=False, QN=False, PMM="", NEPMM="", TE=False, GP=False):
    Configuration.breakSymmetry = SB
    Configuration.graphProperty = GP
    Configuration.QBFNEPM = QN
    Configuration.CNFNEPM = CN
    Configuration.FORALLPMMethod = PMM
    Configuration.FORALLNEPMMethod = NEPMM
    Configuration.TseytinEncoding = TE
    print("configuration: PMMethod=%s, NEPMMethod=%s, breakSymmetry=%r, QBFNEPM=%r,CNFNEPM=%r, TseytinEncoding=%r" % (Configuration.FORALLPMMethod, Configuration.FORALLNEPMMethod, Configuration.breakSymmetry, Configuration.QBFNEPM,Configuration.CNFNEPM, Configuration.TseytinEncoding ) )

def generateFORALLNEPMFormula(graph, formulaPath, state, k = 0):
    varMap = {}
    for e in graph.edges:
        allocateVar(varMap, getPMEdgeString(e))
    for i in range(1, graph.n + 1):
        for j in range(1, graph.d + 1):
            allocateVar(varMap, getVCString(i, j))
    with open(formulaPath, 'w+') as f:
        # perfect matching edges
        f.write("c color constraints\n")
        for e in graph.edges:
            f.write("im %d -> ( %d & %d ) \n" % (
                varMap[getPMEdgeString(e)], varMap[getVCString(e[0], e[2])], varMap[getVCString(e[1], e[3])]))
        # exact-one edges
        f.write("c exact-one edges for PM\n")
        for i in range(1, graph.n + 1):
            edgeList = graph.getAdjacentEdges(i)
            if len(edgeList) > 0:
                f.write("eo ")
                for e in edgeList:
                    f.write(repr(varMap[getPMEdgeString(e)]) + " ")
                f.write("\n")
            else:
                f.write('false\n')
        # exact-one for ad-hoc color of each vertex
        f.write("c exact-one for ad-hoc color of each vertex\n")
        for i in range(1, graph.n + 1):
            f.write("eo ")
            for j in range(1, graph.d + 1):
                f.write(repr(varMap[getVCString(i, j)]) + " ")
            f.write('\n')
        # symmetric function for vertex coloring
        if state == "GHZ":
        #NAE(vc(1,r),vc(2,r),...) for GHZ states
            for j in range(1, graph.d + 1):
                f.write("nae ")
                for i in range(1,graph.n+1):
                    f.write("%d " % (varMap[getVCString(i,j)]))
                f.write('\n')
        elif state == "W":
            lits = []
            for i in range(1,graph.n+1):
                lits.append( varMap[getVCString(i,1)])
            cnf = CardEnc.equals(lits=lits,bound=1, encoding=1,topv=len(varMap)+1)
            cnf = cnf.negate()
            for c in cnf:
                f.write("cnf ")
                for l in c:
                    f.write("%d " % l)
                f.write('\n')
        elif state == "Dicke":
            print("Dicke state")
            encoding = 1
            lits = []
            for i in range(1,graph.n+1):
                lits.append(varMap[getVCString(i,1)])
            cnfAM = CardEnc.atmost(lits=lits,bound=k-1,encoding=encoding,top_id=len(varMap))
            for c in cnfAM.clauses:
                for l in c:
                    if abs(l) > len(varMap):
                        allocateVar(varMap, "var %d used in encoding cardinality in CNF" % abs(l))
            cnfAL = CardEnc.atleast(lits=lits,bound=k+1,encoding=encoding,top_id=len(varMap))
            for c in cnfAL.clauses:
                for l in c:
                    if abs(l) > len(varMap):
                        allocateVar(varMap, "var %d used in encoding cardinality in CNF" % abs(l))
            if not Configuration.TseytinEncoding:
                print("using the brute force encoding. generate %d * %d = %d clauses " % (len(cnfAM.clauses), len(cnfAL.clauses), len(cnfAM.clauses)*len(cnfAL.clauses)))
                for c1 in cnfAM.clauses:
                    for c2 in cnfAL.clauses:
                        f.write("cnf ")
                        for l in c1:
                            f.write("%d " % l)
                        for l in c2:
                            f.write("%d " % l)
                        f.write("\n")
            else:
                _, constraintList = multiLogicalOROfCNFByTseytinEncoding(varMap, [cnfAL.clauses, cnfAM.clauses], nameList = ["atleast", "atmost"] )
                print("using Tseytin Encoding. Gathering %d constraints" % len(constraintList))
                writeConstraintsToFile(f, constraintList, isList = True)
        elif state == "Empty":
            f.write("card ")
            for i in range(1,graph.n+1):
                f.write("%d " % varMap[getVCString(i,1)])
            f.write(" = %d ;\n" % graph.n)
        else:
            print("Unknown State: %s " % state)
            exit(0)
    return varMap


def detectSymmetry(f, graph, varMap):
    n = graph.n
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            neigh_i = set(graph.getNeighbors(i))
            if j in neigh_i: neigh_i.remove(j)
            neigh_j = set(graph.getNeighbors(j))
            if i in neigh_j: neigh_j.remove(i)
            if neigh_i == neigh_j:
                f.write(("cnf %d %d\n" % (-varMap[getTutteVariableString(i)], varMap[getTutteVariableString(j)])))
                #print("v%d v%d detected" % (i,j))

def generateFORALLPMFormula(graph, formulaPath, varMap, state, k=0):
    symmetryBreaking = Configuration.breakSymmetry
    for i in range(1, graph.n + 1):
        allocateVar(varMap,getTutteVariableString(i))
    for i in range(1, graph.n + 1):
        allocateVar(varMap, getOddComponentString(i))
    for i in range(1, graph.n + 1):
        ub = i+1 if symmetryBreaking else graph.n+1
        for j in range(1, ub):
            allocateVar(varMap, getConnectedComponentString(i,j))
    for e in graph.edges:
        allocateVar(varMap, getRestEdgeString(e))
    for i in range(1, graph.n + 1):
        for j in range(1, graph.d + 1):
            allocateVar(varMap, getVCString(i, j))
    with open(formulaPath, 'w+') as f:
        # exact-one for ad-hoc color of each vertex
        f.write("c exact-one for ad-hoc color of each vertex\n")
        for i in range(1, graph.n + 1):
            f.write("eo ")
            for j in range(1, graph.d + 1):
                f.write(repr(varMap[getVCString(i, j)]) + " ")
            f.write('\n')
        for e in graph.edges:
            f.write("le %d <-> ( ! %d & ! %d ) & ( %d & %d ) \n" % (varMap[getRestEdgeString(e)], varMap[getTutteVariableString(e[0])], varMap[getTutteVariableString(e[1])], varMap[getVCString(e[0], e[2])],
                                                               varMap[getVCString(e[1],e[3])]))
        for e in graph.edges:
            ub = min(e[0], e[1]) + 1 if symmetryBreaking else graph.n+1
            for i in range(1, ub):
                f.write("cc %d -> ( %d = %d )\n" % (varMap[getRestEdgeString(e)], varMap[getConnectedComponentString(e[0],i)], varMap[getConnectedComponentString(e[1],i)] ))
        for i in range(1, graph.n+1):
            f.write("x %d " % varMap[getOddComponentString(i)])
            lb = i if symmetryBreaking else 1
            for j in range(lb, graph.n+1 ):
                f.write("%d " % varMap[getConnectedComponentString(j,i)])
            f.write("\n")
        for i in range(1, graph.n+1):
            f.write('eo ')
            f.write('%d ' % varMap[getTutteVariableString(i)])
            ub = i + 1 if symmetryBreaking else graph.n+1
            for j in range(1,ub):
                f.write("%d " % varMap[getConnectedComponentString(i,j)])
            f.write("\n")
        if symmetryBreaking:
            for i in range(1, graph.n+1):
                for j in range(i+1, graph.n+1):
                   f.write('nor %d %d\n' % (varMap[getTutteVariableString(i)], varMap[getConnectedComponentString(j,i)]))        
        
        symmetryBreaking2 = True
        if symmetryBreaking2:
            for i in range(1, graph.n+1):
                for j in range(1, i):
                   for kk in range(i, graph.n+1):
                        f.write('cnf %d %d\n' % (-varMap[getConnectedComponentString(i,j)], -varMap[getConnectedComponentString(kk,i)]))

        graphProperty = Configuration.graphProperty
        if graphProperty:
            detectSymmetry(f, graph, varMap)
        f.write('card ')
        for i in range(1, graph.n+1):
            f.write("%d -%d " % (varMap[getOddComponentString(i)], varMap[getTutteVariableString(i)]))
        f.write(">= 1 ;\n")
        maximumTutte = False
        if maximumTutte:
            for e in graph.edges:
                allocateVar(varMap, getMaximumMatchingEdgeString(e))
            for e in graph.edges:
                f.write("im %d -> ( %d & %d ) \n" % (
                    varMap[getMaximumMatchingEdgeString(e)], varMap[getVCString(e[0], e[2])], varMap[getVCString(e[1], e[3])]))
            for i in range(1, graph.n + 1):
                edgeList = graph.getAdjacentEdges(i)
                if len(edgeList) > 0:
                    f.write("card ")
                    for e in edgeList:
                        f.write(repr(varMap[getMaximumMatchingEdgeString(e)]) + " ")
                f.write("<= 1 ;\n")
            for i in range(1, graph.n + 1):
                edgeList = graph.getAdjacentEdges(i)
                if len(edgeList) > 0:
                    f.write("cnf ")
                    f.write("%d " % varMap[getOddComponentString(i)])
                    for e in edgeList:
                        f.write(repr(varMap[getMaximumMatchingEdgeString(e)]) + " ")
                    f.write("\n")
                else:
                    f.write('false\n')
                if len(edgeList) > 0:
                    f.write("cnf ")
                    f.write("-%d " % varMap[getTutteVariableString(i)])
                    for e in edgeList:
                        f.write(repr(varMap[getMaximumMatchingEdgeString(e)]) + " ")
                    f.write("\n")
        print('forall pm var num: %d ' % len(varMap))   
        if state == "GHZ":
            for j in range(1, graph.d + 1):
                f.write("ae ") # ae = all-equal
                for i in range(1, graph.n + 1):
                    f.write("%d " % (varMap[getVCString(i, j)]))
                f.write('\n')
            return len(varMap)
        elif state == "W":
            f.write("eo ")
            for i in range(1,graph.n+1):
                f.write("%d " % varMap[getVCString(i,1)])
            f.write('\n')
        elif state == "Dicke":
            f.write("card ")
            for i in range(1,graph.n+1):
                f.write("%d " % varMap[getVCString(i,1)])
            f.write(" = %d ;\n" % k)
            print("write k = %d " %k) 
        elif state == "Empty":
            f.write("card ")
            for i in range(1,graph.n+1):
                f.write("%d " % varMap[getVCString(i,1)])
            f.write(" = %d ;\n" % graph.n)
        else: 
            print("unknown state %s" % state)
            exit(0)

def checkFORALLPM(graph, state, k = 0, FORALLPMFormulaPath="formula/FORALLPMformula.hybrid", PBXORFORALLPMFormulaPath="formula/FORALLPM.pb"): # check the nepm comdition for all legal states. if the extended graph with unassigned edges are true has no illegal PM, return true. otherwise return false.
    varMap = {}
    start = time.time()
    random_num = random.randint(1,1000000)
    FORALLPMFormulaPath="formula/FORALLPMformula_%d.hybrid" % random_num
    PBXORFORALLPMFormulaPath="formula/FORALLPM_%d.pb" % random_num
    generateFORALLPMFormula(graph, FORALLPMFormulaPath, varMap, state, k=k) # k is the rhs of the dicke state
    end = time.time()
    print("generate PM formula takes %f seconds" % (end - start))
    print("k = %d " % k)    
    constraintList = ["* #variable= 1 #constraint= 1\n"]
    CNFXOR = False
    PBEncoding(FORALLPMFormulaPath, varMap, constraintList)
    constraintList[0] = "* #variable= %d #constraint= %d\n" % (len(varMap),len(constraintList) -1 )
    print("The pbo problem has %d vars and %d cons" % (len(varMap), len(constraintList)-1))
    flag = None
    with open(PBXORFORALLPMFormulaPath,'w+') as f:
        writeConstraintsToFile(f, constraintList, isList = False, form="String")
    if Configuration.FORALLPMMethod == "TutteCNF": 
        CNF, nv = PBEncodingCNF(PBXORFORALLPMFormulaPath, CNFXOR=CNFXOR)
        CNFFormulaPath = "formula/FORALLPM_%d.cnf" % random_num
        FORALLPM_CNF_RES_PATH = "res/FORALLPMCNF_%d.txt" % random_num
        with open (CNFFormulaPath, 'w+') as f:
            f.write("p cnf %d %d \n" % (nv, len(CNF)))
            writeConstraintsToFile(f, CNF, isList = True, form="CNF")
        cmd = "%s %s %s > %s"  % (Configuration.CNFSOLVER_PATH, Configuration.CNFSOLVER_OPTIONS, CNFFormulaPath, FORALLPM_CNF_RES_PATH)
        os.system(cmd)
        with open(FORALLPM_CNF_RES_PATH) as f:
            for line in f.readlines():
                split = line.split()
                if len(split) == 0: continue
                if split[0] == "s":
                    if split[1] == "SATISFIABLE": 
                        flag = False
                        break
                    elif split[1] == "UNSATISFIABLE": 
                        flag = True
                        break
                    else: 
                        print("wrong output from the SAT solver Glucose.")
                        exit(0)
        os.remove(CNFFormulaPath)
        os.remove(FORALLPM_CNF_RES_PATH)
    elif Configuration.FORALLPMMethod == "TuttePBXOR": 
        FORALLPM_PBXOR_RES_PATH = "res/FORALLPMPBXOR_%d.txt" % random_num
        PBXORFORALLPMFormulaPath="formula/FORALLPM_%d.pb" % random_num
        cmd = '%s %s %s > %s' % (Configuration.PBXORSOLVER_PATH, Configuration.PBXORSOLVER_OPTIONS, PBXORFORALLPMFormulaPath, FORALLPM_PBXOR_RES_PATH)
        os.system(cmd)
        flag = readLinpbRes(FORALLPM_PBXOR_RES_PATH, "NEPM", graph, varMap)
        os.remove(FORALLPM_PBXOR_RES_PATH)
        os.remove(PBXORFORALLPMFormulaPath)
    else:
        print("invalid encoding of FORALLPM. Available: TutteCNF, TuttePBXOR")
        exit(0)
    os.remove(FORALLPMFormulaPath)
    return flag

def checkFORALLPMQBF(graph, state, k, QBFFORALLPMFormulaPath="formula/FORALLPM.qbf"): # check the nepm comdition for all legal states. if the extended graph with unassigned edges are true has no illegal PM, return true. otherwise return false.
    varMap = {}
    random_num = random.randint(1,1000000)
    QBFFORALLPMFormulaPath = "formula/FORALLPM_%d.qbf" % random_num
    generateFORALLPMQBFFormula(graph, QBFFORALLPMFormulaPath, varMap, state, k = k)
    FORALLPM_QBF_RES_PATH = "res/FORALLQBF_%d.txt" % random_num
    cmd = '../depqbf/depqbf %s > %s' % (QBFFORALLPMFormulaPath, FORALLPM_QBF_RES_PATH)
    os.system(cmd)
    flag = None
    with open(FORALLPM_QBF_RES_PATH ,'r') as f:
        lines = f.readlines()
        if lines[0] == "SAT\n":
            flag = True
        elif lines[0] == "UNSAT\n": 
            flag = False 
        else:
            print('QBF solver returns no result')
            exit(0)
    os.remove(QBFFORALLPMFormulaPath)
    os.remove(FORALLPM_QBF_RES_PATH)
    return flag

def checkFORALLNEPM(graph, state, k=0, PMFormulaPath="formula/FORALLNEPMformula.hybrid", PBXORPMFormulaPath="formula/FORALLNEPM.pb"): # if the extended graph with unassigned edges are false has no proof of non-existence of PM, return true. Otherwise return true
    start = time.time()
    random_num = random.randint(1,1000000)
    PMFormulaPath="formula/FORALLNEPMformula_%d.hybrid" % random_num
    varMap = generateFORALLNEPMFormula(graph, PMFormulaPath, state, k=k)
    end = time.time()
    print("NEPM formula generated. time used: %f seconds" % (end-start) )
    constraintList = ["* #variable= 1 #constraint= 1\n"]
    PBEncoding(PMFormulaPath, varMap, constraintList)
    constraintList[0] = "* #variable= %d #constraint= %d\n" % (len(varMap), len(constraintList) - 1)
    PBXORPMFormulaPath="formula/FORALLNEPM_%d.pb" % random_num
    flag = None
    os.remove(PMFormulaPath)
    with open(PBXORPMFormulaPath, 'w+') as f:
        writeConstraintsToFile(f, constraintList, isList = False, form="String")
    if Configuration.FORALLNEPMMethod == "EOPB":
        FORALLNEPM_PBRES_PATH = "res/FORALLNEPM_PB_%d.txt" % random_num
        cmd = '%s %s %s > %s' % (Configuration.PBXORSOLVER_PATH, Configuration.PBXORSOLVER_OPTIONS, PBXORPMFormulaPath, FORALLNEPM_PBRES_PATH)
        os.system(cmd)
        flag = readLinpbRes(FORALLNEPM_PBRES_PATH, "PM", graph, varMap)  
        os.remove(FORALLNEPM_PBRES_PATH)
        os.remove(PBXORPMFormulaPath)
    elif Configuration.FORALLNEPMMethod == "EOCNF":
        CNF, nv = PBEncodingCNF(PBXORPMFormulaPath)
        CNFFormulaPath = "formula/FORALLNEPM_%d.cnf" % random_num
        with open (CNFFormulaPath, 'w+') as f:
            f.write("p cnf %d %d \n" % (nv, len(CNF)))
            writeConstraintsToFile(f, CNF, isList = True, form="CNF")
        FORALLNEPM_CNFRES_PATH = "res/FORALLNEPM_CNF_%d.txt" % random_num
        cmd = "%s %s %s > %s"  % (Configuration.CNFSOLVER_PATH, Configuration.CNFSOLVER_OPTIONS, CNFFormulaPath, FORALLNEPM_CNFRES_PATH)
        os.system(cmd)
        with open(FORALLNEPM_CNFRES_PATH) as f:
            for line in f.readlines():
                split = line.split()
                if len(split) == 0: continue
                if split[0] == "s":
                    if split[1] == "SATISFIABLE":
                        flag = False
                        break
                    elif split[1] == "UNSATISFIABLE": 
                        flag = True
                        break
                    else:
                        print("error!")
                        exit(0)
        os.remove(CNFFormulaPath) 
        os.remove(FORALLNEPM_CNFRES_PATH) 
    return flag

def identification(graph, state='GHZ', k = 0,  testing=""):
    # stateInputStyle is in {'name', 'enumerate', 'constraint'}
    # for 'name', state is in {'GHZ','W','Dicke'}
    # for 'enumerate', state is the file name of the list of legal states, e.g., 1,1,1,1 2,2,2,2 3,3,3,3
    # for 'constraint', state is the constraint that defines the legal states, e.g., ae 1 2 3 4 (GHZ state)
    # FORALLPMMethod is from {'Blossom','TutteCNF','TuttePBXOR','QBF'} 
    # FORALLNEPMMethod is from {'SymDet','DP','EOPB','EOCNF'}
    print("state = %s with n = %d, k = %d" % (state, graph.n, k))
    if testing != "FORALLNEPM":
        start = time.time()
        pmFlag = False
        if Configuration.FORALLPMMethod == "Blossom":
            pmFlag = FORALLPMVCByBlossom(graph, state, k)
        elif Configuration.FORALLPMMethod == "TutteCNF" or Configuration.FORALLPMMethod == "TuttePBXOR": 
            pmFlag = checkFORALLPM(graph, state, k)
        elif Configuration.FORALLPMMethod == "QBF":
            pmFlag = checkFORALLPMQBF(graph, state, k)
        else:
            print("invalid FORALLPM method: %s. Available methods: Blossom, TutteCNF, TuttePBXOR, QBF")
            exit(0)
        end = time.time()
        print("n = %d, FORALLPM = %r takes %f seconds by method %s" % (graph.n, pmFlag, (end - start), Configuration.FORALLPMMethod) )
    #if pmFlag == False: return False
    #else: 
    #    print('no illegal PMs')
    if testing != "FORALLPM":
        nepmFlag = False
        start = time.time()
        if Configuration.FORALLNEPMMethod == "EOPB" or Configuration.FORALLNEPMMethod == "EOCNF":
            nepmFlag = checkFORALLNEPM(graph, state, k=k)
        elif Configuration.FORALLNEPMMethod == "SymDet":
            nepmFlag = checkBySymDet(graph,state, k=k)
        elif Configuration.FORALLNEPMMethod == "DP":
            nepmFlag = verifyByDP(graph, state, k=k)
        else:
            print("invalid FORALLNEPM Method: %s " % Configuration.FORALLNEPMMethod)
            print("available FORALLNEPM Methods: SymDet, DP, EOPB, EOCNF")
            exit(0)
        end = time.time()
        print("n = %d, FORALLNEPM = %r takes %f seconds by method %s" % (graph.n, nepmFlag, (end - start), Configuration.FORALLNEPMMethod) )
        return nepmFlag 

if __name__ == '__main__':
    start = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--state',type=str, help='GHZ, W, Dicke')
    parser.add_argument('--graphFile',type=str, help='the input file that encodes a graph')
    parser.add_argument('--breakSymmetry',type=str_to_bool, default=True, help='symmetry breaking for Tutte encoding')
    parser.add_argument('--TseytinEncoding',type=str_to_bool,default=True,help='using Tseytin encoding of the logical OR of two CNF formulas')
    parser.add_argument('--QBFNEPM',type=str_to_bool, default=False, help='use QBF encoding for NEPM instead of Tutte encoding')
    parser.add_argument('--CNFNEPM',type=str_to_bool, default=False, help='use CNF encoding with symmetry for NEPM instead of Tutte encoding')
    parser.add_argument('--FORALLPMMethod',type=str,default="Blossom", help='use enumeration of all colorings')
    parser.add_argument('--FORALLNEPMMethod',type=str,default="EOPB", help='use enumeration of all colorings')
    parser.add_argument('--graphProperty',type=str_to_bool,default=True, help='detect graph symmetry')
    parser.add_argument('--Problem',type=str,default="FORALLPM", help='{FORALLPM, FORALLNEPM}')
    parser.add_argument('--experiment', type=str,default="Dicke",help='{Bi, Dicke, KDicke, SAT}')
    parser.add_argument('--k', type=int,default=0,help='the number of red vertices of legal colorings')
    args = parser.parse_args()
    configurate(SB=args.breakSymmetry, TE=args.TseytinEncoding,CN=args.CNFNEPM, QN=args.QBFNEPM, PMM=args.FORALLPMMethod, NEPMM=args.FORALLNEPMMethod, GP=args.graphProperty)
    graph = Graph()
    graph.readGraph(args.graphFile)
    flag = identification(graph, state=args.state, testing="FORALLPM", k = args.k)

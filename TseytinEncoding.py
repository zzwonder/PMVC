from util import *

def multiLogicalOROfCNFByTseytinEncoding(varMap, CNFList, nameList = []):
    # get the CNF representation of the OR of two CNFs
    allClauses = []
    orVars = []
    for i in range(len(CNFList)):
        CNFVar, CL = TseytinEncodingSingleCNF(CNFList[i],varMap, name=nameList[i])
        allClauses += CL
        orVars.append(CNFVar)
    overallVar = allocateExtraVar(varMap, "Tseytin variable of multiple logical OR")
    for l in orVars:
        allClauses.append([-l, overallVar])
        # X -> x1 or x2 or ...
    orClause = [-overallVar]
    for l in orVars:
        orClause.append(l)
    allClauses.append(orClause)
    allClauses.append([overallVar])
    return overallVar, allClauses

def TseytinEncodingSingleCNF(CNF,varMap, name=None):
    overallVar = allocateExtraVar(varMap, "Tseytin variable of a CNF with name %s" % name)
    CL = [] # constraint list
    #print("CNF=%r" % CNF)
    for index in range(len(CNF)):
        clauseVar = allocateVar(varMap, "Tseytin variable of %d-th clause in the encoding of %s" % (index, name))
        #print("clauesVar = %d " % clauseVar)
        c = CNF[index]
        for l in c: #pass
            CL.append([-l, clauseVar])
        # X -> x1 or x2 or ...
        orClause = [-clauseVar]
        for l in c:
            orClause.append(l)
        CL.append(orClause)
    # A = a1 and a2 ...
    andClause = [overallVar]
    for index in range(len(CNF)):
        clauseVar = varMap["Tseytin variable of %d-th clause in the encoding of %s" % (index, name)]
        andClause.append(-clauseVar)
    CL.append(andClause)
    for index in range(len(CNF)):
        clauseVar = varMap["Tseytin variable of %d-th clause in the encoding of %s" % (index, name)]
        CL.append([clauseVar, -overallVar])
    #CL.append([overallVar]) think about why this line can not exist?
    return overallVar, CL

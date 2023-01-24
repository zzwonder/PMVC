from getStrings import *
def allocateExtraVar(mapping, string):
    number = len(mapping) + 1
    mapping["Unique Variable %d: %s"  % (number, string)] = number
    return number

def allocateVar(mapping, string):
    if string in mapping:
        return mapping[string]
    else:
        number = len(mapping) + 1
        mapping[string] = number
        return number

def readPMfromRes(split, graph):
    # split is the split of vline
    pm = set()
    pmVars = []
    for i in range(min(len(graph.edges), len(split))):
        if split[i][0] == 'x':
            edgeStr = getEdgeString(graph.edges[i])
            pm.add(edgeStr)
    #todo: make the edges as unique id. Then use set inclusion for graphs to see whether the PM is there.
    #print('learned PM: '+repr(pm))
    return pm

def readColoringfromRes(vlineSplit, graph, varMap):
    coloring = {}
    positiveVarSet = set()
    for s in vlineSplit:
        if s[0] == 'x':
            positiveVarSet.add(int(s[1:]))
    for i in range(1, graph.n+1):
        for c in range(1, graph.d+1):
            var = varMap[getVCString(i,c)]
            if var in positiveVarSet:
                coloring[i] = c
                break
    if len(coloring) != graph.n:
        print("incomplete coloring!")
        exit(0)
    return coloring


def writeConstraintsToFile(f, constraintList, isList = False, form="String"):
    for constraint in constraintList:
        if isList:
            if form != "CNF":
                f.write("cnf ")
            for l in constraint:
                if l == 'x':  f.write("x ")
                else:  f.write("%d " % l)
            if form == "CNF": f.write("0")
            f.write("\n")
        else:
            f.write(constraint)

def readLinpbRes(resFile,problemType,graph, varMap): # problemType = {'PM','NEPM'}
    with open(resFile,'r') as f:
        g = open("res/FORALLPMTutte.txt", "w+")
        lines = f.readlines()
        for line in lines:
            split = line.split()
            if len(split) == 0: continue
            if split[0] == 's':
                if split[1] == 'UNSATISFIABLE': return True
                elif split[1] == 'SATISFIABLE': 
                    pass
            if split[0] == 'v':
                #todo: retract the PM and add it to the forbidden list
                if problemType == "PM":
                    pm = readPMfromRes(split[1:],graph)
                    g.write("illegal PM")
                    #g.write(pm)
                if problemType == "NEPM": 
                    eoList = {}
                    for i in range(1,graph.n+1):
                        eoList[i] = []
                    coloring = readColoringfromRes(split[1:], graph, varMap)
                    g.write("no PM for coloring ")
                    g.write(repr(coloring))
        return False

def fillMap(varMap, nv):
    while(len(varMap) < nv):
         allocateExtraVar(varMap,"cardEnc")

def str_to_bool(value):
    if value.lower() in {'false', 'f', '0', 'no', 'n'}:
        return False
    elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
        return True
    raise ValueError('{value} is not a valid boolean value')

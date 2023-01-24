from pysat.pb import *

def PBEncodingCNF(formulaPath, CNFXOR=False):
    CNFList = []
    encoding = 0  
    start = 0
    with open(formulaPath) as f:
        lines = f.readlines()
        for line in lines:
            cnf = None
            split = line.split()
            if split[0] == 'c': continue
            elif split[0] == "*" and split[1] == "xor":
                lits = []
                for i in range(2, len(split) -1 ): 
                    if split[0] == "-":
                        lits.append(-int(split[i][2:]))
                    else: lits.append(int(split[i][1:]))
                if split[-1] == "0": lits[0] *= (-1)
                if CNFXOR:
                    CNFList.append( ['x'] + lits)
                else:
                    blow_clauses,start = de_xor(lits,start)
                    start += 1
                    for b in blow_clauses:
                        cnf = xor2cnf(b)
                        CNFList += cnf
            elif split[0] == "*": 
                start = int(split[2]) + 1
                #print("read nv: %d" % start)
            else: # pb constraints
                lits = []
                coefs = []
                for i in range(int((len(split) - 3)/2)):
                    coefs.append(int(split[i*2]))
                    lits.append(int(split[i*2+1][1:]))
                comparator = split[len(split)-3]
                if comparator == ">=":
                    cnf = PBEnc.atleast(lits=lits, weights=coefs, bound = int(split[-2]), encoding = encoding, top_id = start)
                elif comparator == "<=":
                    cnf = PBEnc.atmost(lits=lits, weights=coefs, bound = int(split[-2]), encoding = encoding, top_id = start)
                elif comparator == "=":
                    cnf = PBEnc.equals(lits=lits, weights=coefs, bound = int(split[-2]), encoding = encoding, top_id = start)
                if cnf.nv > start:
                    start = cnf.nv
                CNFList += cnf
    print("cnf file has %d vars and %d clauses" % (start, len(CNFList)))
    return CNFList, start

def xor2cnf(xor):
    if len(xor)==3:
        return [[-xor[0],-xor[1],xor[2]], [ xor[0],-xor[1],-xor[2]], [-xor[0],xor[1],-xor[2]],[xor[0],xor[1],xor[2]] ]
    if len(xor)==2:
        return [[ xor[0],xor[1]],[-xor[0],-xor[1]]]

def de_xor(llist,start):
    oldstart = start
    exactFlag = 0
    if len(llist)<=3:
        return [list(llist),],start
    else:
        clist = []
        i = 0
        while True:
            if i>=len(llist):
                break
            elif i==len(llist)-1:
                exactFlag = 1
                break
            else:
                clist.append([-llist[i],llist[i+1],start+1])
                start+=1
                i+=2
    if exactFlag == 1:
        flist,_ = de_xor([llist[-1]] + list(range(oldstart+1,start+1)),start)
    else:
        flist,_ = de_xor(range(oldstart+1,start+1),start)
    return clist+flist,_

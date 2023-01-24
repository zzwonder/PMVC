from getStrings import *
from util import *
def PBEncoding(formulaPath, varMap, constraintList, XOR2CNF=False):
    with open(formulaPath) as f:
        lines = f.readlines()
        for line in lines:
            split = line.split()
            if split[0] == 'c': continue
            elif split[0] == 'eo':
                string = ""
                for k in range(1, len(split)):
                    string += ("+1 x%d " % int(split[k]))
                string += " = 1 ;\n"
                constraintList.append(string)
            elif split[0] == 'co':
                string = ""
                for k in range(1, len(split)):
                    string += ("+1 x%d " % int(split[k]))
                string += (" >= %d ;\n" % (graph.n / 2) )
                constraintList.append(string)
            elif split[0] == 'im':
                constraintList.append("-1 x%d +1 x%d >= 0 ; \n" % (int(split[1]), int(split[4])))
                constraintList.append("-1 x%d +1 x%d >= 0 ; \n" % (int(split[1]), int(split[6])))
            elif split[0] == 'nor':
                constraintList.append("-1 x%d -1 x%d >= -1 ; \n" % (int(split[1]), int(split[2])))
            elif split[0] == 'imply':
                constraintList.append("-1 x%d +1 x%d >= 0 ; \n" % (int(split[1]), int(split[3])))
            elif split[0] == 'false':
                constraintList.append("+1 x1 = 2 ;\n")
            elif split[0] == 'x':
                if not XOR2CNF:
                    string = "* xor "
                    for k in range(1, len(split)):
                        string +=("x%d " % int(split[k]))
                    string += "0 \n"
                    constraintList.append(string)
                else: # the following needs to rewritten
                    blow_clauses,start = de_xor(lits,start)
                    start += 1
                    for b in blow_clauses:
                        cnf = xor2cnf(b)
                        CNFList += cnf   
            elif split[0] == 'card':
                string = ""
                for k in range(1, len(split)-3):
                    if int(split[k]) > 0:
                        string += ("+1 x%s " % (split[k]))
                    else:
                        string += ("-1 x%d " % (-int(split[k])))
                string += ("%s %s %s\n" % (split[-3],split[-2],split[-1]))
                constraintList.append(string)
            elif split[0] == 'cc':
                constraintList.append("-1 x%s -1 x%s  +1 x%s >= -1 ;\n" % (split[1], split[4], split[6]) )
                constraintList.append("-1 x%s +1 x%s  -1 x%s >= -1 ;\n" % (split[1], split[4], split[6]) )
            elif split[0] == 'le':
                constraintList.append("+1 x%s +1 x%s +1 x%s -1 x%s -1 x%s >= -1 ;\n" % (split[1],split[5],split[8],split[12],split[14]))
                constraintList.append("-4 x%s -1 x%s -1 x%s +1 x%s +1 x%s >= -2 ;\n" % (split[1],split[5],split[8],split[12],split[14]))
            elif split[0] == 'nae':
                stringneg = ""
                for k in range(1,len(split)):
                    stringneg += ("-1 x%s " % split[k] )
                constraintList.append(stringneg + ">= " + repr(-len(split)+2) + " ;\n")
            elif split[0] == 'ae':
                for k in range(1,len(split)-1):
                    constraintList.append("* xor x%s x%s 0\n" % (split[k],split[k+1]))
            elif split[0] == 'assign':
                constraintList.append("+1 x%s = %s ;\n" % (split[1], split[2]))
            elif split[0] == 'cnf':
                neg = 0
                string = ""
                for i in range(1, len(split)):
                    var = int(split[i])
                    if var>0:
                        string += ("+1 x%d " % var)
                    else:
                        neg +=1
                        string += ("-1 x%d "% abs(var))
                string += (" >= %d ;\n" % (1-neg))
                constraintList.append(string)
            else: 
                print("Unknown prefix: %s" % split[0])

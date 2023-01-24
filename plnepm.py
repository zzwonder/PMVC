def checkNEPM(graph, state, NEPMFormulaPath="nepmformula.txt", PBXORNEPMFormulaPath="pbxornepmformula.txt"): # check the nepm comdition for all legal states. if the extended graph with unassigned edges are true has no illegal PM, return true. otherwise return false.
    varMap = {}
    start = time.time()
    generateNEPMFormula(graph,NEPMFormulaPath,varMap,state)
    end = time.time()
    print("generate NEPM formula takes %f seconds" % (end - start))

    constraintList = ["* #variable= 1 #constraint= 1\n"]
    PBEncoding(NEPMFormulaPath,varMap, constraintList)
    constraintList[0] = "* #variable= %d #constraint= %d\n" % (len(varMap),len(constraintList) -1 )

    with open(PBXORNEPMFormulaPath,'w+') as f:
        writeConstraintsToFile(f, constraintList, isList = False, form="String")

    if Configuration.NEPMMethod == "EOCNF":   
        CNF, nv = PBEncodingCNF(PBXORNEPMFormulaPath, CNFXOR=False)
        CNFFormulaPath = "nepmcnf.cnf"
        with open (CNFFormulaPath, 'w+') as f:
            f.write("p cnf %d %d \n" % (nv, len(CNF)))
            writeConstraintsToFile(f, CNF, isList = True, form="CNF")
        cmd = "../../SATsolvers/glucose/glucose-syrup-4.1/simp/glucose %s > nepmcnfres.txt"  % CNFFormulaPath
        os.system(cmd)
        with open("nepmcnfres.txt") as f:
            for line in f.readlines():
                split = line.split()
                if len(split) == 0: continue
                if split[0] == "s":
                    if split[1] == "SATISFIABLE":
                        return False
                    elif split[1] == "UNSATISFIABLE": return True
                    else:
                        print("error!")
                        exit(0)
    elif Configuration.NEPMMethod == "EOPB":
        print("calling LINPB")
        cmd = '../../linpb/build/linpb %s --print-sol=1 > nepmres_Linpb.txt' % PBXORNEPMFormulaPath
        os.system(cmd)
        return readLinpbRes("nepmres_Linpb.txt", "NEPM", graph, varMap)
    else:
        print("invalid method of NEPM!")
        exit(0)

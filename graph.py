import random
class Graph:
    def __init__(self):
        self.n = 0
        self.m = 0
        self.d = 0
        self.edges = []

    def init(self, n, m, d):
        self.n = n
        self.m = m
        self.d = d

    def getAdjacentEdges(self, v):
        edgeList = []
        for e in self.edges:
            if e[0] == v or e[1] == v: edgeList.append(e)
        return edgeList

    def getNeighbors(self, v):
        neighborList = []
        for e in self.edges:
            if e[0] == v:
                neighborList.append(e[1])
            if e[1] == v:
                neighborList.append(e[0])
        return neighborList

    def readGraph(self, filename):
        with open(filename) as f:
            lines = f.readlines()
            for line in lines:
                split = line.split()
                if split[0] == "c":  continue
                if split[0] == "graph":
                    self.init(int(split[1]), int(split[2]), int(split[3]))
                    continue
                self.edges.append([int(split[0]), int(split[1]), int(split[2]), int(split[3])])

    def generateRandomGraph(self, n, d, p):
        for v in range(1,n+1):
            for u in range(v+1, n+1):
                for cv in range(1,d+1):
                    for cu in range(1,d+1):
                        if random.random() < p:
                            self.edges.append([v,u,cv,cu])
        self.init(n, len(self.edges), d)

    def generateOnlyBiColoredRandomGraph(self, n, d, p):
        for v in range(1,n+1):
            for u in range(v+1, n+1):
                for cv in range(1,d+1):
                    for cu in range(1,d+1):
                        if cu != cv:
                            if random.random() < p:
                                self.edges.append([v,u,cv,cu])
        self.init(n, len(self.edges), d)
    def generateCompleteBipartiteGraph(self, n1, n2, d):
        for v in range(1,n1+1):
            for u in range(n1+1,n1 + n2 + 1):
                for cv in range(1,d+1):
                    for cu in range(1,d+1):
                        self.edges.append([v,u,cv,cu])
        self.init(n1+n2,len(self.edges),d)

    def generateOnlyBiColoredCompleteBipartiteGraph(self, n1, n2, d):
        for v in range(1,n1+1):
            for u in range(n1+1,n1 + n2 + 1):
                for cv in range(1,d+1):
                    for cu in range(1,d+1):
                        if cv != cu:
                            self.edges.append([v,u,cv,cu])
        self.init(n1+n2,len(self.edges),d)

    def generateOnlyBiColoredRandomBipartiteGraph(self, n1, n2, d, p):
        for v in range(1,n1+1):
            for u in range(n1+1,n1 + n2 + 1):
                for cv in range(1,d+1):
                    for cu in range(1,d+1):
                        if cv != cu:
                            if random.random() < p:
                                self.edges.append([v,u,cv,cu])
        self.init(n1+n2,len(self.edges),d)

    def generateBicoloredCompleteGraph(self,n,d):
        for v in range(1, n + 1):
            for u in range(v+1, n + 1):
                for cv in range(1, d + 1):
                    for cu in range(1, d + 1):
                        self.edges.append([v,u,cv,cu])
        self.init(n,n*(n-1)/2*d*d, d)
    
    def generateMonocoloredCompleteGraph(self, n1, n2):
        for v in range(1,n1+1):
            for u in range(n1+1,n1 + n2 + 1):
                self.edges.append([v,u,1,1])
        self.init(n1+n2,len(self.edges),1)

    def generateOnlyBiColoredCompleteGraph(self, n,d):
        for v in range(1, n+1):
            for u in range(v+1, n+1):
                for cv in range(1, d + 1):
                    for cu in range(1, d + 1):
                        if cv != cu:
                            self.edges.append([v,u,cv,cu])
        self.init(n,len(self.edges), d)
    
    def generateDickeGraph(self, n, k):
        print("dicke graph: n= %d, k=%d" % (n,k))
        if k > n/2: 
            k = n-k
        for v in range(1, k+1):
            for u in range(k+1, n+1):
                for cv in range(1, 3):
                    for cu in range(1, 3):
                        if cv != cu:
                            self.edges.append([v,u,cv,cu])
        for v in range(k+1, n+1):
            for u in range(v+1, n+1):
                self.edges.append([v,u,2,2])  
        self.init(n,len(self.edges), 2)

    def generateCompleteGraph(self,n,d):
        for v in range(1, n + 1):
            for u in range(v+1, n + 1):
                for c in range(1, d + 1):
                        self.edges.append([v,u,c,c])
        self.init(n,n*(n-1)/2*d, d)

    def generateCycle(self, n):
        for v in range(n):
            if v % 2 == 0:
                self.edges.append([v+1 , (v+1) % n + 1, 1, 1])
            else:
                self.edges.append([v+1 , (v+1) % n + 1, 2, 2])
        self.init(n,n,2)
    
    def removeRandomEdges(self, numToRemove, seed = None):
        random.seed(seed)
        for i in range(numToRemove):
            self.edges.pop(random.randrange(len(self.edges))) 
        self.init(self.n,len(self.edges),self.d)
    
    def removeSomeMonoColoredEdges(self, numToRemove, k, seed = None):
        random.seed(seed)
        while numToRemove > 0:
            vertex1 = random.randint(k+1, self.n)
            vertex2 = random.randint(k+1, self.n)
            if vertex1 != vertex2:
                #print([min(vertex1, vertex2), max(vertex1, vertex2), 2, 2])
                if [min(vertex1, vertex2), max(vertex1, vertex2), 2, 2] in self.edges: 
                    self.edges.remove([min(vertex1, vertex2), max(vertex1, vertex2), 2, 2])
                    numToRemove -= 1
        self.init(self.n,len(self.edges),self.d)

    def removeCrossEdges(self, numToRemove, k, seed = None):
        random.seed(seed)
        while numToRemove > 0:
            vertex1 = random.randint(1, k)
            vertex2 = random.randint(k+1, self.n)
            c1 = random.randint(1,2)
            c2 = 1
            if c1 == 1: c2 = 2
            if [vertex1, vertex2, c1, c2] in self.edges:
                self.edges.remove([vertex1, vertex2, c1, c2])
                numToRemove -= 1
            print("remove")
            print([vertex1, vertex2, c1, c2])
        self.init(self.n,len(self.edges),self.d)
 
    def addRandomEdges(self, k, seed = None, monoColor=True):
        random.seed(seed)
        for i in range(k):
            edge = random.sample(range(1, self.n), 2)
            color1 = random.randint(1, self.d)
            #color2 = random.randint(1, self.d)
            self.edges.append([min(edge), max(edge), color1, color1]) 
        self.init(self.n,len(self.edges),self.d)

    def regularize(self):
        for i in range(len(self.edges)):
            if self.edges[i][0]>self.edges[i][1]:
                temp = self.edges[i][1]
                self.edges[i][1] = self.edges[i][0]
                self.edges[i][0] = temp
                temp = self.edges[i][3]
                self.edges[i][3] = self.edges[i][2]
                self.edges[i][2] = temp

    def writeToFile(self, filepath):
        with open(filepath, "w+") as f:
            f.write("graph %d %d %d\n" % (self.n, len(self.edges), self.d))
            for e in self.edges:
                f.write("%d %d %d %d\n" % (e[0], e[1], e[2], e[3]))

    def writeToClingoFile(self, filepath):
        with open(filepath, "w+") as f:
            for e in self.edges:
                f.write("edge(%d,%d,%d,%d).\n" % (e[0], e[1], e[2], e[3]))


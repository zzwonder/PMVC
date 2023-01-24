def generateKDickeGraphBenchmarks():
    for size in range(10,91,5):
        for k in range(int(size * 0.1), int(size * 0.5), int(size*0.1)):
            for i in range(10):
                graph = Graph()
                graph.generateDickeGraph(size, k)
                seed = i
                graph.removeSomeMonoColoredEdges(0.4 * (size - k)*(size - k - 1) / 2, k, seed = i)
                graph.regularize()
                graph.writeToFile("graphs/Dicke_deleteNsquare_n%d_k%d_%d.txt" % (size, k, i))

                graph = Graph()
                graph.generateDickeGraph(size, k)
                seed = i
                graph.removeCrossEdges(2, k, seed = i)
                graph.regularize()
                graph.writeToFile("graphs/Dicke_delete2_n%d_k%d_%d.txt" % (size, k, i))
    exit(0)

def generateExp2Benchmarks():
    for size in range(6,40,2):
        for k in range(int(size/2), int(size/2)+1 ):
            graph = Graph()
            graph.generateOnlyBiColoredCompleteBipartiteGraph(int(size/2), int(size/2), 2)
            graph.writeToFile("benchmarks/Experiment2/Dicke_n%d_k%d.txt" % (size, k))

    for k in range(1, 19):
        graph = Graph()
        graph.generateDickeGraph(36, k)
        graph.writeToFile("benchmarks/Experiment2/Dicke_n%d_k%d.txt" % (36, k))

def generateExp1Benchmarks():
    for size in range(10,70,2):
        graph = Graph()
        graph.generateMonocoloredCompleteGraph(size, size+2)
        graph.writeToFile("benchmarks/Experiment1/CompleteBipartite_%d_%d.txt" % (size, size-2))


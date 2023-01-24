import networkx as nx
from graph import *

def detectGraphSymmetry(G):
    nxG = nx.Graph()
    edgeColor = {}
    edgeList = []
    starting = G.n + 1
    for e in G.edges:
        edge = (e[0],e[1])
        if e[2] == e[3]:
            edgeList.append(edge)
            edgeColor[edge] = e[2]
        else:
            edge1 = (e[0], starting)
            edge2 = (starting, starting+1)
            starting += 1
            edge3 = (starting, e[1])
            starting += 1
            edgeColor[edge1] = e[2]
            edgeColor[edge2] = 0
            edgeColor[edge3] = e[3]
            edgeList.append(edge1)
            edgeList.append(edge2)
            edgeList.append(edge3)
    nxG.add_edges_from(edgeList)
    ismags = nx.algorithms.isomorphism.ISMAGS(nxG, nxG)
    per, coset = ismags.analyze_symmetry(graph=nxG, node_partitions=[set(nxG.nodes)],edge_colors= edgeColor)
    print(coset)
    #for p in per:
    #    print(p)
    #    print("\n")

G = nx.Graph()
#G.add_edges_from([[1,2],[1,3],[1,4],[1,5],[2,3],[2,4],[2,5],[3,4],[3,5],[4,5]])
#G.add_edges_from([[1,3],[3,4],[2,4],[1,5],[5,6],[2,6]])
#edgeColors = {(1,3):1, (3,4):0, (2,4):2, (1,5):2,(5,6):0, (2,6):1}

graph = Graph()
#graph.generateOnlyBiColoredCompleteGraph(20, 2)
graph.generateOnlyBiColoredCompleteBipartiteGraph(10,10, 2)
ratio = 0.0
graph.removeRandomEdges(int(ratio * len(graph.edges)))

#print(ismags.analyze_symmetry(graph=G, node_partitions=[set(G.nodes)],edge_colors= edgeColors))
detectGraphSymmetry(graph)
                                            

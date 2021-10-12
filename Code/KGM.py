#Knowledge Graph Merger

#---- Libraries -----
from HelpFiles.FileModules import *
from GraphEngine.GraphEngine import *
from MergeEngine.MergeEngine import MergeEngine
from Evaluation.Evaluation import Evaluator

#------- Main -------

#Setup GraphEngine
CONFIG_GE= load_config("../Data/ConfigFiles/CONFIG_GE.yaml")
GE = GraphEngine(CONFIG_GE)
print(CONFIG_GE)

#Setup MergeEngine
CONFIG_ME = load_config("../data/ConfigFiles/CONFIG_ME.yaml")
ME = MergeEngine(CONFIG_ME)
print(CONFIG_ME)

#Setup Evaluator
Evaluate = Evaluator()

#Simulate


#Evaluate



#Test
G = Graph()
nodes = [Node("A"), Node("B"), Node("C"), Node("D")]
edges = [ Edge(nodes[0], nodes[1], "part of"), 
          Edge(nodes[1], nodes[2], "subclass of"), 
          Edge(nodes[2], nodes[3], "Parent of"), 
          Edge(nodes[3], nodes[0], "Creative"), 
          Edge(nodes[0], nodes[2], "Something")]
G.add_nodes(nodes)
G.add_edges(edges)
G.print_info()

plot = Visualize.visualize_graph_network(G, [750, 750])

cv2.imshow('Graph', plot)
cv2.waitKey(0)
cv2.destroyAllWindows()
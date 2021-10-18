#Knowledge Graph Merger

#---- Libraries -----
from HelpFiles.FileModules import *
from GraphEngine.GraphEngine import *
from GraphEngine.Visualization import *
from MergeEngine.MergeEngine import *
from Evaluation.Evaluation import Evaluator

import cv2
#------- Main -------

#Setup GraphEngine
CONFIG_GE= load_config("../Data/ConfigFiles/CONFIG_GE.yaml")
network = GraphEngine.generate_network(CONFIG_GE)

Visualize().network(network)
#Visualize().bubbles(network.bubbles)
#Visualize().websites(network.websites)


#Setup MergeEngine
CONFIG_ME = load_config("../data/ConfigFiles/CONFIG_ME.yaml")
ME = MergeEngine(CONFIG_ME)


#Setup Evaluator
Evaluate = Evaluator()

#Simulate


#Evaluate





#Test
network, bubbles, websites, pages = test_data()

Visualize().pages(pages[:2])
Visualize().websites(websites)
Visualize().bubbles(bubbles)
Visualize().network(network)

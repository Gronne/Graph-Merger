#Knowledge Graph Merger

#---- Libraries -----
from HelpFiles.FileModules import *
from GraphEngine.GraphEngine import GraphEngine
from MergeEngine.MergeEngine import MergeEngine
from Evaluation.Evaluation import Evaluator
from LearningTree.LearningTree import LearningTree

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



#Extra text

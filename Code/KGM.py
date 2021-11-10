#Knowledge Graph Merger

#---- Libraries -----
from HelpFiles.FileModules import *
from GraphEngine.GraphEngine import *
from GraphEngine.Visualization import *
from MergeEngine.MergeEngine import *
from Evaluation.Evaluation import Evaluate
#------- Main -------

#Generate Simulation
CONFIG_GE= load_config("../Data/ConfigFiles/CONFIG_GE.yaml")
ground_truth, network = GraphEngine.generate(CONFIG_GE)

#Merge Network
CONFIG_ME = load_config("../data/ConfigFiles/CONFIG_ME.yaml")
knowledge_tree = MergeEngine.merge(network)

#Evaluate Merge
Evaluate = Evaluate.merge_engine(ground_truth, network, knowledge_tree)





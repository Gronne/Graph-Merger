import numpy
import random 

from GraphEngine.Structures import *
from GraphEngine.KnowledgeGraph import *
from GraphEngine.KnowledgeGenerator import KnowledgeGenerator
from GraphEngine.NetworkGenerator import NetworkGenerator
from GraphEngine.KnowledgeTreeStructures import *
from GraphEngine.Visualization import Visualize
from GraphEngine.Structures import Page




class GraphEngine:        

    def generate(CONFIG):
        random.seed(CONFIG["Seed"])
        numpy.random.seed(CONFIG["Seed"])
        knowledge_tree = GraphEngine._generate_knowledge(CONFIG)
        network = GraphEngine._generate_network(CONFIG, knowledge_tree)        
        GraphEngine._obstruct_knowledge(CONFIG, knowledge_tree, network)
        return knowledge_tree, network

    def _generate_knowledge(CONFIG):
        knowledge_tree = KnowledgeTree()
        KnowledgeGenerator.generate_topics_and_atoms(CONFIG, knowledge_tree)
        KnowledgeGenerator.generate_atom_knowledge(CONFIG, knowledge_tree)
        KnowledgeGenerator.generate_sub_layers(CONFIG, knowledge_tree)
        KnowledgeGenerator.generate_names(CONFIG, knowledge_tree)
        return knowledge_tree

    def _generate_network(CONFIG, knowledge_tree):
        network = Network()
        while NetworkGenerator.is_knowledge_satisfied(CONFIG, knowledge_tree, network) == False:
            for _ in range(0, CONFIG["Network"]["SatisfactionFrequency"]):
                website = NetworkGenerator.generate_website(CONFIG, knowledge_tree)
                network.add_website(website)
                print(f"Number of Websites: {len(network.websites)}")
        print(f"Number of Websites: {len(network.websites)}")
        print(f"Number of Pages: " + str(len([page for website in network.websites for page in website.pages])))
        NetworkGenerator.generate_external_links(CONFIG, knowledge_tree, network)
        return network

    
    def _obstruct_knowledge(CONFIG, knowledge_tree, network):
        pass
        












class Mutator:
    pass




















def test_data():
    def small_graph():
        class_nodes = [Node("Dyr"), Node("Transportmiddel")]
        nodes = [Node("Hund"), Node("Kat"), Node("Bil"), Node("Fly")]
        class_edges = [ nodes[0].add_class(class_nodes[0]), 
                        nodes[1].add_class(class_nodes[0]),
                        nodes[2].add_class(class_nodes[1]),
                        nodes[3].add_class(class_nodes[1])]
        edges = [ Edge(nodes[0], nodes[1], "part of"), 
                Edge(nodes[1], nodes[0], "part of"),
                Edge(nodes[0], nodes[1], "Something"),
                Edge(nodes[1], nodes[0], "Something"),
                Edge(nodes[1], nodes[2], "subclass of"), 
                Edge(nodes[2], nodes[3], "Parent of"), 
                Edge(nodes[3], nodes[0], "Creative"), 
                Edge(nodes[0], nodes[2], "Something")]
        return Graph(nodes + class_nodes, edges + class_edges)


    def large_graph():
        nodes = [Node("Hund"), Node("Kat"), Node("Bil"), Node("Fly"), Node("Abe"), Node("Banan"), Node("Circus"), Node("Dommer"), Node("Endelig")]
        edges = [ Edge(nodes[0], nodes[1], "connection"),
                Edge(nodes[1], nodes[2], "connection"),
                Edge(nodes[2], nodes[3], "connection"),
                Edge(nodes[3], nodes[4], "connection"),
                Edge(nodes[4], nodes[5], "connection"),
                Edge(nodes[5], nodes[6], "connection"),
                Edge(nodes[6], nodes[7], "connection"),
                Edge(nodes[7], nodes[8], "connection"),
                Edge(nodes[8], nodes[0], "connection"),
                Edge(nodes[0], nodes[3], "connection"),
                Edge(nodes[0], nodes[5], "connection"),
                Edge(nodes[0], nodes[7], "connection"),
                Edge(nodes[3], nodes[0], "connection"),
                Edge(nodes[3], nodes[8], "connection"),
                Edge(nodes[5], nodes[3], "connection")]
        return Graph(nodes, edges)


    pages = [Page(small_graph()), Page(large_graph()), Page(), Page(), Page(), Page(), Page(), Page(), Page()]

    websites : List[Website] = [ Website([pages[0], pages[1], pages[2]]), 
                                Website([pages[3]]), 
                                Website([pages[4], pages[5], pages[6], pages[7], pages[8]])]

    websites[0].add_internal_link(pages[0], pages[1])
    websites[0].add_internal_link(pages[1], pages[0])
    websites[0].add_internal_link(pages[0], pages[2])
    websites[0].add_internal_link(pages[2], pages[0])

    websites[2].add_internal_link(pages[4], pages[5])
    websites[2].add_internal_link(pages[5], pages[4])
    websites[2].add_internal_link(pages[4], pages[6])
    websites[2].add_internal_link(pages[6], pages[4])
    websites[2].add_internal_link(pages[4], pages[7])
    websites[2].add_internal_link(pages[7], pages[8])
    websites[2].add_internal_link(pages[8], pages[4])


    websites[0].add_external_link(pages[0], pages[3])
    websites[0].add_external_link(pages[0], pages[4])

    websites[2].add_external_link(pages[4], pages[0])
    websites[2].add_external_link(pages[6], pages[3])
    websites[2].add_external_link(pages[6], pages[0])


    bubbles = [Bubble([websites[0], websites[1]]), Bubble([websites[1], websites[2]])]

    single_page = Page()
    website_alone = Website([single_page])

    website_alone.add_external_link(single_page, pages[0])

    network = Network([website_alone], bubbles)

    return network, bubbles, websites, pages









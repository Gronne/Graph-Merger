from typing import List, Union, Dict, Set
import cv2
import random
import networkx
from networkx.drawing.nx_pydot import graphviz_layout

from GraphEngine.KnowledgeTreeStructures import KnowledgeTree
from GraphEngine.KnowledgeGraph import *
from GraphEngine.Structures import *
from GraphEngine.VisualizationEngine import GraphEngineVisualizer



class Visualize:
    def __init__(self, size = [800, 1000]):
        self._size = size

    def knowledge_tree(self, knowledge_tree : KnowledgeTree, normal_graph = True):
        plot = KnowledgeTreeVisualizer(self._size, normal_graph).visualize(knowledge_tree)
        self._plot(plot, "Knowledge Tree")

    def page(self, page: Page):
        plot = PageVisualizer(self._size).visualize(page)
        self._plot(plot, "Page")

    def pages(self, pages: List[Page]):
        for page in pages:
            self.page(page)

    def website(self, website : Website):
        plot = WebsiteVisualizer(self._size).visualize(website)
        self._plot(plot, "Website")

    def websites(self, websites: List[Website]):
        for website in websites:
            self.website(website)

    def bubble(self, bubble : Bubble):
        plot = BubbleVisualizer(self._size).visualize(bubble)
        self._plot(plot, "Bubble")

    def bubbles(self, bubbles : List[Bubble]):
        for bubble in bubbles:
            self.bubble(bubble)

    def network(self, network : Network):
        plot = NetworkVisualizer(self._size).visualize(network)
        self._plot(plot, "Network")

    def networks(self, networks : List[Network]):
        for network in networks:
            self.network(network)

    def _plot(self, plot, name):
        cv2.imshow(name, plot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()






class KnowledgeTreeVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000], normal_graph = True):
        super().__init__(size, (0.8, 0.2), 0) #0 = Horizontal, 1 = Vertical
        self._normal_graph = normal_graph

    def _info_plot_strings(self, knowledge_tree : KnowledgeTree):
        strings = [ "Knowledge Tree",
                    "Nr. of Topics: " + str(len(knowledge_tree.topics)),
                    "Nr. of Subtopics: " + str(len(knowledge_tree.subtopics)),
                    "Nr. of Atoms: " + str(len(knowledge_tree.atoms)),
                    "Max layers: " + str(max([knowledge_tree.get_layer(topic) for topic in knowledge_tree.topics])),
                    "Min layers: " + str(min([knowledge_tree.get_layer(topic) for topic in knowledge_tree.topics])),
                    "Different Names: " + str(len(knowledge_tree.names)),
                    "Triples: " + str(sum([len(atom.triples) for atom in knowledge_tree.atoms])) ]
        return strings

    def _find_node_positions(self, knowledge_tree : KnowledgeTree, node_ids, edge_node_ids):
        if self._normal_graph:
            return super()._find_node_positions(knowledge_tree, node_ids, edge_node_ids)
        graph = networkx.Graph()
        graph.add_nodes_from(node_ids)
        graph.add_edges_from(edge_node_ids)
        node_positions = graphviz_layout(graph, prog="dot", root=knowledge_tree.root.id)
        largest_xy = (0, 0)
        for pos_key in node_positions:
            pos = node_positions[pos_key]
            if pos[0] > largest_xy[0]:
                largest_xy = (pos[0], largest_xy[1])
            if pos[1] > largest_xy[1]:
                largest_xy = (largest_xy[0], pos[1])
        for pos_key in node_positions:
            pos = node_positions[pos_key]
            node_positions[pos_key] = ((pos[0]/(largest_xy[0]/2))-1, (pos[1]/(largest_xy[1]/2))-1)
        return node_positions

    def _node_text(self, node):
        return node.name

    def _edge_text(self, edge):
        return " "






class PageVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0) #0 = Horizontal, 1 = Vertical

    def _info_plot_strings(self, page : Page):
        website_id = str(page.website.id) if page.website != None else None
        website_string = "Website:"+str(website_id)
        page_string = "Page: "+str(page.id)
        return [page_string, website_string]

    def _node_text(self, node):
        return node.name

    def _edge_text(self, edge):
        return str(edge.label)





class WebsiteVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _info_plot_strings(self, website : Website, size):
        website_string = "Website: " + str(website.id)
        page_strings = ["Page: " + str(page_id) for page_id in website.page_ids]
        return [website_string] + page_strings

    def _node_text(self, node):
        return "Page: " + str(node.id)

    def _edge_text(self, edge):
        return " "





class BubbleVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _info_plot_strings(self, bubble : Bubble, size):
        bubble_string = "Bubble"
        website_strings = ["Website: " + str(website_id) for website_id in bubble.website_ids]
        return [bubble_string] + website_strings

    def _node_text(self, node):
        return "Website:" + str(node.id)

    def _edge_text(self, edge):
        edges = [link for link in edge.from_page.website.external_links if link.to_page.website.id == edge.to_page.website.id]
        return " " + str(len(edges)) + " "





class NetworkVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)
        self._network = None

    def visualize(self, network):
        self._network = network
        return super().visualize(network)

    def _info_plot_strings(self, network : Network, size):
        strings = [ "Network", 
                    "Nr. of bubbles: " + str(len(network.bubbles)), 
                    "Nr. of websites: " + str(len(network.websites)), 
                    "Nr. of pages: " + str(sum([len(website.pages) for website in network.websites])), 
                    "Nr. of internal links: " + str(sum([len(website.internal_links) for website in network.websites])), 
                    "Nr. of external links: " + str(sum([len(website.external_links) for website in network.websites])) ]
        return strings

    def _node_text(self, node):
        return "Website:" + str(node.id)

    def _edge_text(self, edge):
        edges = [link for link in edge.from_page.website.external_links if link.to_page.website.id == edge.to_page.website.id]
        return " " + str(len(edges)) + " "

    def _place_circle(self, layout, website, coor, circle_radius, circle_border):
        bubbles = self._network.get_bubbles(website)
        if len(bubbles):
            for count, bubble in enumerate(bubbles):
                random.seed(bubble.id)
                layout =  cv2.circle(layout, coor, int(circle_radius)+(circle_border*count), (int(random.random()*255), int(random.random()*255), int(random.random()*255)), circle_border)
        else:
            layout = super()._place_circle(layout, website, coor, circle_radius, circle_border)
        return layout



















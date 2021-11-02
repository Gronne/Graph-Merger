from typing import List, Union, Dict, Set
import cv2
import random

from GraphEngine.KnowledgeGraph import *
from GraphEngine.Structures import *
from GraphEngine.VisualizationEngine import GraphEngineVisualizer



class Visualize:
    def __init__(self, size = [800, 1000]):
        self._size = size

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





class PageVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0) #0 = Horizontal, 1 = Vertical

    def _create_info_plot(self, page : Page, size):
        layout = self._generate_layout(size)
        website_id = str(page.website.id) if page.website != None else None
        min_size = size[0] if size[0] < size[1] else size[1]
        page_info_start_coor = (size[1]/2, int(size[0]/2-min_size*0.2))
        web_info_start_coor = (size[1]/2, int(size[0]/2+min_size*0.2))
        layout = self._place_text(layout, "Page: "+str(page.id), page_info_start_coor, min_size*0.9)
        layout = self._place_text(layout, "Website:"+str(website_id), web_info_start_coor, min_size*0.9)
        return layout

    def _node_text(self, node):
        return node.name

    def _edge_text(self, edge):
        return str(edge.label)





class WebsiteVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _create_info_plot(self, website : Website, size):
        layout = self._generate_layout(size)
        min_size = size[0] if size[0] < size[1] else size[1]
        number_of_elements = len(website.pages)+2 # +1 for the website, +1 for distance
        start_coor = (size[1]/2, int(size[0]/2-(min_size*0.2 * (number_of_elements/2))))
        layout = self._place_text(layout, "Website: "+str(website.id), start_coor, min_size*0.9)
        for page_count, page_id in enumerate(website.page_ids):
            page_info_start_coor = (start_coor[0], start_coor[1]+min_size*0.2*(page_count+2))
            layout = self._place_text(layout, "page:"+str(page_id), page_info_start_coor, min_size*0.9)
        return layout

    def _node_text(self, node):
        return "Page: " + str(node.id)

    def _edge_text(self, edge):
        return " "





class BubbleVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _create_info_plot(self, bubble : Bubble, size):
        layout = self._generate_layout(size)
        min_size = size[0] if size[0] < size[1] else size[1]
        number_of_elements = len(bubble.websites)+2 # +1 for the website, +1 for distance
        start_coor = (size[1]/2, int(size[0]/2-(min_size*0.2 * (number_of_elements/2))))
        layout = self._place_text(layout, "Bubble", start_coor, min_size*0.9)
        for page_count, page_id in enumerate(bubble.website_ids):
            page_info_start_coor = (start_coor[0], start_coor[1]+min_size*0.2*(page_count+2))
            layout = self._place_text(layout, "page:"+str(page_id), page_info_start_coor, min_size*0.9)
        return layout

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

    def _create_info_plot(self, network : Network, size):
        layout = self._generate_layout(size)
        min_size = size[0] if size[0] < size[1] else size[1]
        number_of_elements = 6+1 #+1 for distance
        start_coor = (size[1]/2, int(size[0]/2-(min_size*0.2 * (number_of_elements/2))))
        layout = self._place_text(layout, "Network", start_coor, min_size*0.9)
        layout = self._place_text(layout, "Nr. of bubbles: " + str(len(network.bubbles)), (start_coor[0], start_coor[1]+min_size*0.2*2), min_size*0.9)
        layout = self._place_text(layout, "Nr. of websites: " + str(len(network.websites)), (start_coor[0], start_coor[1]+min_size*0.2*3), min_size*0.9)
        layout = self._place_text(layout, "Nr. of pages: " + str(sum([len(website.pages) for website in network.websites])), (start_coor[0], start_coor[1]+min_size*0.2*4), min_size*0.9)
        layout = self._place_text(layout, "Nr. of internal links: " + str(sum([len(website.internal_links) for website in network.websites])), (start_coor[0], start_coor[1]+min_size*0.2*5), min_size*0.9)
        layout = self._place_text(layout, "Nr. of external links: " + str(sum([len(website.external_links) for website in network.websites])), (start_coor[0], start_coor[1]+min_size*0.2*6), min_size*0.9)
        return layout

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



















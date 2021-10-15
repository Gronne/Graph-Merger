from typing import List, Union, Dict, Set
import networkx
import cv2
from networkx.algorithms.distance_measures import radius
import numpy
import math

from GraphEngine.KnowledgeGraph import *
from GraphEngine.Structures import *



class Visualize:
    def __init__(self, size = [500, 500]):
        self._size = size

    def page(self, page: Page):
        plot = PageVisualizer(self._size).visualize(page)
        self._plot(plot, "Page")

    def website(self, website : Website):
        plot = WebsiteVisualizer(self._size).visualize(website)
        self._plot(plot, "Website")

    def bubble(self, bubble : Bubble):
        plot = WebsiteVisualizer(self._size).visualize(bubble)
        self._plot(plot, "Bubble")

    def network(self, network : Network):
        plot = WebsiteVisualizer(self._size).visualize(network)
        self._plot(plot, "Network")

    def _plot(self, plot, name):
        cv2.imshow(name, plot)
        cv2.waitKey(0)
        cv2.destroyAllWindows()




class GraphEngineVisualizer:
    def __init__(self, size, size_distribution, axis):
        self._axis = axis
        self._graph_size = self._calc_graph_size(size, size_distribution, axis)
        self._info_size = self._calc_info_size(size, size_distribution, axis)

    def _calc_graph_size(self, size, size_distribution, axis):
        vertical = [int(size[0]*size_distribution[0]), size[1]]
        horizontal = [size[0], int(size[1]*size_distribution[0])]
        return horizontal if axis == 0 else vertical

    def _calc_info_size(self, size, size_distribution, axis):
        vertical = [int(size[0]*size_distribution[1]), size[1]]
        horizontal = [size[0], int(size[1]*size_distribution[1])]
        return horizontal if axis == 0 else vertical
        
    def visualize(self, obj):
        _graph_plot = self._create_graph_plot(obj, self._graph_size)
        _into_plot = self._create_info_plot(obj, self._info_size)
        return numpy.concatenate((_into_plot, _graph_plot), axis = 1-self._axis) 

    def _create_graph_plot(self, obj, plot_size):
        raise Exception("Implement '_plot_graph(obj, plot_size) -> plot' in class that is a child of GraphEngineVisualizer")

    def _create_info_plot(self, obj, plot_size):
        raise Exception("Implement '_plot_info(obj, plot_size) -> plot' in class that is a child of GraphEngineVisualizer")

    def _get_node_positions(self, obj : object) -> Dict:
        node_ids, edge_node_ids = self._get_graph_components(obj)
        graph = networkx.DiGraph()
        graph.add_nodes_from(node_ids)
        graph.add_edges_from(edge_node_ids)
        return networkx.drawing.spring_layout(graph)     

    def _get_graph_components(self, obj : object):
        raise Exception("Implement '_get_graph_components(object) -> (node_ids, edge_node_ids)'")

    def _generate_layout(self, size: List[int]):
        layout = numpy.zeros(size + [3],dtype=numpy.uint8)
        layout.fill(255)
        return layout
        






class PageVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0) #0 = Horizontal, 1 = Vertical

    def _create_graph_plot(self, page : Page, size):
        node_pos = self._get_node_positions(page)
        layout = self._generate_layout(size)
        layout = VisualizerBaseFunctionality._place_nodes(layout, size, page.graph, node_pos)
        layout = VisualizerBaseFunctionality._place_edges(layout, size, page.graph, node_pos)
        return layout

    def _create_info_plot(self, page : Page, size):
        layout = self._generate_layout(size)
        website_id = str(page.website.id) if page.website != None else None
        layout = cv2.putText(layout, "Page: " + str(page.id), (0+5, int(size[0]/2)-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        layout = cv2.putText(layout, "Website: " + str(website_id), (0+5, int(size[0]/2)+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        return layout

    def _get_graph_components(self, page: Page):
        node_ids = page.graph.get_node_ids()
        edge_node_ids = page.graph.get_edge_node_ids()
        return node_ids, edge_node_ids






class WebsiteVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _create_graph_plot(self, website : Website, size):
        node_ids, edge_node_ids = self._get_graph_components(website)
        node_pos = self._get_node_positions(node_ids, edge_node_ids)

    def _create_info_plot(self, website : Website, size):
        pass

    def _get_graph_components(self, website : Website):
        node_ids = website.page_ids
        edge_node_ids = [(pair[0].id, pair[1].id) for pair in website.internet_link_pairs]
        return node_ids, edge_node_ids




class BubbleVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _create_graph_plot(self, bubble : Bubble, size):
        node_pos = self._get_node_positions(bubble)

    def _create_info_plot(self, bubble : Bubble, size):
        pass

    def _get_graph_components(self, bubble : Bubble):
        node_ids = [website.id for website in bubble.websites]
        edge_node_ids = [(pair[0].id, pair[1].id) for pair in bubble.external_link_pairs]
        return node_ids, edge_node_ids




class NetworkVisualizer(GraphEngineVisualizer):
    def __init__(self, size = [800, 1000]):
        super().__init__(size, (0.8, 0.2), 0)

    def _create_graph_plot(self, network : Network, size):
        node_pos = self._get_node_positions(network)

    def _create_info_plot(self, network : Network, size):
        pass

    def _get_graph_components(self, network : Network):
        node_ids = [website.id for website in network.websites]
        edge_node_ids = [(pair[0].id, pair[1].id) for pair in network.website_link_pairs]
        return node_ids, edge_node_ids












class VisualizerBaseFunctionality:
    def _place_edges(layout, size, graph, node_pos):
        nr_of_nodes = len(graph.get_node_ids())
        for edge in graph.get_edges():
            coor_from = VisualizerBaseFunctionality._transform_coors(size, node_pos[edge.from_node.id])
            coor_to = VisualizerBaseFunctionality._transform_coors(size, node_pos[edge.to_node.id])
            layout = VisualizerBaseFunctionality._add_arrow_and_type(layout, size, graph, edge, nr_of_nodes, coor_from, coor_to)
        return layout

    def _add_arrow_and_type(layout, img_size, graph, edge, nr_of_nodes, coor_from, coor_to):
        radian_offset = VisualizerBaseFunctionality._calc_radian_offset(graph, edge)
        radius = VisualizerBaseFunctionality._calc_full_circle_radius(img_size, nr_of_nodes)

        if edge.from_node.id < edge.to_node.id:
            angle_from = math.atan(abs(coor_from[1]-coor_to[1])/abs(coor_from[0]-coor_to[0])) + radian_offset
            angle_to = math.atan(abs(coor_from[1]-coor_to[1])/abs(coor_from[0]-coor_to[0])) - radian_offset
        else:
            angle_from = math.atan(abs(coor_from[1]-coor_to[1])/abs(coor_from[0]-coor_to[0])) - radian_offset
            angle_to = math.atan(abs(coor_from[1]-coor_to[1])/abs(coor_from[0]-coor_to[0])) + radian_offset
        
        height_from = int(radius*math.sin(angle_from))
        width_from = int(radius*math.cos(angle_from))

        height_to = int(radius*math.sin(angle_to))
        width_to = int(radius*math.cos(angle_to))
    
        if (coor_to[0] - coor_from[0]) >= 0 and (coor_to[1] - coor_from[1]) >= 0:   
            new_coor_from = (coor_from[0] + width_from, coor_from[1] + height_from)
            new_coor_to = (coor_to[0] - width_to, coor_to[1] - height_to)
        elif (coor_to[0] - coor_from[0]) < 0 and (coor_to[1] - coor_from[1]) >= 0:
            new_coor_from = (coor_from[0] - width_from, coor_from[1] + height_from)
            new_coor_to = (coor_to[0] + width_to, coor_to[1] - height_to)
        elif (coor_to[0] - coor_from[0]) < 0 and (coor_to[1] - coor_from[1]) < 0:
            new_coor_from = (coor_from[0] - width_from, coor_from[1] - height_from)
            new_coor_to = (coor_to[0] + width_to, coor_to[1] + height_to)
        elif (coor_to[0] - coor_from[0]) >= 0 and (coor_to[1] - coor_from[1]) < 0:
            new_coor_from = (coor_from[0] + width_from, coor_from[1] - height_from)
            new_coor_to = (coor_to[0] - width_to, coor_to[1] + height_to)

        arrow_img = cv2.arrowedLine(layout, new_coor_from, new_coor_to, (0, 0, 0), 4)
        text_img = VisualizerBaseFunctionality._add_text_to_arrow(arrow_img, edge.type, new_coor_from, new_coor_to)
        return text_img

    def _add_text_to_arrow(img, text, from_coor, to_coor):
        center = (from_coor[0]-((from_coor[0]-to_coor[0])/2), from_coor[1]-((from_coor[1]-to_coor[1])/2))
        arrow_length = math.sqrt((from_coor[0]-to_coor[0])**2 + (from_coor[1]-to_coor[1])**2)
        text_font = cv2.FONT_HERSHEY_SIMPLEX
        text_thickness = int(math.ceil(arrow_length/(len(text)*20)))
        axis = 0 if abs(from_coor[0]-to_coor[0]) > abs(from_coor[1]-to_coor[1]) else 1
        text_scale = abs(from_coor[axis]-to_coor[axis])/300
        text_size, _ = cv2.getTextSize(text, text_font, text_scale, text_thickness)
        text_start = (int(center[0] - text_size[0] / 2), int(center[1] + text_size[1] / 2)-(text_size[1]))
        return cv2.putText(img, text, text_start, text_font, text_scale, (255, 0, 0), text_thickness, cv2.LINE_AA)

    def _calc_radian_offset(graph, edge):
        edges_between_nodes = graph.get_edges_between(edge.from_node, edge.to_node)
        sorted_edge_ids = sorted([edge.id for edge in edges_between_nodes])
        index = sorted_edge_ids.index(edge.id)
        full_offset = (6.28/18) * (len(edges_between_nodes)-1)
        return -(full_offset/2) + ((6.28/18) * index)

    def _calc_full_circle_radius(img_size, nr_of_nodes):
        smallest_side = img_size[0] if img_size[0] < img_size[1] else img_size[1]
        circle_radius = smallest_side/(3*nr_of_nodes)
        circle_border = math.ceil(circle_radius/10)
        return circle_radius + circle_border - 1

    def _place_nodes(layout, size, graph, node_pos):
        nr_of_nodes = len(graph.get_node_ids())
        for pos_id in node_pos:
            node = graph.get_node(pos_id)
            coor = VisualizerBaseFunctionality._transform_coors(size, node_pos[pos_id])
            layout = VisualizerBaseFunctionality._add_node(layout, node, coor, nr_of_nodes, size)
        return layout

    def _transform_coors(size : List[int], coor) -> Set[int]:
        x = size[1] * (((coor[0] * 0.8) + 1) / 2) #0.8 centers it closer to the middle of the screen
        y = size[0] * (((coor[1] * 0.8) + 1) / 2)
        return (int(x), int(y))

    def _add_node(layout, node: Node, coor, nr_of_nodes: int, img_size: List[int]):
        #Nodes should take up less screen the more there is
        smallest_side = img_size[0] if img_size[0] < img_size[1] else img_size[1]
        circle_radius = smallest_side/(3*nr_of_nodes)
        circle_border = math.ceil(circle_radius/10)
        layout = VisualizerBaseFunctionality._add_circle(layout, coor, circle_radius, circle_border)
        layout = VisualizerBaseFunctionality._add_text_to_circle(layout, node, coor, circle_radius, circle_border)
        return layout

    def _add_circle(layout, coor, circle_radius, circle_border):
        layout =  cv2.circle(layout, coor, int(circle_radius), (50, 50, 50), circle_border)
        return layout

    def _add_text_to_circle(layout, node: Node, coor, circle_radius, circle_border):
        font = cv2.FONT_HERSHEY_SIMPLEX
        text = node.name + ( ":" + node.class_node.name if node.class_node.name != "" else "")
        text_thickness = int(math.ceil(circle_radius/(len(text)*10)))
        text_scale = VisualizerBaseFunctionality._find_node_text_scale(text, font, text_thickness, circle_radius)
        text_size, _ = cv2.getTextSize(text, font, text_scale, text_thickness)
        text_origin = (int(coor[0] - text_size[0] / 2), int(coor[1] + text_size[1] / 2))
        layout = cv2.putText(layout, text, text_origin, font, text_scale, (255, 0, 0), text_thickness, cv2.LINE_AA)
        return layout

    def _find_node_text_scale(text, font, thickness, node_radius):
        diameter = node_radius * 1.5
        scale_factor = 1
        text_scale = (diameter/scale_factor)
        text_size, _ = cv2.getTextSize(text, font, text_scale, thickness)
        while text_size[0] > diameter:
            scale_factor += 0.25
            text_scale = (diameter/scale_factor)
            text_size, _ = cv2.getTextSize(text, font, text_scale, thickness)
        return text_scale
    

    def visualize_graph_tree(graph: Graph) -> None:
        nodes, edges = graph









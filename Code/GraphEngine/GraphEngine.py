from typing import List, Union, Dict, Set
import networkx
import cv2
from networkx.algorithms.distance_measures import radius
import numpy
import math

from GraphEngine.KnowledgeGraph import *




class GraphEngine:
    def __init__(self, CONFIG):
        pass









class Visualize:
    #Find where to place the nodes using the networkx-lib, generate the graphic with own code using open-cv
    def KnowledgeGraph(graph: Graph, size = [500, 500]) -> None:
        node_pos = Visualize._get_node_network_structure(graph)
        layout = Visualize._generate_layout(size + [3])
        layout = Visualize._place_nodes(layout, size, graph, node_pos)
        layout = Visualize._place_edges(layout, size, graph, node_pos)
        return layout

    def _get_node_network_structure(graph: Graph) -> Dict:
        G = networkx.DiGraph()
        G.add_nodes_from(graph.get_node_ids())
        G.add_edges_from(graph.get_edge_ids())
        return networkx.drawing.spring_layout(G) 

    def _generate_layout(size: List[int]):
        layout = numpy.zeros(size,dtype=numpy.uint8)
        layout.fill(255)
        return layout

    def _place_edges(layout, size, graph, node_pos):
        nr_of_nodes = len(graph.get_node_ids())
        for edge in graph.get_edges():
            coor_from = Visualize._transform_coors(size, node_pos[edge.from_node.id])
            coor_to = Visualize._transform_coors(size, node_pos[edge.to_node.id])
            layout = Visualize._add_arrow(layout, size, graph, edge, nr_of_nodes, coor_from, coor_to)
        return layout

    def _add_arrow(layout, img_size, graph, edge, nr_of_nodes, coor_from, coor_to):
        radian_offset = Visualize._calc_radian_offset(graph, edge)
        radius = Visualize._calc_full_circle_radius(img_size, nr_of_nodes)

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
        
        return cv2.arrowedLine(layout, new_coor_from, new_coor_to, (0, 0, 0), 4)

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
            coor = Visualize._transform_coors(size, node_pos[pos_id])
            layout = Visualize._add_node(layout, node, coor, nr_of_nodes, size)
        return layout

    def _transform_coors(size : List[int], coor) -> Set[int]:
        x = size[0] * (((coor[0] * 0.8) + 1) / 2) #0.9 centers it closer to the middle of the screen
        y = size[1] * (((coor[1] * 0.8) + 1) / 2)
        return (int(x), int(y))

    def _add_node(layout, node: Node, coor, nr_of_nodes: int, img_size: List[int]):
        #Nodes should take up less screen the more there is
        smallest_side = img_size[0] if img_size[0] < img_size[1] else img_size[1]
        circle_radius = smallest_side/(3*nr_of_nodes)
        circle_border = math.ceil(circle_radius/10)
        layout = Visualize._add_circle(layout, coor, circle_radius, circle_border)
        layout = Visualize._add_text_to_circle(layout, node, coor, circle_radius, circle_border)
        return layout

    def _add_circle(layout, coor, circle_radius, circle_border):
        layout =  cv2.circle(layout, coor, int(circle_radius), (50, 50, 50), circle_border)
        return layout

    def _add_text_to_circle(layout, node: Node, coor, circle_radius, circle_border):
        text_scale = int(circle_border/4)
        text_thickness = int(math.ceil(circle_radius/10)/2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size, _ = cv2.getTextSize(node.name, font, text_scale, text_thickness)
        text_origin = (int(coor[0] - text_size[0] / 2), int(coor[1] + text_size[1] / 2))
        layout = cv2.putText(layout, node.name, text_origin, font, text_scale, (255, 0, 0), text_thickness, cv2.LINE_AA)
        return layout
    

    def visualize_graph_tree(graph: Graph) -> None:
        nodes, edges = graph
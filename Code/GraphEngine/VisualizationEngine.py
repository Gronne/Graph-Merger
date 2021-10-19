from typing import List, Union, Dict, Set
import networkx
import cv2
from networkx.algorithms.distance_measures import radius
import numpy
import math

from GraphEngine.KnowledgeGraph import *
from GraphEngine.Structures import *




class GraphEngineVisualizer:
    def __init__(self, size, size_distribution, axis):
        self._axis = axis
        self._graph_size = self.__calc_graph_size(size, size_distribution, axis)
        self._info_size = self.__calc_info_size(size, size_distribution, axis)

    def __calc_graph_size(self, size, size_distribution, axis):
        vertical = [int(size[0]*size_distribution[0]), size[1]]
        horizontal = [size[0], int(size[1]*size_distribution[0])]
        return horizontal if axis == 0 else vertical

    def __calc_info_size(self, size, size_distribution, axis):
        vertical = [int(size[0]*size_distribution[1]), size[1]]
        horizontal = [size[0], int(size[1]*size_distribution[1])]
        return horizontal if axis == 0 else vertical
        
    def visualize(self, obj):
        _graph_plot = self._create_graph_plot(obj, self._graph_size)
        _into_plot = self._create_info_plot(obj, self._info_size)
        return numpy.concatenate((_into_plot, _graph_plot), axis = 1-self._axis) 

    def _create_graph_plot(self, obj, plot_size):
        node_coor = self._get_node_coordinates(obj, plot_size)
        layout = self._generate_layout(plot_size)
        layout = self._place_nodes(layout, obj, node_coor)
        layout = self._place_edges(layout, obj, node_coor)
        return layout

    def _create_info_plot(self, obj, plot_size):
        raise Exception("Implement '_plot_info(obj, plot_size) -> plot' in class that is a child of GraphEngineVisualizer")

    def _get_node_coordinates(self, obj : object, size) -> Dict:
        nodes, edges = self._get_graph_components(obj)
        node_ids = self._to_ids(nodes)
        edge_node_ids = self._to_edge_pair_ids(edges)
        graph = networkx.DiGraph()
        graph.add_nodes_from(node_ids)
        graph.add_edges_from(edge_node_ids)
        node_positions = networkx.drawing.spring_layout(graph)
        return self._transform_positions_to_coors(size, node_positions)

    def _to_ids(self, objects):
        return [obj.id for obj in objects]

    def _to_edge_pair_ids(self, edges):
        return [edge.id_pair for edge in edges]

    def _transform_positions_to_coors(self, size : List[int], positions):
        return {pos_id: self._transform_position_to_coor(size, positions[pos_id]) for pos_id in positions}

    def _transform_position_to_coor(self, size, pos):
        x = size[1] * (((pos[0] * 0.8) + 1) / 2) #0.8 centers it closer to the middle of the screen
        y = size[0] * (((pos[1] * 0.8) + 1) / 2)
        return (int(x), int(y))     

    def _get_graph_components(self, obj):
        nodes = obj.nodes
        edges = obj.edges
        return nodes, edges

    def _generate_layout(self, size: List[int]):
        layout = numpy.zeros(size + [3],dtype=numpy.uint8)
        layout.fill(255)
        return layout

    def _place_text(self, layout, text, middle_coor, width, color = (255, 0, 0)):
        font = cv2.FONT_HERSHEY_SIMPLEX
        line_type = cv2.LINE_AA
        thickness = int(math.ceil(width/(len(text)*10)))
        scale = self.__calc_text_scale(text, font, thickness, width)
        text_size, _ = cv2.getTextSize(text, font, scale, thickness)
        start_coor = (int(middle_coor[0] - text_size[0] / 2), int(middle_coor[1] + text_size[1] / 2))
        return cv2.putText(layout, text, start_coor, font, scale, color, thickness, line_type)

    def _place_circle(self, layout, node, coor, circle_radius, circle_border):
        layout =  cv2.circle(layout, coor, int(circle_radius), (50, 50, 50), circle_border)
        return layout

    def __calc_text_scale(self, text, font, thickness, width):
        scale_factor = 1
        text_scale = (width/scale_factor)
        while cv2.getTextSize(text, font, text_scale, thickness)[0][0] > width:
            scale_factor += 0.25
            text_scale = (width/scale_factor)
        return text_scale

    def _place_nodes(self, layout, obj, node_coor):
        nodes, _ = self._get_graph_components(obj)
        node_ids = self._to_ids(nodes)
        for node_id in node_coor:
            node = obj.get_node(node_id)
            layout = self._place_node(layout, node, node_coor[node_id], len(node_ids))
        return layout

    def _place_node(self, layout, node, coor, nr_of_nodes):
        #Nodes should take up less screen the more there is
        circle_radius = self._circle_radius(layout, nr_of_nodes)
        circle_border = math.ceil(circle_radius/10)
        layout = self._place_circle(layout, node, coor, circle_radius, circle_border)
        layout = self._place_text(layout, self._node_text(node), coor, circle_radius*2*0.8)
        return layout

    def _circle_radius(self, layout, nr_of_nodes):
        smallest_side = layout.shape[0] if layout.shape[0] < layout.shape[1] else layout.shape[1]
        nr_of_nodes = nr_of_nodes if nr_of_nodes >= 5 else 5
        circle_radius = smallest_side/(2.5*nr_of_nodes)
        return circle_radius

    def _place_edges(self, layout, obj, node_coors):
        _, edges = self._get_graph_components(obj)
        for edge in edges:
            coor_from, coor_to = self._calc_edge_coor(layout, obj, node_coors, edge)
            layout = cv2.arrowedLine(layout, coor_from, coor_to, (0, 0, 0), 4)
            middle_coor = ((coor_from[0] + (coor_to[0]-coor_from[0])/2), coor_from[1] + ((coor_to[1]-coor_from[1])/2))
            max_size = abs(coor_from[1] - coor_to[1]) if abs(coor_from[0]-coor_to[0]) < abs(coor_from[1] - coor_to[1]) else abs(coor_from[0]-coor_to[0])
            width = (math.sqrt(max_size)*6) / (len(obj.get_edges_between(edge)) / (2 if len(obj.get_edges_between(edge)) > 1 else 1))
            layout = self._place_text(layout, self._edge_text(edge), middle_coor, width, (50, 50, 255))
        return layout

    def _node_text(self, node):
        raise Exception("Implement '_node_text(node) -> string'")

    def _edge_text(self, edge):
        raise Exception("Implement '_edge_text(edge) -> string'")

    def _calc_edge_coor(self, layout, obj, node_coors, edge):
        radian_offset = self._calc_radian_offset(obj, edge)
        radius = self._calc_circle_radius(layout, len(obj.nodes))
        coor_from = self._calc_edge_from_coor(node_coors, edge.id_pair, radian_offset, radius)
        coor_to = self._calc_edge_to_coor(node_coors, edge.id_pair, radian_offset, radius)
        return coor_from, coor_to

    def _calc_radian_offset(self, obj, edge):
        order_number = self._find_edge_order_number(obj, edge)
        full_offset = (6.28/18) * (len(obj.get_edges_between(edge))-1)
        return -(full_offset/2) + ((6.28/18) * order_number)
        
    def _find_edge_order_number(self, obj, edge):
        edges_between = obj.get_edges_between(edge)
        sorted_edge_ids = sorted([temp_edge.id for temp_edge in edges_between] , key=lambda k: k)
        index = sorted_edge_ids.index(edge.id)
        return index

    def _calc_circle_radius(self, layout, nr_of_nodes):
        circle_radius = self._circle_radius(layout, nr_of_nodes)
        circle_border = math.ceil(circle_radius/10)
        return circle_radius + circle_border - 1

    def _calc_edge_from_coor(self, node_coors, edge_id_pair, radian_offset, radius):
        from_coor = node_coors[edge_id_pair[0]]
        to_coor = node_coors[edge_id_pair[1]]
        height, width = self._calc_height_width_to_node_border(node_coors, edge_id_pair, radian_offset, radius, inverse_dir = 0)
        coor = self._calc_node_border_coor(from_coor, to_coor, height, width, inverse_dir = 0)
        return coor

    def _calc_edge_to_coor(self, node_coors, edge_id_pair, radian_offset, radius):
        from_center_coor = node_coors[edge_id_pair[0]]
        to_center_coor = node_coors[edge_id_pair[1]]
        height, width = self._calc_height_width_to_node_border(node_coors, edge_id_pair, radian_offset, radius, inverse_dir = 1)
        coor = self._calc_node_border_coor(from_center_coor, to_center_coor, height, width, inverse_dir = 1 )
        return coor

    def _calc_height_width_to_node_border(self, node_coors, edge_id_pair, radian_offset, radius, inverse_dir = 0):
        angle = self._calc_angle_from_node_center(node_coors, edge_id_pair, radian_offset, inverse_dir)
        height = int(radius*math.sin(angle))
        width = int(radius*math.cos(angle))
        return height, width

    def _calc_angle_from_node_center(self, node_coors, edge_id_pair, radian_offset, inverse_dir):
        from_center_coor = node_coors[edge_id_pair[0]]
        to_center_coor = node_coors[edge_id_pair[1]]
        angle = math.atan(abs(from_center_coor[1]-to_center_coor[1])/abs(from_center_coor[0]-to_center_coor[0]))
        if edge_id_pair[0] < edge_id_pair[1]:
            angle += -radian_offset if inverse_dir else radian_offset
        else:
            angle += radian_offset if inverse_dir else -radian_offset
        return angle

    def _calc_node_border_coor(self, from_center_coor, to_center_coor, height, width, inverse_dir = 0):
        if (to_center_coor[0] - from_center_coor[0]) >= 0 and (to_center_coor[1] - from_center_coor[1]) >= 0:   
            coor = (to_center_coor[0] - width, to_center_coor[1] - height) if inverse_dir else (from_center_coor[0] + width, from_center_coor[1] + height)
        elif (to_center_coor[0] - from_center_coor[0]) < 0 and (to_center_coor[1] - from_center_coor[1]) >= 0:
            coor = (to_center_coor[0] + width, to_center_coor[1] - height) if inverse_dir else (from_center_coor[0] - width, from_center_coor[1] + height)
        elif (to_center_coor[0] - from_center_coor[0]) < 0 and (to_center_coor[1] - from_center_coor[1]) < 0:
            coor = (to_center_coor[0] + width, to_center_coor[1] + height) if inverse_dir else (from_center_coor[0] - width, from_center_coor[1] - height)
        elif (to_center_coor[0] - from_center_coor[0]) >= 0 and (to_center_coor[1] - from_center_coor[1]) < 0:
            coor = (to_center_coor[0] - width, to_center_coor[1] + height) if inverse_dir else (from_center_coor[0] + width, from_center_coor[1] - height)
        return coor



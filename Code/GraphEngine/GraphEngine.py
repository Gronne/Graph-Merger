from typing import List, Union, Dict, Set
import networkx
import cv2
from networkx.algorithms.distance_measures import radius
import numpy
import math



class GraphEngine:
    def __init__(self, CONFIG):
        pass




class Node:
    _id_count = 0

    def __init__(self, name : str):
        self._id = self._generate_unique_id()
        self._name = name

    def _generate_unique_id(self) -> int:
        Node._id_count += 1
        return Node._id_count

    def __eq__(self, node: object) -> bool:
        return self.id == node.id

    @property
    def id(self) -> int:
        return self._id
        
    @property
    def name(self) -> str:
        return self._name




class Edge:
    def __init__(self, from_node : Node, to_node : Node):
        self._from_node = from_node
        self._to_node = to_node

    def __eq__(self, edge : object) -> bool:
        return self.from_node == edge.from_node and self.to_node == edge.to_node

    @property
    def from_node(self) -> Node:
        return self._from_node

    @property
    def to_node(self) -> Node:
        return self._to_node




class Graph:
    def __init__(self, nodes : List[Node] = None, edges : List[Edge] = None):
        self._nodes = {}
        if nodes != None:
            self.add_nodes(nodes)
            
        self._edges = [] if nodes == None else edges

    def add_node(self, node: Union[str, Node]) -> None:
        if isinstance(node, str):
            node = Node(node)
        if node.id not in self._nodes:
            self._nodes[node.id] = node

    def remove_node(self, node: Node) -> None:
        if node.id in self._nodes:
            del self._nodes

    def add_nodes(self, nodes) -> None:
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: Union[Edge, List[Node], Node], node_b : Node = None) -> None:
        edge = self._convert_to_edge(edge, node_b)
        if edge not in self._edges:
            self._edges += [edge]

    def _convert_to_edge(self, edge, node_b):
        if isinstance(edge, Node):
            edge = Edge(edge, node_b)
        elif isinstance(edge, List):
            edge = Edge(edge[0], edge[1])
        return edge

    def add_edges(self, edges) -> None:
        for edge in edges:
            self.add_edge(edge)

    def get_node_ids(self):
        return [id for id in self._nodes]

    def get_edge_ids(self):
        return [(edge.from_node.id, edge.to_node.id) for edge in self._edges]

    def get_node(self, id):
        return self._nodes[id]

    def get_edges(self):
        return self._edges

    def print_info(self):
        print('Nodes: ' + ''.join(f"{self._nodes[id].name}-{str(self._nodes[id].id)}, " for id in self._nodes)[:-2])
        print("Edges: " + ''.join(f"{edge.from_node.name}->{edge.to_node.name}, " for edge in self._edges)[:-2])






class VisualizeGraph:
    #Find where to place the nodes using the networkx-lib, generate the graphic with own code using open-cv
    def visualize_graph_network(graph: Graph, size = [500, 500]) -> None:
        node_pos = VisualizeGraph._get_node_network_structure(graph)
        layout = VisualizeGraph._generate_layout(size + [3])
        layout = VisualizeGraph._place_nodes(layout, size, graph, node_pos)
        layout = VisualizeGraph._place_edges(layout, size, graph, node_pos)
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
            coor_from = VisualizeGraph._transform_coors(size, node_pos[edge.from_node.id])
            coor_to = VisualizeGraph._transform_coors(size, node_pos[edge.to_node.id])
            layout = VisualizeGraph._add_arrow(layout, size, nr_of_nodes, coor_from, coor_to)
        return layout

    def _add_arrow(layout, img_size, nr_of_nodes, coor_from, coor_to):
        radius = VisualizeGraph._calc_full_circle_radius(img_size, nr_of_nodes)
        angle = math.atan(abs(coor_from[1]-coor_to[1])/abs(coor_from[0]-coor_to[0]))

        height = int(radius*math.sin(angle))
        width = int(radius*math.cos(angle))
    
        if (coor_to[0] - coor_from[0]) >= 0 and (coor_to[1] - coor_from[1]) >= 0:   
            new_coor_from = (coor_from[0] + width, coor_from[1] + height)
            new_coor_to = (coor_to[0] - width, coor_to[1] - height)
        elif (coor_to[0] - coor_from[0]) < 0 and (coor_to[1] - coor_from[1]) >= 0:
            new_coor_from = (coor_from[0] - width, coor_from[1] + height)
            new_coor_to = (coor_to[0] + width, coor_to[1] - height)
        elif (coor_to[0] - coor_from[0]) < 0 and (coor_to[1] - coor_from[1]) < 0:
            new_coor_from = (coor_from[0] - width, coor_from[1] - height)
            new_coor_to = (coor_to[0] + width, coor_to[1] + height)
        elif (coor_to[0] - coor_from[0]) >= 0 and (coor_to[1] - coor_from[1]) < 0:
            new_coor_from = (coor_from[0] + width, coor_from[1] - height)
            new_coor_to = (coor_to[0] - width, coor_to[1] + height)
        
        return cv2.arrowedLine(layout, new_coor_from, new_coor_to, (0, 0, 0), 4)

    def _calc_full_circle_radius(img_size, nr_of_nodes):
        smallest_side = img_size[0] if img_size[0] < img_size[1] else img_size[1]
        circle_radius = smallest_side/(3*nr_of_nodes)
        circle_border = math.ceil(circle_radius/10)
        return circle_radius + circle_border - 1

    def _place_nodes(layout, size, graph, node_pos):
        nr_of_nodes = len(graph.get_node_ids())
        for pos_id in node_pos:
            node = graph.get_node(pos_id)
            coor = VisualizeGraph._transform_coors(size, node_pos[pos_id])
            layout = VisualizeGraph._add_node(layout, node, coor, nr_of_nodes, size)
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
        layout = VisualizeGraph._add_circle(layout, coor, circle_radius, circle_border)
        layout = VisualizeGraph._add_text_to_circle(layout, node, coor, circle_radius, circle_border)
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
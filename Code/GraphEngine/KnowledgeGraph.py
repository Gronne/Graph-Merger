from typing import Any, List, Union, Dict, Set


class EdgeType:
    def __init__(self, name = 1):
        self._type = self._name_to_type(name)

    def _name_to_type(self, name):
        return 1

    def __eq__(self, edge_type):
        return self.value == edge_type.value

    @property
    def value(self):
        return self._type



class Property:
    def __init__(self, node = None):
        self._node = node

    def add_property(self, node) -> None:
        self._node = node

    def __eq__(self, prop):
        return self._node == prop._node

    @property
    def value(self):
        return self._node.name



class Identifier:
    _id_count = 0
    def __init__(self):
        self._id = Identifier._id_count
        Identifier._id_count += 1

    @property
    def value(self) -> int:
        return self._id



class Node:
    _id_count = 0

    def __init__(self, name : str, label : str = None):
        self._identifier = Identifier()
        self._name = name
        self._edges = {}
        self._label = str("") if label == None else label

    def __eq__(self, node: object) -> bool:
        return self.id == node.id

    def add_edge(self, edge) -> None:
        self._edges[edge.id] = edge

    def remove_edge(self, edge) -> None:
        if edge.id in self._edges:
            del self._edges[edge.id]

    def set_label(self, label : str) -> None:
        self._label = label

    @property
    def id(self) -> int:
        return self._identifier.value
        
    @property
    def name(self) -> str:
        return self._name

    @property
    def edges(self):
        return self._edges

    @property
    def nr_of_edges(self):
        return len([key for key in self._edges])

    @property
    def label(self):
        return self._label




class Edge:
    def __init__(self, from_node, to_node, type, properties = None):
        self._check_nodes(from_node, to_node)
        self._id = Identifier()
        self._from_node = from_node
        self._to_node = to_node
        self._type = type
        self._properties = self._init_properties(properties)

    def _check_nodes(self, from_node, to_node):
        if from_node == to_node:
            raise Exception("A node can not point to itself")

    def _init_properties(self, properties):
        _properties = []
        if properties != None:
            _properties += properties if isinstance(properties, List) else [properties]
        return set(_properties)

    def __eq__(self, edge : object) -> bool:
        from_check = self.from_node == edge.from_node
        to_check = self.to_node == edge.to_node
        type_check = self.type == edge.type
        property_check = self._properties == edge.properties
        return  from_check and to_check and type_check and property_check 

    @property
    def from_node(self) -> Node:
        return self._from_node

    @property
    def to_node(self) -> Node:
        return self._to_node

    @property
    def type(self):
        return self._type

    @property
    def properties(self):
        return self._properties

    @property
    def id(self):
        return self._id.value





class Graph:
    def __init__(self, nodes = None, edges = None):
        self._dict_of_nodes = self._populate_dict_of_nodes(nodes)
        self._dict_of_words = self._populate_dict_of_words(nodes)
        self._dict_of_edges = self._populate_dict_of_edges(edges)

    def _populate_dict_of_nodes(self, nodes):
        return {node.id: node for node in nodes} if nodes != None else {}

    def _populate_dict_of_words(self, nodes):
        if nodes == None: return {}
        dict_of_words = {node.name: {} for node in nodes}
        for node in nodes:
            dict_of_words[node.name][node.id] = node
        return dict_of_words

    def _populate_dict_of_edges(self, edges):
        return {edge.id: edge for edge in edges} if edges != None else {}

    def add_node(self, node: Node) -> None:
        self._dict_of_nodes[node.id] = node
        if node.name not in self._dict_of_words:
            self._dict_of_words[node.name] = {}
        self._dict_of_words[node.name][node.id] = node

    def add_nodes(self, nodes : List[Node]) -> None:
        for node in nodes:
            self.add_node(node)

    def remove_node(self, node: Node) -> None:
        if node.id in self._dict_of_nodes:
            del self._dict_of_nodes[node.id]
            del self._dict_of_words[node.name][node.id]

    def add_edge(self, edge: Edge) -> None:
        self._add_edge_to_dict_of_edges(edge)
        self._add_edge_to_nodes(edge)

    def add_edges(self, edges: List[Edge]):
        for edge in edges:
            self.add_edge(edge)

    def remove_edge(self, edge):
        self._remove_from_nodes(edge)
        self._remove_from_dict_of_edges(edge)

    def _remove_from_nodes(self, edge):
        self._dict_of_nodes[edge.from_node.id].remove_edge(edge)
        self._dict_of_nodes[edge.to_node.id].remove_edge(edge)

    def _remove_from_dict_of_edges(self, edge):
        if edge.id in self._dict_of_edges:
            del self._dict_of_edges[edge.id]

    def _add_edge_to_dict_of_edges(self, edge):
        self._dict_of_edges[edge.id] = edge

    def _add_edge_to_nodes(self, edge):
        self._dict_of_nodes[edge.from_node.id].add_edge(edge)
        self._dict_of_nodes[edge.to_node.id].add_edge(edge)

    def get_nodes(self) -> List[Node]:
        return [self._dict_of_nodes[key] for key in self._dict_of_nodes]

    def get_edges(self) -> List[Edge]:
        return [self._dict_of_edges[key] for key in self._dict_of_edges]

    def get_node(self, id) -> Node:
        return self._dict_of_nodes[id]

    def get_node_ids(self):
        return [key for key in self._dict_of_nodes]

    def get_edge_ids(self):
        return [(self._dict_of_edges[key].from_node.id, self._dict_of_edges[key].to_node.id) for key in self._dict_of_edges]

    def get_edges_between(self, node_a, node_b):
        return [node_a.edges[key] for key in node_a.edges if key in node_b.edges]

    def print_info(self):
        print('Nodes: ' + ''.join(f"{self._dict_of_nodes[id].name}-{str(self._dict_of_nodes[id].id)}, " for id in self._dict_of_nodes)[:-2])
        print("Edges: " + ''.join(f"{self._dict_of_edges[id].from_node.name}->{self._dict_of_edges[id].to_node.name}, " for id in self._dict_of_edges)[:-2])
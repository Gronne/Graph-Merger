from __future__ import annotations
from typing import Any, List, Union, Dict, Set, Tuple


class Type:
    def __init__(self, name = None, id = None):
        self._types = {1: "Type", 2: "Subclass of", 3: "subproperty of", 4: "domain", 5: "range"}
        self._type = self._get_type(name, id)

    def _get_type(self, name, id):
        if name != None and id == None:
            return self._name_to_type(name)
        elif name == None and id != None:
            return self._id_to_type(id)
        else:
            raise Exception("Type must be initialized with either a name or type of the following: " + str(self._types))
    
    def _name_to_type(self, name):
        inverted_dict = {self._types[key]: key for key in self._types}
        if name not in inverted_dict:
            raise Exception("Type must be one of the following: " + str(self._types))
        return inverted_dict[name]

    def _id_to_type(self, id):
        if id not in self._types:
            raise Exception("type must be one of the following: " + str(self._types))
        return id
            

    def __eq__(self, edge_type):
        return self.value == edge_type.value

    @property
    def value(self):
        return self._type



class NodeClass:
    def __init__(self, type: Type, node_class: None):
        self._type = type
        self._class = node_class

    @property
    def type(self): 
        return self._type

    @property
    def node_class(self):
        return self._class




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
    def __init__(self, id = None):
        if id == None:
            self._id = Identifier._id_count
            Identifier._id_count += 1
        else:
            self._id = id
            if Identifier._id_count < id:
                Identifier._id_count = id + 1

        

    @property
    def value(self) -> int:
        return self._id

    @property
    def type(self) -> int:
        return int



class Node:
    def __init__(self, name : str, id=None):
        self._identifier = Identifier(id)
        self._name = name
        self._edges = {}
        self._classes = {}    
        self._properties = {}

    def __eq__(self, node: Node) -> bool:
        if not isinstance(node, Node):
            return False
        return self.id == node.id

    def add_edge(self, edge : Edge) -> None:
        self._edges[edge.id] = edge

    def remove_edge(self, edge : Edge) -> None:
        if edge.id in self._edges:
            del self._edges[edge.id]

    def add_class(self, class_node : Node, class_edge = None) -> Edge:
        if class_node == None: return None
        if class_edge != None: 
            self._classes[class_node.id] = class_node
            edge = class_edge
        else:
            self._classes[class_node.id] = class_node
            edge = Edge(self, class_node, "isA")
        return edge

    def add_classes(self, class_nodes : List[Node]) -> List[Edge]:
        if isinstance(class_nodes, None): return None
        return [self.add_class(node) for node in class_nodes]

    def add_property(self, property_node : Node, property_type : str) -> Edge:
        if isinstance(property_type, Edge):
            self._properties[property_node.id] = property_node
            edge = property_type
        else:
            self._properties[property_node.id] = property_node
            edge = Edge(self, property_node, property_type)
        return edge

    def add_properties(self, properties : List[Tuple[Node, str]]) -> List[Edge]:
        if isinstance(properties, None): return
        return [self.add_property(property[0], property[1]) for property in properties]

    def get_edges_to(self, node : Union[Node, int]) -> Edge:
        try:
            if isinstance(node, Node):
                return [self._edges[edge_id] for edge_id in self._edges if self._edges[edge_id].to_node == node]
            else:
                return [self._edges[edge_id] for edge_id in self._edges if self._edges[edge_id].to_node.id == node]
        except:
            raise Exception(f"No edges points to node: {node.id}")
            
    @property
    def id(self) -> int:
        return self._identifier.value
        
    @property
    def name(self) -> str:
        return self._name

    @property
    def edges(self) -> List[Edge]:
        return self._edges

    @property
    def nr_of_edges(self) -> int:
        return len([key for key in self._edges])

    @property
    def classes(self) -> List[Tuple[Node, Edge]]:
        return [(self._classes[node_id], self.get_edges_to(node_id)) for node_id in self._classes]

    @property
    def properties(self) -> List[Tuple[Node, Edge]]:
        return [(self._properties[property_id], self.get_edges_to(property_id)) for property_id in self._properties]






class Edge:
    def __init__(self, from_node, to_node, label, id = None):
        self._check_nodes(from_node, to_node)
        self._id = Identifier(id)
        self._from_node = from_node
        self._to_node = to_node
        self.from_node.add_edge(self)
        self.to_node.add_edge(self)
        self._types = {}    
        self._properties = {}
        self._label = label
        #self._edge_node = Node(name)

    def _check_nodes(self, from_node, to_node):
        if from_node == to_node:
            raise Exception("A node cannot point to itself")

    def __eq__(self, edge : object) -> bool:
        if not isinstance(edge, Edge):
            return False
        from_check = self.from_node == edge.from_node
        to_check = self.to_node == edge.to_node
        type_check = self._types == edge._types
        property_check = self._properties == edge._properties
        return  from_check and to_check and type_check and property_check 

    #def add_type(self, type_node : Node) -> Edge:
    #    if isinstance(type_node, None): return None
    #    self._types[type_node.id] = type_node
    #    edge = self._edge_node.add_class(type_node)
    #    return edge

    #def add_types(self, types : List[Node]) -> List[Edge]:
    #    if isinstance(types, None): return None
    #   return [self.add_type(node) for node in types]

    #def add_property(self, property_node : Node, property_type : str) -> Edge:
    #    self._properties[property_node.id] = property_node
    #    edge = self._edge_node.add_property(property_node, property_type)
    #    return edge

    #def add_properties(self, properties : List[Tuple[Node, str]]) -> List[Edge]:
    #    if isinstance(properties, None): return None
    #   return [self.add_type(property[0], property[1]) for property in properties]


    @property
    def from_node(self) -> Node:
        return self._from_node

    @property
    def to_node(self) -> Node:
        return self._to_node

    @property
    def id(self):
        return self._id.value

    @property
    def id_pair(self):
        return (self.from_node.id, self.to_node.id)
    
    @property
    def label(self):
        return self._label

    





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

    @property
    def nodes(self) -> List[Node]:
        return self.get_nodes()

    @property
    def edges(self) -> List[Edge]:
        return self.get_edges()

    def get_node(self, id) -> Node:
        return self._dict_of_nodes[id]

    def get_node_ids(self):
        return [key for key in self._dict_of_nodes]

    def get_edge_node_ids(self):
        return [(self._dict_of_edges[key].from_node.id, self._dict_of_edges[key].to_node.id) for key in self._dict_of_edges]

    def get_edges_between(self, node_a, node_b = None):
        if isinstance(node_a, Edge):
            node_b = node_a.to_node
            node_a = node_a.from_node
        elif isinstance(node_a, Identifier.type):
            node_a = self.get_node(node_a)
            node_b = self.get_node(node_b)
        return [node_a.edges[key] for key in node_a.edges if key in node_b.edges]

    def print_info(self):
        print('Nodes: ' + ''.join(f"{self._dict_of_nodes[id].name}-{str(self._dict_of_nodes[id].id)}, " for id in self._dict_of_nodes)[:-2])
        print("Edges: " + ''.join(f"{self._dict_of_edges[id].from_node.name}->{self._dict_of_edges[id].to_node.name}, " for id in self._dict_of_edges)[:-2])
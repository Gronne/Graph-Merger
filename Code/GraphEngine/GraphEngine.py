from typing import List, Union


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
        self._nodes = [] 
        if nodes != None:
            self.add_nodes(nodes)
            
        self._edges = [] if nodes == None else edges

    def add_node(self, node: Union[str, Node]) -> None:
        if isinstance(node, str):
            node = Node(node)
        if node not in self._nodes:
            self._nodes += [node]

    def remove_node(self, node: Node) -> None:
        self._nodes.remove(node)

    def add_nodes(self, nodes) -> None:
        for node in nodes:
            self.add_node(node)

    def add_edge(self, edge: Union[Edge, List[Node], Node], node_b : Node = None) -> None:
        if isinstance(edge, Node):
            edge = Edge(edge, node_b)
        elif isinstance(edge, list):
            edge = Edge(edge[0], edge[1])
        if edge not in self._edges:
            self._edges += [edge]

    def add_edges(self, edges) -> None:
        for edge in edges:
            self.add_edge(edge)

    def print_info(self):
        print('Nodes: ' + ''.join(f"{node.name}-{str(node.id)}, " for node in self._nodes)[:-2])
        print("Edges: " + ''.join(f"{edge.from_node.name}->{edge.to_node.name}, " for edge in self._edges)[:-2])





def visualize_graph_network(graph: Graph) -> None:
    pass



def visualize_graph_tree(graph: Graph) -> None:
        nodes, edges = graph
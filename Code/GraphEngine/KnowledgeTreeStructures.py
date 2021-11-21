from __future__ import annotations
from GraphEngine.KnowledgeGraph import *
from GraphEngine.Structures import *





class KnowledgeTree:
    def __init__(self):
        self._root = Topic(); self._root.add_name("Root")
        self._topics : dict[int, Topic] = {}        #{topic_id -> {"Topic": topic, "Atoms": {}, "SubTopics": {}, "node": Node}
        self._subtopics : dict[int, Topic] = {}     #{topic_id -> {"SubTopic": Topic, "Topics": {} "Layer": int}
        self._atoms : dict[int, Topic] = {}         #{topic_id -> {"Atom" : atom, "Topics": {}}
        self._names : dict[str, list[Topic]] = {}   #{name -> [Topic]}
        self._tree_graph : Graph = Graph()

        self._topic_to_pages : dict[int, list[Page]] = {}
        self._page_to_topics : dict[int, list[Topic]] = {}

        self._website_trust : dict[int, float] = {}

    @property
    def atoms(self) -> list[Topic]:
        return [self._atoms[key]["Atom"] for key in self._atoms]

    @property
    def topics(self) -> list[Topic]:
        return [self._topics[key]["Topic"] for key in self._topics]

    @property
    def subtopics(self) -> list[Topic]:
        return [self._subtopics[key]["SubTopic"] for key in self._subtopics]

    @property
    def names(self) -> list[str]:
        return [name for name in self._names]

    @property
    def root(self) -> Topic:
        return self._root

    @property
    def nodes(self) -> Topic:
        return self.topics + self.subtopics + self.atoms + [self.root]

    @property
    def edges(self) -> Topic:   #use triple links?
        return [edge for node in self.nodes for edge in node.edges]

    @property
    def tree_graph(self) -> Graph:
        return self._tree_graph
            
    def get_node(self, topic_id : int) -> Topic:
        if topic_id in self._topics: return self._topics[topic_id]["Topic"]
        elif topic_id in self._subtopics: return self._subtopics[topic_id]["SubTopic"]
        elif topic_id in self._atoms: return self._atoms[topic_id]["Atom"]
        elif topic_id == self.root.id: return self.root

    def get_edges_between(self, topic_a : Topic, topic_b : Topic = None):
        if isinstance(topic_a, TopicEdge):
            return [topic_a]
        if topic_a in topic_b.children:
            return [TopicEdge(topic_a, topic_b)]
        elif topic_a in topic_b.parents:
            return [TopicEdge(topic_b, topic_a)]
        
    def add_topic(self, topic : Topic) -> None:
        self._topics[topic.id] = {"Topic": topic, "Atoms": {}, "SubTopics": {}, "Layer": 0}
        topic.add_parent(self._root)
        self._root.add_child(topic)
        self._tree_graph.add_node(topic.node)
        if topic.id not in self._topic_to_pages:
            self._topic_to_pages[topic.id] = []

    def add_topics(self, topics : list[Topic]) -> None:
        for topic in topics:
            self.add_topic(topic)

    def add_atom(self, atom : Topic, topics : list[Topic]) -> None:
        self._atoms[atom.id] = {"Atom" : atom, "Topics": {}, "Layer": 0}
        self._tree_graph.add_node(atom.node)
        for topic in topics:
            self._atoms[atom.id]["Topics"][topic.id] = topic
            self._topics[topic.id]["Atoms"][atom.id] = atom     
            self._topics[topic.id]["Layer"] = 1
            if atom.id not in self._topic_to_pages:
                self._topic_to_pages[atom.id] = []        
            
    def add_subtopic(self, subtopic : Topic, layer : int, topic : Topic, last_layer = False) -> None:
        self._subtopics[subtopic.id] = {"SubTopic" : subtopic, "Topic": topic, "Layer": layer}
        self._tree_graph.add_node(subtopic.node)
        self._tree_graph.add_edges([triple.predicate for triple in subtopic._triples_to_children.values()])
        self._topics[topic.id]["SubTopics"][subtopic.id] = subtopic     
        self._topics[topic.id]["Layer"] = layer + 1
        if subtopic.id not in self._topic_to_pages:
            self._topic_to_pages[subtopic.id] = []
        if last_layer == True:
            subtopic.add_parent(topic)
            edge = topic.add_child(subtopic)
            self._tree_graph.add_edge(edge)       

    def add_subtopics(self, subtopics : list[Topic], layer : int, topic : Topic, last_layer = False) -> None:
        for subtopic in subtopics:
            self.add_subtopic(subtopic, layer, topic, last_layer)

    def get_atoms(self, topic : Topic) -> list[Topic]:
        return [self._topics[topic.id]["Atoms"][atom_key] for atom_key in self._topics[topic.id]["Atoms"]]

    def add_name(self, element : Topic, name : str, parent : Topic = None, children : list[Topic] = None) -> None:
        element.add_name(name)
        if parent != None:
            parent.add_child_name(element, name)
        if children != None:
            for child in children:
                child.add_parent_name(element, name)
        if name not in self._names:
            self._names[name] = []
        self._names[name] += [element]

    def get_elements_by_name(self, name : str) -> list[Topic]:
        return self._names[name]

    def get_topics(self, element : Topic) -> list[Topic]:
        if self.is_topic(element):
            return [element]
        elif self.is_atom(element):
            return [self._atoms[element.id]["Topics"][topic_key] for topic_key in self._atoms[element.id]["Topics"]]
        elif self.is_subtopic(element):
            return [self._subtopics[element.id]["Topic"]]
    
    def same_topic(self, element_a : Topic, element_b : Topic) -> bool:
        topics_a = self.get_topics(element_a)
        topics_b = self.get_topics(element_b)
        for topic_a in topics_a:
            if topic_a in topics_b:
                return True
        return False
    
    def get_layer(self, element: Topic) -> int:
        if element.id in self._topics:
            return self._topics[element.id]["Layer"]
        elif element.id in self._subtopics:
            return self._subtopics[element.id]["Layer"]
        elif element.id in self._atoms:
            return self._atoms[element.id]["Layer"]
        elif element == self.root:
            return self.get_max_layer()
        else:
            raise Exception("Element does not exist in the Knowledge Tree")

    def is_atom(self, element : Topic) -> bool:
        return element.id in self._atoms

    def is_subtopic(self, element : Topic) -> bool:
        return element.id in self._subtopics

    def is_topic(self, element : Topic) -> bool:
        return element.id in self._topics

    def connect_topic_and_page(self, topic : Topic, page : Page) -> None:
        if page.id not in self._page_to_topics:
            self._page_to_topics[page.id] = []
        if topic != self.root:
            self._topic_to_pages[topic.id] += [page]
            self._page_to_topics[page.id] += [topic]

    def get_page_topics(self, page : Page) -> list[Topic]:
        if isinstance(page, Page):
            return self._page_to_topics[page.id]
        else:
            return self._page_to_topics[page]

    def get_topic_pages(self, topic : Topic) -> list[Page]:
        if isinstance(topic, Topic):
            return [] if topic == self.root else self._topic_to_pages[topic.id]
        else:
            return [] if topic == self.root else self._topic_to_pages[topic]

    def get_max_layer(self):
        return max([self._topics[topic_id]["Layer"] for topic_id in self._topics])+1

    def add_website_trust_factor(self, website : Website, trust_factor):
        self._website_trust[website.id] = trust_factor

    def get_website_trust_factor(self, website : Website):
        return self._website_trust[website.id]





class Topic:
    def __init__(self, id = None):
        self._id = Identifier(id)
        self._names : list[str] = []
        self._parents : Dict[int, Topic] = {} #{id -> {"Topic": Topic, "Name": Str}}
        self._children : Dict[int, Topic] = {} #{id -> {"Topic": Topic, "Name": Str}}
        self._triples : list[Triple] = []
        self._triples_to_children : dict[int, Triple] = {} #{topic_id -> triple}
        self._node = Node(name = str(self.id), id=self.id)

    def __eq__(self, topic : Topic):
        return self.id == topic.id

    @property
    def id(self) -> int:
        return self._id.value

    @property
    def names(self) -> list[str]:
        return self._names
    
    @property
    def name(self) -> str:
        return ''.join(name + "-" for name in self.names)[-1]

    @property
    def parents(self) -> list[Topic]:
        return [self._parents[parent_id]["Topic"] for parent_id in self._parents]

    @property
    def children (self) -> list[Topic]:
        return [self._children[child_id]["Topic"] for child_id in self._children]

    @property
    def all_children(self) -> list[Topic]:
        return self.children + list({grandchild.id: grandchild for child in self.children for grandchild in child.children}.values())

    @property
    def edges(self) -> list[TopicEdge]:
        return [TopicEdge(child, self) for child in self.children]

    @property
    def node(self) -> Node:
        return self._node

    @property
    def triples(self) -> list[Triple]:
        if len(self.children) == 0: return []
        return self._triples + list(self._triples_to_children.values()) + [triple for child in self.children for triple in child.triples]

    def get_child_triple(self, child) -> Triple:
        if child.id in self._children:
            return self._triples_to_children[child.id]
        else:
            raise Exception(f"child {child.id} is not a direct child of topic {self.id}")

    def add_name(self, name : str) -> None:
        self._names += [name]

    def add_parent(self, parent: Topic) -> None:
        self._parents |= {parent.id: {"Topic": parent, "Name": None}}

    def add_parents(self, parents : list[Topic]) -> None:
        for parent in parents:
            self.add_parent(parent)

    def add_child(self, child: Topic) -> None:
        self._children |= {child.id: {"Topic": child, "Name": None}}
        edge = Edge(self.node, child.node, "Is")
        self._triples_to_children[child.id] = Triple(self.node, child.node, edge)
        return edge

    def add_children(self, children : list[Topic]) -> None:
        for child in children:
            self.add_child(child)

    def add_triple(self, triple : Triple) -> None:
        self._triples += [triple]

    def add_triples(self, triples : list[Triple]) -> None:
        self._triples += triples

    def add_parent_name(self, parent, name):
        self._parents[parent.id]["Name"]

    def add_child_name(self, child, name):
        self._children[child.id]["Name"]

    def get_own_triples(self):
        return self._triples

    def in_children(self, child):
        return child.id in self._children




class TopicEdge:
    def __init__(self, child : Topic, parent : Topic):
        self._id = Identifier()
        self._child = child
        self._parent = parent

    @property
    def id(self) -> int:
        self._id.value

    @property
    def child(self) -> Topic:
        return self._child

    @property
    def parent(self) -> Topic:
        return self._parent

    @property
    def id_pair(self) -> Tuple[int, int]:
        return (self._parent.id, self._child.id)
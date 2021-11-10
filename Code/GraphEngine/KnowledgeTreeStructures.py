from __future__ import annotations
from GraphEngine.KnowledgeGraph import *






class KnowledgeTree:
    def __init__(self):
        self._root = Topic()
        self._topics : dict[int, Topic] = {}        #{id -> {"Topic": topic, "Atoms": {}, "SubTopics": {}}}
        self._subtopics : dict[int, Topic] = {}     #{id -> {"SubTopic": Topic, "Topics": {} "Layer": int}}
        self._atoms : dict[int, Topic] = {}         #{id -> {"Atom" : atom, "Topics": {}}}
        self._names : dict[str, list[Topic]] = {}   #{name -> [Topic]}

    @property
    def atoms(self) -> list[Topic]:
        return [self._atoms[key]["Atom"] for key in self._atoms]

    @property
    def topics(self) -> list[Topic]:
        return [self._topics[key]["Topic"] for key in self._topics]

    @property
    def root(self) -> Topic:
        return self._root
        
    def add_topic(self, topic : Topic) -> None:
        self._topics[topic.id] = {"Topic": topic, "Atoms": {}, "SubTopics": {}, "Layer": 0}
        topic.add_parent(self._root)
        self._root.add_child(topic)

    def add_topics(self, topics : list[Topic]) -> None:
        for topic in topics:
            self.add_topic(topic)

    def add_atom(self, atom : Topic, topics : list[Topic]) -> None:
        self._atoms[atom.id] = {"Atom" : atom, "Topics": {}, "Layer": 0}
        for topic in topics:
            self._atoms[atom.id]["Topics"][topic.id] = topic
            self._topics[topic.id]["Atoms"][atom.id] = atom     
            self._topics[topic.id]["Layer"] = 1
            
    def add_subtopic(self, subtopic : Topic, layer : int, topic : Topic, last_layer = False) -> None:
        self._subtopics[subtopic.id] = {"SubTopic" : subtopic, "Topic": topic, "Layer": layer}
        self._topics[topic.id]["SubTopics"][subtopic.id] = subtopic     
        self._topics[topic.id]["Layer"] = layer + 1
        if last_layer == True:
            subtopic.add_parent(topic)
            topic.add_child(subtopic)

    def add_subtopics(self, subtopics : list[Topic], layer : int, topic : Topic, last_layer = False) -> None:
        for subtopic in subtopics:
            self.add_subtopic(subtopic, layer, topic, last_layer)

    def get_atoms(self, topic : Topic) -> list[Topic]:
        return [self._topics[topic.id]["Atoms"][atom_key] for atom_key in self._topics[topic.id]["Atoms"]]

    def add_name(self, element, name : str) -> None:
        element.add_name(name)
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
        else:
            raise Exception("Element does not exist in the Knowledge Tree")

    def is_atom(self, element):
        return element.id in self._atoms

    def is_subtopic(self, element):
        return element.id in self._subtopics

    def is_topic(self, element):
        return element.id in self._topics




class Topic:
    def __init__(self, id = None):
        self._id = Identifier(id)
        self._names : list[str] = []
        self._parents : list[Topic] = []
        self._children : list[Topic] = []
        self._triples : list[Triple] = []

    @property
    def id(self) -> int:
        return self._id.value

    @property
    def names(self) -> list[str]:
        return self._names

    @property
    def parents(self) -> list[Topic]:
        return self._parents

    @property
    def children (self) -> list[Topic]:
        return self._children 

    @property
    def triples(self) -> list[Triple]:
        children_triples = { str(triple.object) + "-" + str(triple.subject) + "-" + str(triple.predicate.label): triple for child in self.children for triple in child.triples}
        own_triples = {str(triple.object) + "-" + str(triple.subject) + "-" + str(triple.predicate.label): triple for triple in self._triples}
        collective_triples = children_triples | own_triples
        return [collective_triples[key] for key in collective_triples]

    def add_name(self, name : str) -> None:
        self._names += [name]

    def add_parent(self, parent: Topic) -> None:
        self._parents += [parent]

    def add_parents(self, parents : list[Topic]) -> None:
        self._parents += parents

    def add_child(self, child: Topic) -> None:
        self._children += [child]

    def add_children(self, children : list[Topic]) -> None:
        self._children += children

    def add_triple(self, triple : Triple) -> None:
        self._triples += [triple]

    def add_triples(self, triples : list[Triple]) -> None:
        self._triples += triples
import numpy
import math
import random

from GraphEngine.KnowledgeTreeStructures import *
from GraphEngine.KnowledgeGraph import *
from GraphEngine.ProbabilityEngine import ProbabilityEngine



class KnowledgeGenerator:
    def generate_topics_and_atoms(CONFIG, knowledge_tree : KnowledgeTree):
        k3_total_atoms = CONFIG["Knowledge"]["Shape"]["Atoms"]
        topics_relative_info = KnowledgeGenerator._generate_topics_relative_info(CONFIG)     
        intersections = KnowledgeGenerator._determine_intersections(topics_relative_info) 
        topics = KnowledgeGenerator._initiate_topics(topics_relative_info)
        knowledge_tree.add_topics([topics[key] for key in topics])
        atoms = KnowledgeGenerator._initiate_atoms(k3_total_atoms)
        KnowledgeGenerator._add_atoms_to_topics(knowledge_tree, atoms, topics, intersections)

    def _generate_topics_relative_info(CONFIG):
        k1_width = CONFIG["Knowledge"]["Shape"]["Width"]
        k2_depth_var = CONFIG["Knowledge"]["Shape"]["Variance"]
        k4_avg_intersect = CONFIG["Knowledge"]["Intersection"]["Average"]
        k5_intersect_var = CONFIG["Knowledge"]["Intersection"]["Variance"]
        topics_info_depth = KnowledgeGenerator._generate_topics_relative_depth(k1_width, k2_depth_var)
        topics_info_inter = KnowledgeGenerator._generate_topics_relative_intersection(k1_width, k4_avg_intersect, k5_intersect_var)
        topics_info = KnowledgeGenerator._merge_topic_dicts(topics_info_depth, topics_info_inter)
        return topics_info
    
    def _generate_topics_relative_depth(nr_of_topics, depth_variance):
        relative_depths = (numpy.random.uniform(-depth_variance, depth_variance, nr_of_topics) + 1) * 0.5
        return {index: {"relative depth": relative_depth} for index, relative_depth in enumerate(relative_depths)}

    def _generate_topics_relative_intersection(nr_of_topics, average_intersection, intersection_variance):
        relative_intersections = numpy.random.uniform(-intersection_variance, intersection_variance, nr_of_topics)+average_intersection
        return {index: {"relative intersection": relative_intersection} for index, relative_intersection in enumerate(relative_intersections)} 

    def _merge_topic_dicts(dict_a, dict_b):
        return {key : dict_a[key] | dict_b[key] for key in dict_a}

    def _determine_intersections(topics_info):
        topics_inter_area = [(topic_key, topics_info[topic_key]["relative depth"] * topics_info[topic_key]["relative intersection"]) for topic_key in topics_info]
        topics_inter_area.sort(key=lambda x:x[1], reverse = True)
        intersections = {}
        if len(topics_inter_area) == 1:
            a_inter = topics_inter_area.pop()
            return {KnowledgeGenerator._id_list_to_key([topic_id]): ([topic_id], topics_info[topic_id]["relative depth"]) for topic_id in topics_info}
        if len(topics_inter_area) == 2:
            a_inter = topics_inter_area.pop()
            b_inter = topics_inter_area.pop()
            inter_map = {KnowledgeGenerator._id_list_to_key([a_inter[0], b_inter[0]]): ([a_inter[0], b_inter[0]], b_inter[1] if a_inter[1] < b_inter[1] else a_inter[1])}
            unique_inter_map = {KnowledgeGenerator._id_list_to_key([topic_id]): ([topic_id], topics_info[topic_id]["relative depth"]) for topic_id in topics_info}
            return unique_inter_map | inter_map
        while len(topics_inter_area) > 0:
            a_inter = topics_inter_area.pop()
            if len(topics_inter_area) > 0:
                b_inter = topics_inter_area.pop()
                ab_inter = ([a_inter[0], b_inter[0]], a_inter[1])
                remnant = (b_inter[0], b_inter[1] - ab_inter[1])
                intersections |= {KnowledgeGenerator._id_list_to_key(ab_inter[0]): ab_inter}
            else:
                b_inter = KnowledgeGenerator._get_biggest_intersection_wo_topic(intersections, a_inter)
                ab_inter = ([a_inter[0]] + b_inter[0], (a_inter[1] if b_inter[1] >= a_inter[1] else b_inter[1]))
                remnant = (a_inter[0], a_inter[1]-ab_inter[1])
                b_inter = (b_inter[0], b_inter[1]-ab_inter[1])
                intersections |= {KnowledgeGenerator._id_list_to_key(ab_inter[0]): ab_inter, KnowledgeGenerator._id_list_to_key(b_inter[0]): b_inter}
            if remnant[1] > 0:
                topics_inter_area += [remnant]
        KnowledgeGenerator._add_non_intersecting_areas(intersections, topics_info)
        return intersections

    def _get_biggest_intersection_wo_topic(intersections, topic):
        largest_intersection = (0, 0)
        for inter_key in intersections:
            id_list = intersections[inter_key][0]
            if topic[0] not in id_list:
                if intersections[inter_key][1] > largest_intersection[1]:
                    largest_intersection = intersections[inter_key]
        return largest_intersection

    def _id_list_to_key(list):
        return ''.join(str(element)+"-" for element in list)[:-1]

    def _key_to_id_list(key):   #I don't need this one, can use tage intersections[key][0] for the list
        return [int(id) for id in key.split('-')]

    def _add_non_intersecting_areas(intersections, topics_info):
        for topic_key in topics_info:
            inter_key = KnowledgeGenerator._id_list_to_key([topic_key])
            topic_intersections = [intersections[key][1] for key in intersections if topic_key in intersections[key][0]]
            area = topics_info[topic_key]["relative depth"] - sum(topic_intersections)
            intersections[inter_key] = ([topic_key], area)

    def _calc_total_relative_depth(intersections):
        return sum(intersections[key][1] for key in intersections)

    def _initiate_topics(topic_info):
        return {key: Topic() for key in topic_info}

    def _initiate_atoms(nr_of_atoms):
        return [Topic() for _ in range(0, nr_of_atoms)]

    def _add_atoms_to_topics(knowledge_tree : KnowledgeTree, atoms, topics, intersections):
        intersections_list = [intersections[key] for key in intersections]
        intersection = intersections_list.pop()
        total_relative_depth = KnowledgeGenerator._calc_total_relative_depth(intersections)
        nr_of_atoms = len(atoms)
        accumulated_relative_depth = intersection[1]
        threshold = nr_of_atoms * (accumulated_relative_depth / total_relative_depth)
        atom_topics = [topics[id] for id in intersection[0]]
        for atom_count, atom in enumerate(atoms):
            if atom_count > threshold:
                intersection = intersections_list.pop()
                accumulated_relative_depth += intersection[1]
                threshold = nr_of_atoms * (accumulated_relative_depth / total_relative_depth)
                atom_topics = [topics[id] for id in intersection[0]]
            knowledge_tree.add_atom(atom, atom_topics)

    def generate_atom_knowledge(CONFIG, knowledge_tree):
        a1_triple_interval = CONFIG["Knowledge"]["Atoms"]["Triples"]
        a2_node_sparsity = CONFIG["Knowledge"]["Atoms"]["Nodes"]
        a3_edge_sparsity = CONFIG["Knowledge"]["Atoms"]["Edges"]
        for atom in knowledge_tree.atoms:
            nr_of_triples = numpy.random.randint(a1_triple_interval["Minimum"], a1_triple_interval["Maximum"]+1)
            nr_of_portential_node_names = KnowledgeGenerator._generate_nr_of_potential_node_names(nr_of_triples, a2_node_sparsity)
            nr_of_portential_edge_names = KnowledgeGenerator._generate_nr_of_potential_edge_names(nr_of_triples, a3_edge_sparsity)
            triples = KnowledgeGenerator._generate_triples(nr_of_triples, nr_of_portential_node_names, nr_of_portential_edge_names)
            atom.add_triples(triples)

    def _generate_nr_of_potential_node_names(nr_of_triples, node_sparsity):
        min_nodes = math.ceil(0.5 * (1 + math.sqrt(4*nr_of_triples+1)))
        max_nodes = nr_of_triples+1
        return int(ProbabilityEngine.HouseDistribution(min_nodes, max_nodes, node_sparsity["UniformArea"], node_sparsity["Sparsity"]))

    def _generate_nr_of_potential_edge_names(nr_of_triples, edge_sparsity):
        return int(ProbabilityEngine.HouseDistribution(2, nr_of_triples, edge_sparsity["UniformArea"], edge_sparsity["Sparsity"]))

    def _generate_triples(nr_of_triples, nr_of_node_names, nr_of_edge_names):
        triple_placeholders = KnowledgeGenerator._generate_triple_placeholders(nr_of_triples, nr_of_node_names, nr_of_edge_names)
        unique_nodes = KnowledgeGenerator._unique_nodes(triple_placeholders)
        KnowledgeGenerator._name_nodes(unique_nodes)
        edge_names = KnowledgeGenerator._edge_names(triple_placeholders)
        return KnowledgeGenerator._construct_triples(triple_placeholders, unique_nodes, edge_names)

    def _generate_triple_placeholders(nr_of_triples, nr_of_node_names, nr_of_edge_names):
        triple_placeholders = []
        while len(triple_placeholders) < nr_of_triples:
            placeholder = KnowledgeGenerator._generate_triple_placeholder(nr_of_node_names, nr_of_edge_names)
            if placeholder not in triple_placeholders:
                triple_placeholders += [placeholder]
        return triple_placeholders

    def _generate_triple_placeholder(nr_of_node_names, nr_of_edge_names):
        object = numpy.random.randint(0, nr_of_node_names)
        subject = numpy.random.randint(0, nr_of_node_names)
        predicate = numpy.random.randint(0, nr_of_edge_names)
        while object == subject:
            subject = numpy.random.randint(0, nr_of_node_names)
        return (object, subject, predicate)

    def _unique_nodes(triple_placeholders):
        node_dict = {}
        for placeholder in triple_placeholders:
            node_dict[placeholder[0]] = None
            node_dict[placeholder[1]] = None
        return {key: Node() for key in node_dict}

    def _edge_names(triple_placeholders):
        edge_dict = {}
        for placeholder in triple_placeholders:
            if placeholder[2] not in edge_dict:
                edge_dict[placeholder[2]] = Identifier().value
        return edge_dict

    def _name_nodes(unique_nodes):
        for node_key in unique_nodes: 
            name = str(unique_nodes[node_key].id)
            unique_nodes[node_key].set_name(name)

    def _construct_triples(triple_placeholders, unique_nodes, edge_names):
        triples = []
        for placeholder in triple_placeholders:
            object = unique_nodes[placeholder[0]]
            subject = unique_nodes[placeholder[1]]
            predicate = Edge(object, subject, edge_names[placeholder[2]])
            triples += [Triple(object, subject, predicate)]
        return triples

    def generate_sub_layers(CONFIG, knowledge_tree : KnowledgeTree):
        s3_topic_threshold = CONFIG["Knowledge"]["SubTopics"]["TopicThreshold"]
        for topic in knowledge_tree.topics:
            layer_nr = 1
            subtopics = KnowledgeGenerator._generate_sub_layer(CONFIG, knowledge_tree.get_atoms(topic), layer_nr)
            while len(subtopics) > s3_topic_threshold:
                knowledge_tree.add_subtopics(subtopics, layer_nr, topic)  
                subtopics = KnowledgeGenerator._generate_sub_layer(CONFIG, subtopics, layer_nr) 
                layer_nr += 1
            knowledge_tree.add_subtopics(subtopics, layer_nr, topic, last_layer = True)  

    def _generate_sub_layer(CONFIG, elements, layer_nr):
        s1_element_interval = CONFIG["Knowledge"]["SubTopics"]["Elements"]
        s2_overlap = CONFIG["Knowledge"]["SubTopics"]["Overlap"]
        s4_merge_sparsity = CONFIG["Knowledge"]["SubTopics"]["Merge"]
        subtopics = KnowledgeGenerator._generate_sub_topics(elements, s1_element_interval, s2_overlap, layer_nr)
        for subtopic in subtopics:
            KnowledgeGenerator._generate_subtopic_knowledge(subtopic, s4_merge_sparsity)
        return subtopics

    def _generate_sub_topics(elements, element_interval, overlap, layer_nr):
        layer_size = int(len(elements)*(1+(overlap)*(1/layer_nr)))
        subtopics = []
        #Use all elements a single time
        elements_used = 0
        while elements_used < len(elements):
            nr_of_subtopic_elements = KnowledgeGenerator._generate_nr_of_subtopic_elements(element_interval)
            subtopic_elements = KnowledgeGenerator._extract_elements(elements, nr_of_subtopic_elements, elements_used)
            elements_used += len(subtopic_elements)
            subtopics += [KnowledgeGenerator._initiate_subtopic(subtopic_elements)]
        #Choose elements randomly
        while elements_used < layer_size:
            nr_of_subtopic_elements = KnowledgeGenerator._generate_nr_of_subtopic_elements(element_interval)
            subtopic_elements = KnowledgeGenerator._extract_random_elements(elements, nr_of_subtopic_elements)
            elements_used += len(subtopic_elements)
            subtopics += [KnowledgeGenerator._initiate_subtopic(subtopic_elements)]
        return subtopics

    def _generate_nr_of_subtopic_elements(element_interval):
        numbers = numpy.random.randint(element_interval["Minimum"], element_interval["Maximum"]+1, 2)
        return int((numbers[0]+numbers[1])/2)

    def _extract_elements(elements, nr_of_elements_to_extract, elements_used):
        if (elements_used + nr_of_elements_to_extract) < len(elements):
            return elements[elements_used:elements_used+nr_of_elements_to_extract]
        else:
            return elements[elements_used:len(elements)]            

    def _initiate_subtopic(subtopic_elements):
        topic = Topic()
        topic.add_children(subtopic_elements)
        for element in subtopic_elements:
            element.add_parent(topic)
        return topic

    def _extract_random_elements(elements, nr_of_subtopic_elements):
        random_indexes = numpy.random.randint(0, len(elements), nr_of_subtopic_elements)
        return [elements[random_index] for random_index in random_indexes]

    def _generate_subtopic_knowledge(subtopic : Topic, merge_sparsity):
        nr_of_elements = len(subtopic.children)
        nr_of_triples = int(ProbabilityEngine.HouseDistribution(nr_of_elements-1, nr_of_elements*(nr_of_elements+1), merge_sparsity["UniformArea"], merge_sparsity["Sparsity"]))
        if nr_of_triples == 0: nr_of_triples += 1
        pool_of_predicates = [triple.predicate.label for triple in subtopic.triples if triple.predicate.label != "Is"] 
        pool_of_predicates += [UniquePredicate.name() for _ in range(0, nr_of_elements)]
        #Connect direct children
        while len(subtopic.children) > 1 and KnowledgeGenerator._elements_are_connected(subtopic) == False:
            random_object = random.choice(subtopic.children)
            random_subject = random.choice(subtopic.children)
            while random_object == random_subject:
                random_subject = random.choice(subtopic.children)
            random_predicate = random.choice(pool_of_predicates)
            subtopic.add_triple(Triple(random_object.node, random_subject.node, random_predicate))
            nr_of_triples -= 1 if nr_of_triples > 0 else 0
        #Connect cross layers
        pool_of_children = subtopic.all_children
        while len(subtopic.children) > 1 and nr_of_triples > 0:
            random_object = random.choice(pool_of_children)
            random_subject = random.choice(pool_of_children)
            while random_object == random_subject:
                random_subject = random.choice(pool_of_children)
            random_predicate = random.choice(pool_of_predicates)
            subtopic.add_triple(Triple(random_object.node, random_subject.node, random_predicate))
            nr_of_triples -= 1


    def _elements_are_connected(subtopic : Topic):
        children_in_triples = {child.id: child for triple in subtopic.get_own_triples() for child in [triple.object, triple.subject]}
        children_unused = [child for child in subtopic.children if child.id not in children_in_triples]
        return len(children_unused) == 0

    def generate_names(CONFIG, knowledge_tree : KnowledgeTree):
        n1_distance = CONFIG["Knowledge"]["Names"]["Distance"]
        n2_several_names = CONFIG["Knowledge"]["Names"]["SeveralNames"]
        fifo = KnowledgeGenerator._create_fifo_queue()

        for element in knowledge_tree.root.children:
            knowledge_tree.add_name(element, UniqueName.name())
            fifo.push(element.children, element)

        while len(fifo) > 0:
            element, parent = fifo.pop()
            fifo.push(element.children, element)
            if len(element.names) == 0 or n2_several_names >= numpy.random.uniform(0.00001, 1):
                if n1_distance > 0:
                    closest_name_elements = KnowledgeGenerator._closest_elements(knowledge_tree, element)
                    for name_element in closest_name_elements:
                        name = name_element[0]
                        if KnowledgeGenerator._valid_name(element, name):
                            increased_prob = 4 if element == name_element[2] else 0
                            if (((1+n1_distance)**(name_element[1]-1+increased_prob))-1) > numpy.random.uniform(0.001, 1):
                                knowledge_tree.add_name(element, name, parent = parent, children = element.children)
                                break
                    if len(element.names) == 0:
                        knowledge_tree.add_name(element, UniqueName.name())
                else:
                    knowledge_tree.add_name(element, UniqueName.name())

    def _create_fifo_queue():
        class FIFO:
            def __init__(self):
                self._list : list[object] = []
            def push(self, elements, parent):
                if isinstance(elements, list): self._list = [(element, parent) for element in elements] + self._list
                else: self._list = [(elements, parent)] + self._list
            def pop(self):
                return self._list.pop()
            def __len__(self):
                return len(self._list)
        return FIFO()

    def _valid_name(element : Topic, name : str):
        for parent in element.parents:
            if name in parent.names:
                return False
            for e in parent.parents + parent.children:
                if name in e.names:
                    return False
        return True

    def _closest_elements(knowledge_tree : KnowledgeTree, element : Topic) -> List[Tuple[Topic, int]]:
        closest_elements = []
        name_counter = 0
        while name_counter < UniqueName.unique_counter:
            name = UniqueName.construct_name(name_counter)
            name_counter += 1
            elements = knowledge_tree.get_elements_by_name(name)
            closest_element = (None, 10000)
            for match_element in elements:
                dist = KnowledgeGenerator._dist_between_elements(knowledge_tree, element, match_element)
                if dist < closest_element[1]:
                    closest_element = (name, dist, match_element)
            closest_elements += [closest_element]
        return closest_elements

    def _dist_between_elements(knowledge_tree, element_a, element_b):   
        if knowledge_tree.same_topic(element_a, element_b): #Assumes the fastest route
            dist = abs(knowledge_tree.get_layer(element_a) - knowledge_tree.get_layer(element_b)) + 2
        else:
            dist_to_root_a = abs(knowledge_tree.get_layer(element_a) - knowledge_tree.get_layer(knowledge_tree.get_topics(element_a)[0]))+1
            dist_to_root_b = abs(knowledge_tree.get_layer(element_b) - knowledge_tree.get_layer(knowledge_tree.get_topics(element_b)[0]))+1
            dist = dist_to_root_b + dist_to_root_b - 1
        return dist



    



class UniqueName:
    unique_counter = 0
    def name(name_length = 4):
        name = UniqueName.construct_name(UniqueName.unique_counter, name_length)
        UniqueName.unique_counter += 1
        return name

    def construct_name(counter, name_length = 4):
        name = ""
        for letter_count in range(0, name_length):
            letter_division = int(counter/(25**letter_count))
            remnant = letter_division % 25
            name += chr(65 + remnant)
        return name[::-1]



class UniquePredicate:
    unique_counter = 0
    def name(name_length = 4):
        name = UniquePredicate.construct_name(UniquePredicate.unique_counter, name_length)
        UniquePredicate.unique_counter += 1
        return name

    def construct_name(counter, name_length = 4):
        name = ""
        for letter_count in range(0, name_length):
            letter_division = int(counter/(25**letter_count))
            remnant = letter_division % 25
            name += chr(65 + remnant)
        return name
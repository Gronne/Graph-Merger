import random
import numpy
import math
from GraphEngine.KnowledgeTreeStructures import *
from GraphEngine.Structures import *
from GraphEngine.Visualization import Visualize




class NetworkGenerator:
    def is_knowledge_satisfied(CONFIG, knowledge_tree : KnowledgeTree, network : Network) -> bool:
        ratio = CONFIG["Network"]["Knowledge"]["EachTopicUsed"]["Minimum"]
        tree_graph = Graph(triples = [triple for child in knowledge_tree.root.children for triple in child.triples])
        network_graph = Graph(graphs = [page.graph for website in network.websites for page in website.pages])
        return tree_graph.subset_of(network_graph)



    def generate_website(CONFIG, knowledge_tree : KnowledgeTree) -> Website:
        website_width_depth_ratio = NetworkGenerator._generate_website_width_depth_ratio(CONFIG) #Width and Depth
        website_focus = NetworkGenerator._choose_website_focus(CONFIG, knowledge_tree)
        nr_of_pages = NetworkGenerator._generate_number_of_pages(CONFIG)
        page_size_average = NetworkGenerator._generate_page_size_average(CONFIG)
        website = Website()
        pool_of_topics = {website_focus.id: website_focus}
        while len(website.pages) < nr_of_pages:
            page_size = NetworkGenerator._generate_page_size(CONFIG, page_size_average)
            starting_topic = NetworkGenerator._choose_starting_topic(pool_of_topics)
            page, topics = NetworkGenerator._generate_page(CONFIG, knowledge_tree, starting_topic, page_size, website_width_depth_ratio)
            if NetworkGenerator._is_an_unique_page(page, website.pages):
                NetworkGenerator._connect_topics_and_page(knowledge_tree, topics, page)
                website.add_page(page)
                pool_of_topics |= {topic.id: topic for topic in topics}
        NetworkGenerator._generate_internal_links(CONFIG, knowledge_tree, website)
        return website

    def _connect_topics_and_page(knowledge_tree : KnowledgeTree, topics : List[Topic], page : Page):
        for topic in topics:
            knowledge_tree.connect_topic_and_page(topic, page)

    def _is_an_unique_page(page : Page, pages : List[Page]):
        for p in pages:
            if page.graph == p.graph:
                return False
        return True

    def _choose_website_focus(CONFIG, knowledge_tree : KnowledgeTree) -> Topic:
        #Choose from the topics not yet used or just a random node?
        uniform_distribution = CONFIG["Network"]["Knowledge"]["UniformTopicDistribution"]
        nodes = knowledge_tree.nodes
        nr_of_nodes = len(nodes)
        node = knowledge_tree.root
        while node == knowledge_tree.root:
            if uniform_distribution == True:
                node = nodes[numpy.random.randint(0, nr_of_nodes)]
            else:
                node = nodes[int((numpy.random.randint(0, nr_of_nodes)+numpy.random.randint(0, nr_of_nodes))/2)]
        return node

    def _generate_website_width_depth_ratio(CONFIG):
        return numpy.random.uniform(0, 1)

    def _generate_number_of_pages(CONFIG):
        average = CONFIG["Network"]["Websites"]["Pages"]["Average"]
        minimum = CONFIG["Network"]["Websites"]["Pages"]["Minimum"]
        return NetworkGenerator._generate_chi(minimum, average)

    def _generate_page_size_average(CONFIG):
        average = CONFIG["Network"]["Knowledge"]["Elements"]["Average"]
        minimum = CONFIG["Network"]["Knowledge"]["Elements"]["Minimum"]
        maximum = CONFIG["Network"]["Knowledge"]["Elements"]["Maximum"]
        return NetworkGenerator._generate_chi(minimum, average, maximum)

    def _generate_page_size(CONFIG, average):
        minimum = CONFIG["Network"]["Knowledge"]["Elements"]["Minimum"]
        maximum = CONFIG["Network"]["Knowledge"]["Elements"]["Maximum"]
        return NetworkGenerator._generate_chi(minimum, average, maximum)

    def _generate_chi(minimum, average, maximum = None):
        chi = int(numpy.random.chisquare(average))
        chi = minimum if chi < minimum else chi
        chi = maximum if maximum != None and chi > maximum else chi
        return chi

    def _choose_starting_topic(pool_of_topics : Dict[int, Topic]) -> Topic:
        return random.choice(list(pool_of_topics.values()))
    
    def _generate_page(CONFIG, knowledge_tree : KnowledgeTree, starting_topic : Topic, page_size : int, width_depth_ratio) -> Page:
        topics = NetworkGenerator._choose_topics(knowledge_tree, starting_topic, page_size, width_depth_ratio)
        triples = NetworkGenerator._generate_triples_from_topics(CONFIG, topics)
        return Page(Graph(triples = triples)), topics

    def _choose_topics(knowledge_tree : KnowledgeTree, main_topic : Topic, page_size : int, width_depth_ratio):
        topic_pool = { main_topic.id: main_topic }
        child_parent_pool = { topic.id: topic for topic in main_topic.children + main_topic.parents}
        while len(topic_pool) < page_size or NetworkGenerator._only_topic_is_root(knowledge_tree, topic_pool):
            topic_a, topic_b = NetworkGenerator._pick_two_distinct_random_elements(child_parent_pool)
            width_depth_a = NetworkGenerator._calc_width_depth(knowledge_tree, topic_pool | {topic_a.id: topic_a})
            width_depth_b = NetworkGenerator._calc_width_depth(knowledge_tree, topic_pool | {topic_b.id: topic_b})
            if width_depth_ratio < numpy.random.uniform(0, 1):
                new_topic = topic_b if width_depth_a["Width"] < width_depth_b["Width"] else topic_a
            else:
                new_topic = topic_b if width_depth_a["Depth"] < width_depth_b["Depth"] else topic_a
            topic_pool |= {new_topic.id: new_topic}
            child_parent_pool = child_parent_pool | { topic.id: topic for topic in new_topic.children + new_topic.parents}
            child_parent_pool = {topic_id : child_parent_pool[topic_id] for topic_id in child_parent_pool if topic_id not in topic_pool}
        return [topic_pool[topic_key] for topic_key in topic_pool if topic_pool[topic_key] != knowledge_tree.root]

    def _only_topic_is_root(knowledge_tree, topic_pool):
        return len(topic_pool) == 1 and knowledge_tree.root.id in topic_pool

    def _pick_two_distinct_random_elements(child_parent_pool : Dict[int, Topic]):
        if len(child_parent_pool) == 1:
            topic = random.choice(list(child_parent_pool.values()))
            return topic, topic
        topic_a = None
        topic_b = None
        while topic_a == topic_b:
            topic_a = random.choice(list(child_parent_pool.values()))
            topic_b = random.choice(list(child_parent_pool.values()))
        return topic_a, topic_b

    def _calc_width_depth(knowledge_tree : KnowledgeTree, topics):
        if isinstance(topics, Dict):
            width = (1/NetworkGenerator._largest_layer_diff(knowledge_tree, topics)) * sum([knowledge_tree.get_layer(topics[topic_id])+1 for topic_id in topics])
            depth = NetworkGenerator._largest_layer_diff(knowledge_tree, topics) * sum([1 / (knowledge_tree.get_layer(topics[topic_id])+1) for topic_id in topics])
        else:
            width = (1/NetworkGenerator._largest_layer_diff(knowledge_tree, topics)) * sum([knowledge_tree.get_layer(topic)+1 for topic in topics])
            depth = NetworkGenerator._largest_layer_diff(knowledge_tree, topics) * sum([1 / (knowledge_tree.get_layer(topic)+1) for topic in topics])
        return {"Width": width, "Depth": depth}

    def _largest_layer_diff(knowledge_tree : KnowledgeTree, topics):
        if isinstance(topics, Dict):
            layers = [knowledge_tree.get_layer(topics[topic_id]) for topic_id in topics]
        else:
            layers = [knowledge_tree.get_layer(topic) for topic in topics]
        return (max(layers) - min(layers)) + 1




    def _generate_triples_from_topics(CONFIG, topics : List[Topic]):  #Name, triples, or part of triples - HAVENT IMPLEMENTED NAMES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        topic_subset_flag = CONFIG["Network"]["Knowledge"]["Page"]["ConnectionSubset"]
        topic_map = {topic.id for topic in topics}
        topic_triple_map : dict = {topic.id: {"from":{}, "to":{}} for topic in topics}
        for topic in topics:
            for triple in topic.triples:
                if triple.object.id in topic_map and triple.subject.id in topic_map:
                    if triple.subject.id not in topic_triple_map[triple.object.id]["to"]:
                        topic_triple_map[triple.object.id]["to"][triple.subject.id] = []
                    if triple.object.id not in topic_triple_map[triple.subject.id]["from"]:
                        topic_triple_map[triple.subject.id]["from"][triple.object.id] = []
                    topic_triple_map[triple.object.id]["to"][triple.subject.id] += [triple]
                    topic_triple_map[triple.subject.id]["from"][triple.object.id] += [triple]

        for topic_key, topic_tf_map in topic_triple_map.items():
            is_relations = [to_key for to_key, to_triples in topic_tf_map["to"].items() for triple in to_triples if triple.predicate.label == "Is"]
            random.shuffle(is_relations)
            if len(is_relations) > 1:
                #Find if the keys are connected and if so delete one of them from topic_triple_map
                del_keys = []
                for count, child_key_a in enumerate(is_relations):
                    for child_key_b in is_relations[count+1:]:
                        if child_key_b in topic_triple_map[child_key_a]["to"] or child_key_a in topic_triple_map[child_key_b]["to"]:
                            if child_key_a not in del_keys:
                                del_keys += [child_key_b]
                for key in del_keys:
                    if key in topic_triple_map[topic_key]["to"]:
                        new_triples = [triple for triple in topic_triple_map[topic_key]["to"][key] if triple.predicate.label != "Is"]
                        topic_triple_map[topic_key]["to"][key] = new_triples
                        new_triples = [triple for triple in topic_triple_map[key]["from"][topic_key] if triple.predicate.label != "Is"]
                        topic_triple_map[key]["from"][topic_key] = new_triples

        #Remove connections when multiple
        if topic_subset_flag:
            for key, topic_map in topic_triple_map.items():
                for to_key, to_list in topic_map["to"].items():
                    if len(to_list) > 1:
                        topic_triple_map[key]["to"][to_key] = [random.choice(to_list)]

        triples_to : list[Triple] = [triple for topic_map in topic_triple_map.values() for to_triples in topic_map["to"].values() for triple in to_triples]
        return triples_to


    def _generate_internal_links(CONFIG, knowledge_tree : KnowledgeTree, website : Website):
        structures = NetworkGenerator._choose_structures(CONFIG)
        front_page = NetworkGenerator._choose_front_page(knowledge_tree, website.pages)
        website.add_front_page(front_page)
        width_depth_ratio = NetworkGenerator._internal_link_width_depth_ratio(structures)
        NetworkGenerator._link_internal_pages(knowledge_tree, website, front_page, width_depth_ratio)
        NetworkGenerator._apply_post_structures(knowledge_tree, website, structures)

    def _link_internal_pages(knowledge_tree : KnowledgeTree, website : Website, front_page : Page, width_depth_ratio):
        page_knowledge_graph = NetworkGenerator._website_to_page_knowledge_graph(knowledge_tree, website)
        fifo_queue = [front_page.id]
        while len(fifo_queue) > 0:
            page_id = fifo_queue.pop()
            children_ids = [child_id for child_id in page_knowledge_graph[page_id]] 
            not_implemented_children = {}
            children_implemented = {}
            for child_id in children_ids:
                if NetworkGenerator._connect_to_internal_page(page_knowledge_graph, width_depth_ratio, children_ids, not_implemented_children, page_id, child_id):
                    children_implemented[child_id] = None
                else:
                    not_implemented_children[child_id] = None
            for child_id in children_implemented:
                website.add_internal_link(page_id, child_id)
                if child_id not in fifo_queue:
                    fifo_queue = [child_id] + fifo_queue
                for id in children_implemented:
                    if id != child_id and id in page_knowledge_graph[child_id]:
                        del page_knowledge_graph[child_id][id]
            for child_id in children_ids:
                del page_knowledge_graph[child_id][page_id]
            del page_knowledge_graph[page_id]
    
    def _apply_post_structures(knowledge_tree : KnowledgeTree, website : Website, structures):
        if structures["ToFrontPage"] == True:
            for page in website.pages:
                if page != website.front_page:
                    website.add_internal_link(page, website.front_page)
        if structures["NavigationBar"] == True:
            page_list = [website.front_page] + [link.to_page for link in website.front_page.internal_links]
            for page_a in page_list:
                for page_b in page_list:
                    if page_a != page_b and page_b not in [link.to_page for link in page_a.internal_links]:
                        website.add_internal_link(page_a, page_b)

    def _connect_to_internal_page(page_knowledge_graph, width_depth_ratio, children_ids, not_implemented_children, parent_id, child_id):
        if len(page_knowledge_graph[child_id]) <= 2:    #Rank of child is 2 or below
            return True
        elif any([child_id in page_knowledge_graph[id] for id in children_ids if id != child_id and id not in not_implemented_children]) == False:   #Not connected to children
            return True
        elif numpy.random.uniform(0, 1.0001) < (NetworkGenerator._internal_link_probability(page_knowledge_graph, parent_id, child_id) * width_depth_ratio):   #chosen as link
            return True
        return False

    def _internal_link_probability(page_knowledge_graph, parent_id, child_id):
        children_total_score = sum([NetworkGenerator._internal_link_score(page_knowledge_graph, parent_id, id) for id in page_knowledge_graph[parent_id]])
        probability = (NetworkGenerator._internal_link_score(page_knowledge_graph, parent_id, child_id))/children_total_score
        return probability

    def _internal_link_score(page_knowledge_graph, parent_id, child_id):
        return len(page_knowledge_graph[child_id]) * page_knowledge_graph[parent_id][child_id]

    def _website_to_page_knowledge_graph(knowledge_tree: KnowledgeTree, website : Website):
        page_knowledge_graph = {page.id: {} for page in website.pages} 
        topic_to_pages = {}
        for page in website.pages:
            for topic in knowledge_tree.get_page_topics(page):
                if topic.id not in topic_to_pages:
                    topic_to_pages[topic.id] = []
                topic_to_pages[topic.id] += [page.id]
        for topic_id in topic_to_pages:
            for page_id_a in topic_to_pages[topic_id]:
                for page_id_b in topic_to_pages[topic_id]:
                    if page_id_a != page_id_b:
                        if page_id_b not in page_knowledge_graph[page_id_a]:
                            page_knowledge_graph[page_id_a][page_id_b] = 0
                        page_knowledge_graph[page_id_a][page_id_b] += 1 
        return page_knowledge_graph

    def _internal_link_width_depth_ratio(structures):
        if structures["Chain"] == True:
            return 0
        elif structures["Flat"] == True:
            return 1
        else:
            return (numpy.random.uniform(0, 1.0001)+numpy.random.uniform(0, 1.0001))/2

    def _choose_structures(CONFIG):
        pre_structures = NetworkGenerator._choose_pre_structures(CONFIG)
        post_structures = NetworkGenerator._choose_post_structures(CONFIG)
        return pre_structures | post_structures

    def _choose_pre_structures(CONFIG):
        to_frontpage_flag = NetworkGenerator._structure_flag(CONFIG["Network"]["Websites"]["InternalLinks"]["Structures"]["ToFrontPage"])
        navigation_bar_flag = NetworkGenerator._structure_flag(CONFIG["Network"]["Websites"]["InternalLinks"]["Structures"]["NavigationBar"])
        return {"ToFrontPage": to_frontpage_flag, "NavigationBar": navigation_bar_flag}

    def _choose_post_structures(CONFIG):
        chain_flag = NetworkGenerator._structure_flag(CONFIG["Network"]["Websites"]["InternalLinks"]["Structures"]["Chain"])
        flat_flag = NetworkGenerator._structure_flag(CONFIG["Network"]["Websites"]["InternalLinks"]["Structures"]["Flat"])
        post_structures = {"Chain": chain_flag, "Flat": flat_flag}
        while list(post_structures.values()).count(True) >= 2:
            key = random.choice(list(post_structures.keys()))
            post_structures[key] = False
        return post_structures

    def _structure_flag(probability):
        return numpy.random.uniform(0, 1) < probability

    def _choose_front_page(knowledge_tree, pages):
        candidates = [(page, NetworkGenerator._page_dimensions(knowledge_tree, page)) for page in pages]
        candidates.sort(key=lambda x:x[1]["width"], reverse=True)  
        widest_page = candidates[0][0]
        return widest_page

    def _page_dimensions(knowledge_tree : KnowledgeTree, page):
        layers = [knowledge_tree.get_layer(topic) for topic in knowledge_tree.get_page_topics(page)]
        width = sum(layers)
        depth = sum([1/(layer+1) for layer in layers])
        return {"width": width, "depth": depth}

    def generate_external_links(CONFIG, knowledge_tree : KnowledgeTree, network: Network) -> None:
        min_knowledge_trust = CONFIG["Network"]["Websites"]["ExternalLinks"]["MinimumTrustFactor"]
        for website in network.websites:
            trust_factor = numpy.random.uniform(min_knowledge_trust, 1.0001)
            knowledge_tree.add_website_trust_factor(website, trust_factor)
            external_link_density = numpy.random.uniform(0, 1)
            new_children = {}
            topics = [topic for page in website.pages for topic in knowledge_tree.get_page_topics(page)]
            unique_topic_children = [topic_child for topic in topics for topic_child in topic.children]
            for page in website.pages:
                page_topics = {topic.id: topic for topic in knowledge_tree.get_page_topics(page)}
                page_topics_children = {_child_topic.id: None for key in page_topics for _child_topic in page_topics[key].children}
                page_unique_topic_children = [topic_child for topic_child in unique_topic_children if topic_child.id in page_topics_children]
                for topic_child in page_unique_topic_children:
                    topic_parents = [topic for topic in topic_child.parents if topic.id in page_topics]
                    for topic_parent in topic_parents:
                        if numpy.random.uniform(0, 1.0001) < NetworkGenerator._external_link_probability(knowledge_tree, website, external_link_density, topic_parent):
                            external_pages = [page for page in knowledge_tree.get_topic_pages(topic_child) if page not in website.pages and page in knowledge_tree.get_topic_pages(topic_parent) and not any([edge.to_page.website == website for edge in page.website.external_links])]
                            if len(external_pages) > 0:
                                scores = [(external_page, NetworkGenerator._external_page_score(knowledge_tree, topic_parent, external_page, trust_factor)) for external_page in external_pages]
                                scores.sort(key=lambda x:x[1], reverse=True)  
                                website.add_external_link(page, scores[0][0])
                                new_children[scores[0][0].id] = scores[0][0]
                                break
                unique_topic_children = [topic for topic in unique_topic_children if topic.id not in new_children]

    def _external_link_probability(knowledge_tree : KnowledgeTree, website : Website, external_link_density, topic_parent : Topic):
        pages = knowledge_tree.get_topic_pages(topic_parent)
        page_map = {page.id: page for page in website.pages}
        website_intersections_at_topic = len([page for page in pages if page.id in page_map])
        return external_link_density**(website_intersections_at_topic + math.log2(knowledge_tree.get_layer(topic_parent)))

    def _external_page_score(knowledge_tree : KnowledgeTree, topic_parent : Topic, external_page : Page, trust_factor):
        probability = numpy.random.uniform(0.5, 1)
        external_page_topics = knowledge_tree.get_page_topics(external_page)
        parent_layer = knowledge_tree.get_layer(topic_parent)
        score = (parent_layer+sum([parent_layer - knowledge_tree.get_layer(topic) for topic in external_page_topics]))/(len(external_page_topics))
        return trust_factor * score * probability
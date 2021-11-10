import yaml
import json
import csv
import os

from yaml import reader

from GraphEngine.KnowledgeGraph import Node, Edge, Graph



def load_config(file_addr):
    return load_yalm(file_addr)

def load_yalm(file_addr):
    with open(file_addr) as file:
        return yaml.load(file, Loader=yaml.FullLoader)

def load_json(file_addr):
    with open(file_addr + ".json") as file:
        return json.load(file)


def load_knowledge_graph(folder_addr, base_name):
    folder = folder_addr + base_name + "/"
    nodes_dict = load_json(folder + base_name + "_nodes")
    edges_dict = load_json(folder + base_name + "_edges")

    #Create Nodes
    nodes = {node_id : Node(id = int(node_id), name=nodes_dict[node_id]["name"]) for node_id in nodes_dict}
    
    #Create Edges
    edges = []
    for edge_id in edges_dict:
        node_from = nodes[str(edges_dict[edge_id]["object"])]
        node_to = nodes[str(edges_dict[edge_id]["subject"])]
        edge = Edge(node_from, node_to, label = edges_dict[edge_id]["label"], id = int(edge_id))
        edges += [edge]

    #Add classes and properties to Nodes
    for node_id in nodes_dict:
        node = nodes[node_id]
        #Add Classes
        for class_id in nodes_dict[node_id]["classes"]:
            class_node = nodes[str(class_id)]
            class_edge = node.get_edges_to(class_node)[0]
            node.add_class(class_node, class_edge)
        #Add Properties
        for property_id in nodes_dict[node_id]["properties"]:
            property_node = nodes[str(property_id)]
            property_edge = node.get_edges_to(property_node)[0]
            node.add_property(property_node, property_edge)

    return Graph([nodes[node_id] for node_id in nodes], edges)

def save_knowledge_graph(knowledge_graph, folder_addr, base_name):
    nodes = knowledge_graph.nodes
    edges = knowledge_graph.edges

    nodes_dict = {node.id: _node_to_dict(node) for node in nodes}
    edges_dict = {edge.id: _edge_to_dict(edge) for edge in edges}

    folder = folder_addr + base_name + "/"
    save_dict_as_json(nodes_dict, folder, base_name + "_nodes")
    save_dict_as_json(edges_dict, folder, base_name + "_edges")

def _node_to_dict(node):
    name = node.name
    classes = [tuple[0].id for tuple in node.classes]
    predicates = [edge_id for edge_id in node.edges]
    properties = [tuple[0].id for tuple in node.properties]
    return {"name": name, "classes": classes, "predicates": predicates, "properties": properties}

def _edge_to_dict(edge):
    object = edge.from_node.id
    subject = edge.to_node.id
    label = edge.label
    return {"object": object, "subject": subject, "label": label}



def save_website(website):
    pass

def load_website():
    pass

def save_network(network):
    pass

def load_network():
    pass

def save_bubbles(bulles):
    pass

def load_bubbles():
    pass




def save_dict_as_json(dict, folder_addr, name):
    if os.path.exists(folder_addr) == False:
        os.makedirs(folder_addr)
    with open(folder_addr + name + ".json", "w") as file:
        json.dump(dict, file)

    
import numpy
from GraphEngine.Structures import *
from GraphEngine.KnowledgeGraph import *

from random import choices, triangular
import math


class GraphEngine:        

    def generate_network(CONFIG):
        nr_of_websites = CONFIG['nr_of_websites']
        websites = [GraphEngine._generate_website(CONFIG) for _ in range(0, nr_of_websites)]
        print(len(websites))
        return Network(websites)

    def _generate_website(CONFIG):
        average = CONFIG['average_pages_per_website']
        minimum = CONFIG['min_pages_per_website']
        maximum = CONFIG['max_pages_per_website']
        nr_of_pages = GraphEngine._nr_of_pages(minimum, maximum, average)
        pages = [GraphEngine._generate_page(CONFIG) for _ in range(0, nr_of_pages)]
        return Website(pages)

    def _generate_page(CONFIG):
        return Page()

    def _generate_bubbles(CONFIG):
        return Bubble()

    def _nr_of_pages(minimum, maximum, average):
        uniform_weight = 0.5
        triangle_weight = 0.5
        procentage = 1.0 / (maximum-minimum+1)
        numbers = [number for number in range(minimum, maximum+1)]
        #Generate distribution. uniform_distribution + triangular_distribution
        distribution = [procentage * uniform_weight + GraphEngine._triangular_distribution(minimum, maximum, average, index) * triangle_weight for index, _ in enumerate((numbers))]
        return choices(numbers, distribution)[0]

    def _triangular_distribution(minimum, maximum, average, number):
        #Seen as 100% before being set back
        #-0.5 since it always will be in the middle of the average-column
        nr_of_left_columns = (average - minimum + 1) - 0.5
        nr_of_right_columns = (maximum - average + 1) - 0.5
        height = 1/(maximum-minimum+1)
        left_distribution = GraphEngine._right_angle_distribution(nr_of_left_columns, height)
        right_distribution = GraphEngine._right_angle_distribution(nr_of_right_columns, height)
        left_padded = numpy.concatenate((numpy.array(left_distribution)*2, numpy.zeros((maximum - average))))
        right_padded = numpy.concatenate((numpy.zeros((average - minimum)), numpy.array(right_distribution)*2))
        distribution = left_padded + right_padded
        return distribution[number]

    def _right_angle_distribution(columns, height):
        probabilities = []
        unit_height = height/columns
        unit_width = 1
        for column_nr in range(0, math.floor(columns)):
            triangle = unit_width*unit_height*0.5
            squares = unit_width*unit_height*column_nr
            probabilities += [triangle+squares] 
        probabilities += [unit_width*unit_height*0.25 + unit_width*unit_height*math.floor(columns)*0.5]
        return probabilities












def test_data():
    def small_graph():
        G = Graph()
        classes = [Node("Dyr"), Node("Transportmiddel"), Node("C"), Node("D")]
        nodes = [Node("Hund", classes[0]), Node("Kat", classes[0]), Node("Bil", classes[1]), Node("Fly", classes[1])]
        edges = [ Edge(nodes[0], nodes[1], "part of"), 
                Edge(nodes[1], nodes[0], "part of"),
                Edge(nodes[0], nodes[1], "Something"),
                Edge(nodes[1], nodes[0], "Something"),
                Edge(nodes[1], nodes[2], "subclass of"), 
                Edge(nodes[2], nodes[3], "Parent of"), 
                Edge(nodes[3], nodes[0], "Creative"), 
                Edge(nodes[0], nodes[2], "Something")]
        G.add_nodes(nodes)
        G.add_edges(edges)
        return G


    def large_graph():
        G = Graph()
        nodes = [Node("Hund"), Node("Kat"), Node("Bil"), Node("Fly"), Node("Abe"), Node("Banan"), Node("Circus"), Node("Dommer"), Node("Endelig")]
        edges = [ Edge(nodes[0], nodes[1], "connection"),
                Edge(nodes[1], nodes[2], "connection"),
                Edge(nodes[2], nodes[3], "connection"),
                Edge(nodes[3], nodes[4], "connection"),
                Edge(nodes[4], nodes[5], "connection"),
                Edge(nodes[5], nodes[6], "connection"),
                Edge(nodes[6], nodes[7], "connection"),
                Edge(nodes[7], nodes[8], "connection"),
                Edge(nodes[8], nodes[0], "connection"),
                Edge(nodes[0], nodes[3], "connection"),
                Edge(nodes[0], nodes[5], "connection"),
                Edge(nodes[0], nodes[7], "connection"),
                Edge(nodes[3], nodes[0], "connection"),
                Edge(nodes[3], nodes[8], "connection"),
                Edge(nodes[5], nodes[3], "connection")]
        G.add_nodes(nodes)
        G.add_edges(edges)
        return G


    pages = [Page(small_graph()), Page(large_graph()), Page(), Page(), Page(), Page(), Page(), Page(), Page()]

    websites : List[Website] = [ Website([pages[0], pages[1], pages[2]]), 
                                Website([pages[3]]), 
                                Website([pages[4], pages[5], pages[6], pages[7], pages[8]])]

    websites[0].add_internal_link(pages[0], pages[1])
    websites[0].add_internal_link(pages[1], pages[0])
    websites[0].add_internal_link(pages[0], pages[2])
    websites[0].add_internal_link(pages[2], pages[0])

    websites[2].add_internal_link(pages[4], pages[5])
    websites[2].add_internal_link(pages[5], pages[4])
    websites[2].add_internal_link(pages[4], pages[6])
    websites[2].add_internal_link(pages[6], pages[4])
    websites[2].add_internal_link(pages[4], pages[7])
    websites[2].add_internal_link(pages[7], pages[8])
    websites[2].add_internal_link(pages[8], pages[4])


    websites[0].add_external_link(pages[0], pages[3])
    websites[0].add_external_link(pages[0], pages[4])

    websites[2].add_external_link(pages[4], pages[0])
    websites[2].add_external_link(pages[6], pages[3])
    websites[2].add_external_link(pages[6], pages[0])


    bubbles = [Bubble([websites[0], websites[1]]), Bubble([websites[1], websites[2]])]

    single_page = Page()
    website_alone = Website([single_page])

    website_alone.add_external_link(single_page, pages[0])

    network = Network([website_alone], bubbles)

    return network, bubbles, websites, pages





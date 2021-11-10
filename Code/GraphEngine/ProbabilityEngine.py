import math
import random
import numpy


class ProbabilityEngine:
    def HouseDistribution(minimum, maximum, uniform_area, sparsity):
        return numpy.random.randint(minimum, maximum+1)









#def _generate_website(CONFIG):
#        average = CONFIG['average_pages_per_website']
#        minimum = CONFIG['min_pages_per_website']
#        maximum = CONFIG['max_pages_per_website']
#        nr_of_pages = GraphEngine._nr_of_pages(minimum, maximum, average)
#        pages = [GraphEngine._generate_page(CONFIG) for _ in range(0, nr_of_pages)]
#        return Website(pages)

#    def _generate_page(CONFIG):
#        return Page()

#    def _generate_bubbles(CONFIG):
#        return Bubble()

#    def _nr_of_pages(minimum, maximum, average):
#        uniform_weight = 0.5
#       triangle_weight = 0.5
#       procentage = 1.0 / (maximum-minimum+1)
#        numbers = [number for number in range(minimum, maximum+1)]
#        #Generate distribution. uniform_distribution + triangular_distribution
#        distribution = [procentage * uniform_weight + GraphEngine._triangular_distribution(minimum, maximum, average, index) * triangle_weight for index, _ in enumerate((numbers))]
#        return choices(numbers, distribution)[0]

#    def _triangular_distribution(minimum, maximum, average, number):
#        #Seen as 100% before being set back
#        #-0.5 since it always will be in the middle of the average-column
#        nr_of_left_columns = (average - minimum + 1) - 0.5
#        nr_of_right_columns = (maximum - average + 1) - 0.5
#        height = 1/(maximum-minimum+1)
#        left_distribution = GraphEngine._right_angle_distribution(nr_of_left_columns, height)
#        right_distribution = GraphEngine._right_angle_distribution(nr_of_right_columns, height)
#        left_padded = numpy.concatenate((numpy.array(left_distribution)*2, numpy.zeros((maximum - average))))
#        right_padded = numpy.concatenate((numpy.zeros((average - minimum)), numpy.array(right_distribution)*2))
#        distribution = left_padded + right_padded
#        return distribution[number]

#    def _right_angle_distribution(columns, height):
#        probabilities = []
#        unit_height = height/columns
#        unit_width = 1
#        for column_nr in range(0, math.floor(columns)):
#            triangle = unit_width*unit_height*0.5
#            squares = unit_width*unit_height*column_nr
#            probabilities += [triangle+squares] 
#        probabilities += [unit_width*unit_height*0.25 + unit_width*unit_height*math.floor(columns)*0.5]
#        return probabilities
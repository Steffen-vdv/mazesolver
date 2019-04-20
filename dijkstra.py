import time
import math
from pixelnode import PixelNode

class Dijkstra:
	def __init__(self):
		a = 1
	
	def get_path(self, destination_node):
		current_node = destination_node
		
		path = []
		while hasattr(current_node, 'parent'):
			path.insert(0, current_node)
			current_node = current_node.parent
		
		return path
	
	## Very basic implementation of Dijkstra's Algorithm. 
	## For in-depth information, see: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
	def solve(self, maze):
		nodes = maze.get_pixel_nodes()
		initial_node = maze.get_start_pixel_node()
		destination_node = maze.get_end_pixel_node()
		
		# Construct an initial state - no node has been visited and every node, apart from the initial node, gets a default infinite distance from the initial node
		for node in nodes:
			node.distance = math.inf
			node.visited = False
		
		initial_node.distance = 0
		
		current_node = initial_node
		# nodes_under_consideration represent the nodes that 
		nodes_under_consideration = []
		while current_node != destination_node:			
			neighbours = current_node.get_neighbours()
			
			for side, neighbour in neighbours.items():
				if not neighbour or neighbour.type == PixelNode.WALL:
					continue
					
				new_distance = current_node.distance + 1
				if(neighbour.distance > new_distance):
					neighbour.distance = new_distance
					neighbour.parent = current_node
				
				if neighbour not in nodes_under_consideration and neighbour.visited == False:
					nodes_under_consideration.append(neighbour)			
			
			current_node.visited = True
				
			smallest_distance_node = None
			for node in nodes_under_consideration:
				if (not smallest_distance_node or smallest_distance_node.distance > node.distance) and node.visited == False:
					smallest_distance_node = node
			
			
			current_node = smallest_distance_node
			#print (str(current_node.x) + ',' + str(current_node.y))
			#time.sleep(0.1)
		
		self.cleanup(nodes)
		
		return self.get_path(destination_node)
		
	def cleanup(self, nodes):
		for node in nodes:
			node.visited = None
			node.distance = None
import time
import math
from node import Node

class Dijkstra:
	def __init__(self):
		a = 1
	
	def get_path(self, destination_node):
		current_node = destination_node
		
		# Traverse the singly linked list end-to-start and build a start-to-end list from it
		path = []
		while hasattr(current_node, "parent"):
			path.insert(0, current_node)
			current_node = current_node.parent
		
		return path
	
	## Very basic implementation of Dijkstra's Algorithm. 
	## For in-depth information, see: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
	def solve(self, maze):
		nodes = maze.get_nodes()
		initial_node = maze.get_start_node()
		destination_node = maze.get_end_node()
		
		# Construct an initial state - no node has been visited and every node, apart from the initial node, gets a default infinite distance from the initial node
		for key, node in nodes.items():
			node.distance = math.inf	
			node.visited = False
		
		initial_node.distance = 0
		
		current_node = initial_node
		# nodes_under_consideration represent the nodes that are open to consideration 
		nodes_under_consideration = []
		
		# While we are not at the end yet AND while we still have a node to consider..
		while current_node and current_node != destination_node:			
			neighbours = current_node.get_neighbours()
			
			for side, neighbour in neighbours.items():
				# Ignore non-existant neighbours, walls and nodes that have already been visited
				if not neighbour or neighbour.type == Node.WALL or neighbour.visited == True:
					continue
				
				# Calculate the new distance and set this distance if it's lower than the last set distance for this path
				# Set this neighbour's parent so that we can backtrack the path later ascendingly
				new_distance = current_node.distance + 1
				if(neighbour.distance > new_distance):
					neighbour.distance = new_distance
					neighbour.parent = current_node
				
				# Add this not-wall not-visited neighbour to the list of nodes we wish to move to next
				if neighbour not in nodes_under_consideration:
					nodes_under_consideration.append(neighbour)			
			
			# The current node has now been fully assessed and will never be considered again
			current_node.visited = True
			if current_node in nodes_under_consideration:
				nodes_under_consideration.remove(current_node)
			
			# Obtain the node with the smallest distance from the initial one and consider this one next
			smallest_distance_node = None
			for node in nodes_under_consideration:
				if not smallest_distance_node or smallest_distance_node.distance > node.distance:
					smallest_distance_node = node
			
			current_node = smallest_distance_node
		
		# Clean up all dynamically added object attributes from the Node objects
		self.cleanup(nodes)
		
		# Sha-bang - We found a solution! Return the path for the caller to handle
		if current_node == destination_node:	
			return self.get_path(destination_node)
		
		# Aww, no solution could be found.. Either an unsolvable maze or I suck at programming
		return False
		
	def cleanup(self, nodes):
		for key, node in nodes.items():
			node.visited = None
			node.distance = None
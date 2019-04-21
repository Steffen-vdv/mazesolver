from itertools import filterfalse
import math
from pixelnode import PixelNode

class Maze:
	def __init__(self, width, height, pixel_data):
		if len(pixel_data) != width * height:
			raise ValueError("Invalid construction of Maze class: Pixel data length does not equal width * height")
		
		self.pixel_nodes = {}
		self.maze_scale = {
			"field": 		 {"width": width, "height": height},
			PixelNode.WALL:  {"x": 1, "y": 1},
			PixelNode.EMPTY: {"x": 1, "y": 1},
		}
		
		for index, pixel_greyscale in enumerate(pixel_data):
			x = index % width
			y = int(index / width)
			
			# Consider black pixels to be walls, consider white pixels to be traversable space
			if pixel_greyscale == 0:
				pixel_node = PixelNode(x, y, 1, 1, PixelNode.WALL)
			elif pixel_greyscale == 255:
				pixel_node = PixelNode(x, y, 1, 1, PixelNode.EMPTY)
			else:
				raise ValueError("Invalid pixel color %s on coordinates %s, %s" % (pixel_greyscale, x, y))
			
			# Add this pixel node to the list
			self.pixel_nodes[self.to_coord_str(x, y)] = pixel_node
		
		# Now that we've processed all nodes, set neighbours for each of these nodes
		self.attach_neighbours()
		
		# Calculate the scaling of the maze nodes (walls, traversable field) by assessing the ENTIRE maze. @TODO Could probably improve efficiency here
		self.set_maze_scale()
		
		# Convert the maze model by replacing pixel-based data with node-based data. 
		# We're not interested in having 100 PixelNode objects for one node that happens to be 100x100, convert those into one object that we work with.
		start_end_data = self.convert_to_scale()
		
		# Re-attach neighbours after conversion, since we're now working with entirely new objects.
		# @TODO Improve efficiency, possibly by skipping the attaching of neighbors 3 statements above. Would require the set_maze_scale algorithm to traverse differently
		self.attach_neighbours()
		
		# Set the start- and end position of the maze, we only support exactly one start and exactly one stop location and passively ignore anything else.
		# Furthermore: Start and stop positions have to be on the top and bottom, respectively.
		self.set_maze_start_end(start_end_data)
		
		print (self.end_pixel_node)
		
		if not hasattr(self, "start_pixel_node"):
			raise ValueError("No maze entrypoint could be identified - they're all walls :o")
	
		if not hasattr(self, "end_pixel_node"):
			raise ValueError("No maze exit point could be identified - they're all walls :o")
	
	def calculate_nodetype_scale(self, from_direction, to_direction, node_type):
		current_successive_number = 0
		lowest_successive_number = math.inf
		current_node = self.pixel_nodes[self.to_coord_str(0, 0)]
		traversal_direction = to_direction
		
		# If we're traversing columns - hop right when we reach the end of a column. If we're traversing rows, hop to the bottom when we reach the last node in the row.
		skip_direction = "right" if from_direction == "bottom" or to_direction == "bottom" else "bottom"
			
		while current_node:
			# Up the successive number if we notice a node of the given type
			if current_node.type == node_type:
				current_successive_number += 1
			
			new_node = current_node.get_neighbour(traversal_direction)
			
			# Sequence is done when we reach the end of the row/column OR if we reach something 
			if not new_node or current_node.type != node_type:
				if current_successive_number < lowest_successive_number and current_successive_number != 0:
					lowest_successive_number = current_successive_number
				current_successive_number = 0
			
			# Reached end of row/column, move on to the next one
			if not new_node:
				new_node = current_node.get_neighbour(skip_direction)
				traversal_direction = from_direction if traversal_direction == to_direction else to_direction
			
			current_node = new_node
		
		return lowest_successive_number
	
	
	def set_maze_scale(self):
		self.maze_scale[PixelNode.WALL]["y"]  = self.calculate_nodetype_scale("top", "bottom", PixelNode.WALL)
		self.maze_scale[PixelNode.EMPTY]["y"] = self.calculate_nodetype_scale("top", "bottom", PixelNode.EMPTY)
		self.maze_scale[PixelNode.WALL]["x"]  = self.calculate_nodetype_scale("left", "right", PixelNode.WALL)
		self.maze_scale[PixelNode.EMPTY]["x"] = self.calculate_nodetype_scale("left", "right", PixelNode.EMPTY)
		
	def convert_to_scale(self):
		# Define some constant values as it relates to the processed maze details, added primarily for readability
		field_width = self.maze_scale["field"]["width"]
		field_height = self.maze_scale["field"]["height"]
		
		wall_width = self.maze_scale[PixelNode.WALL]["x"]
		wall_height = self.maze_scale[PixelNode.WALL]["y"]
		
		empty_width = self.maze_scale[PixelNode.EMPTY]["x"]
		empty_height = self.maze_scale[PixelNode.EMPTY]["y"]
		
		# Set the initial state that we'll be working with
		new_pixel_nodes = {}
		current_pixel_node_key = self.to_coord_str(0, 0)
		initial_pixel_node = self.pixel_nodes[current_pixel_node_key]
		node_width = self.maze_scale[initial_pixel_node.type]["x"]
		node_height = self.maze_scale[initial_pixel_node.type]["y"]
		
		# The x and y coordinates of physical-pixel-node as it was found in the given image
		pixel_x = initial_pixel_node.x
		pixel_y = initial_pixel_node.y
		
		# The x and y coordinates that the model will represent, potentially vastly different from the pixel_x/y
		new_x = 0
		new_y = 0
		
		while current_pixel_node_key in self.pixel_nodes:
			pixel_node = self.pixel_nodes[current_pixel_node_key]
			
			# Create a new node for the new_x and new_y. new_x and new_y are not physical-pixel-based but node-based instead.
			# Retain the original pixel values to be able to convert back into an image later.
			new_node_key = self.to_coord_str(new_x, new_y)
			
			new_pixel_node = PixelNode(new_x, new_y, node_width, node_height, pixel_node.type)
			new_pixel_node.set_original_pixel_values(pixel_x, pixel_y)
			
			new_pixel_nodes[new_node_key] = new_pixel_node
			
			# Skip all other pixels that are within this node's width, we only want 1 node object regardless of the # of pixels it is represented by
			pixel_x += node_width
			
			# Remember: new_x does not represent actual pixels, but is used solely for efficiency purposes
			new_x += 1
			if pixel_x >= field_width:
				# We have reached the end of this row, reset the x and increment the y.
				pixel_x = 0
				pixel_y += node_height
				new_y += 1
				new_x = 0
				
				## Alternate the node height between wall- and empty-space height. The reason for this is based on the way mazes are spaced.
				## Mazes with spacing typically have a few pixels of "dead room" between two empty spaces, which is where a wall would be injectable.
				## Since we want to observe the presence/absense of a wall, we need to check the this dead room where a wall could be.
				## Next to that, we also want to observe empty nodes for supporting blocked off sections with all-wall and no empty spaces.
				## Due to this, we iterate over every potential-wall spot and every potential-empty-room spot to ensure we're creating the model appropriately.
				node_height = wall_height if node_height == empty_height else empty_height
			else:
				# We're not at the end of the row yet, keep going. See comment-block above for information about the statement below.
				node_width = wall_width if node_width == empty_width else empty_width
				
			# Move on to the next pixel-of-interest.
			current_pixel_node_key = self.to_coord_str(pixel_x, pixel_y)
		
		self.pixel_nodes = new_pixel_nodes
		
		return {
			"initial": self.pixel_nodes["0,0"], 
			"final":  self.pixel_nodes[new_node_key]
		} 
			
	def attach_neighbours(self):
		for key, pixel_node in self.pixel_nodes.items():	
			# Attach previously processed neigbours (top and left) to this new pixel_node as neighbour
			# Attach this new pixel_node to previously processed neighbours (right and bottom) as neighbour
			if pixel_node.x > 0:
				left_neighbour = self.pixel_nodes[self.to_coord_str(pixel_node.x - 1, pixel_node.y)]
				
				pixel_node.set_neighbour("left", left_neighbour)
				left_neighbour.set_neighbour("right", pixel_node)
			if pixel_node.y > 0:
				top_neighbour = self.pixel_nodes[self.to_coord_str(pixel_node.x, pixel_node.y - 1)]
				
				pixel_node.set_neighbour("top", top_neighbour)
				top_neighbour.set_neighbour("bottom", pixel_node)
		
	def set_maze_start_end(self, start_end_data):
		# Set this maze's starting point to the first empty node (left-to-right) we can find on the first row
		current_node = start_end_data["initial"]
		while current_node:
			if current_node.type == PixelNode.EMPTY:
				self.start_pixel_node = current_node
				break
				
			current_node = current_node.get_neighbour("right")
		
		# Set this maze's end point to the first empty node (right-to-left) we can find on the last row
		current_node = start_end_data["final"]
		while current_node:
			if current_node.type == PixelNode.EMPTY:
				self.end_pixel_node = current_node
				break
				
			current_node = current_node.get_neighbour("left")
	
	def to_coord_str(self, x, y):
		return str(x) + "," + str(y)
	
	def get_pixel_nodes(self):
		return self.pixel_nodes

	def get_start_pixel_node(self):
		return self.start_pixel_node
		
	def get_end_pixel_node(self):
		return self.end_pixel_node
	
	## HACKY DEBUGGING METHODS HENCEFORTH ##
	
	def debug_neighbour_sanity(self):
		output_list = [[]]
		node = self.pixel_nodes["0,0"]
		node_traversal_direction = "right"
		
		while True:
			if hasattr(node, "visited") and node.visited == True:
				output = "-"
			elif node.type == PixelNode.WALL:
				output = 'X'
			else:
				output = ' '
			
			if node_traversal_direction == "right":
				output_list[-1].append(output)
			else:
				output_list[-1].insert(0, output)
			
			new_node = node.get_neighbour(node_traversal_direction)
			if not new_node:
				new_node = node.get_neighbour("bottom")
				if not new_node:
					break
				else:
					node_traversal_direction = "left" if node_traversal_direction == "right" else "right"
					output_list.append([])
				
			node = new_node
		
		full_output = ''
		for line_char_list in output_list:
			full_output += ''.join(line_char_list) + "\n"
			
		print (full_output)
	
	def debug_pixel_nodes_chronology_sanity(self):
		output = ''
		last_x = 0
		for key, node in self.pixel_nodes.items():
			if node.x != last_x:
				output += "\n"
		
			if hasattr(node, "visited") and node.visited == True:
				output += "-"
			elif node.type == PixelNode.WALL:
				output += "X"
			else:
				output += " "
				
			last_x = node.x
		
		print (output)
from itertools import filterfalse
import math
import copy
from pixelnode import PixelNode

class Maze:
	GREYSCALE_NODETYPES = {
		0: PixelNode.WALL,
		255: PixelNode.EMPTY
	};

	def __init__(self, width, height, pixel_data):
		if len(pixel_data) != width * height:
			raise ValueError("Invalid construction of Maze class: Pixel data length does not equal width * height")
		
		self.pixel_nodes = {}
		self.maze_scale = {	type: {"x": math.inf, "y": math.inf} for type in PixelNode.get_all_node_types()	}
		self.maze_scale["field"] = {"width": width, "height": height}
		
		# Calculate the scaling of the maze nodes (walls, traversable field) by assessing the ENTIRE maze. @TODO Could probably improve efficiency here
		self.set_maze_scale(pixel_data)
		
		start_end_data = self.create_nodes(pixel_data)
		
		# Now that we've processed all nodes, set neighbours for each of these nodes
		self.attach_neighbours()
		
		# Set the start- and end position of the maze, we only support exactly one start and exactly one stop location and passively ignore anything else.
		# Furthermore: Start and stop positions have to be on the top and bottom, respectively.
		self.set_maze_start_end(start_end_data)
		
		if not hasattr(self, "start_pixel_node"):
			raise ValueError("No maze entrypoint could be identified - they're all walls :o")
		if not hasattr(self, "end_pixel_node"):
			raise ValueError("No maze exit point could be identified - they're all walls :o") 	
	
	@staticmethod
	def get_node_type_by_pixel_greyscale(greyscale):
		if greyscale in Maze.GREYSCALE_NODETYPES:
			return Maze.GREYSCALE_NODETYPES[greyscale]
		
		raise ValueError("Unidentified greyscale color " + str(greyscale) + ", supported colors are: " + Maze.GREYSCALE_NODETYPES.keys())
	
	def transpose_pixel_data(self, pixel_data, transposition_length):
		# Transpose the pixel data to enable iterating column by column
		transposed_pixel_data = []
		for index, pixel_greyscale in enumerate(pixel_data):
			axis_coordinate = int(index / transposition_length)
			
			# When we've gone through the first row/column, we have everything, because the loop below grabs all pixels in the other axis
			if (axis_coordinate != 0):
				break
			
			# Obtain and store all pixels in the same column as this one
			transposed_neighbour_index = index
			while (transposed_neighbour_index < len(pixel_data)):
				transposed_pixel_data.append(pixel_data[transposed_neighbour_index])
				transposed_neighbour_index += transposition_length
		
		return transposed_pixel_data
	
	def calculate_maze_scale(self, axis, pixel_data, transposition_length):
		# Assume we always start out with a wall at the left top
		prev_node_type = PixelNode.WALL
		prev_counter_axis_coord = 0
		
		scale_by_type = { type:1 for type in PixelNode.get_all_node_types() }
		
		# We only support 2-D mazes, so this is easy!
		counter_axis = "y" if axis == "x" else "x"
		
		for index, pixel_greyscale in enumerate(pixel_data):
			# Coordinates for each axis, sane even after transposition
			axes_coords = {
				axis: index % transposition_length,
				counter_axis: int(index / transposition_length)
			}			
			
			type = self.get_node_type_by_pixel_greyscale(pixel_greyscale)
			
			if prev_node_type == type and prev_counter_axis_coord == axes_coords[counter_axis]:
				# Still on the same main axis as before + same node type as before: up the sequence
				scale_by_type[type] += 1
			else:
				# We found a new type, or we're at the end of the axis - sequence is complete, store it if it's the lowest sequence yet
				if self.maze_scale[prev_node_type][axis] > scale_by_type[prev_node_type]:
					self.maze_scale[prev_node_type][axis] = scale_by_type[prev_node_type]
				
				# Reset to 1 because we're starting a new sequence (which this current node is a part of)
				scale_by_type[prev_node_type] = 1
						
			prev_node_type = type
			prev_counter_axis_coord = axes_coords[counter_axis]
	
	def set_maze_scale(self, pixel_data):
		width = self.maze_scale["field"]["width"]
		
		self.calculate_maze_scale("x", pixel_data, width)
		y_transposed_pixel_data = self.transpose_pixel_data(pixel_data, width)
		self.calculate_maze_scale("y", y_transposed_pixel_data, width)
		
	def create_nodes(self, pixel_data):
		# Define some constant values as it relates to the processed maze details, added primarily for readability
		field_width = self.maze_scale["field"]["width"]
		field_height = self.maze_scale["field"]["height"]
		
		wall_width = self.maze_scale[PixelNode.WALL]["x"]
		wall_height = self.maze_scale[PixelNode.WALL]["y"]
		
		empty_width = self.maze_scale[PixelNode.EMPTY]["x"]
		empty_height = self.maze_scale[PixelNode.EMPTY]["y"]
		
		# Assumption that 0,0 will always be a wall!
		node_width = self.maze_scale[PixelNode.WALL]["x"]
		node_height = self.maze_scale[PixelNode.WALL]["y"]
		
		# The X/Y coordinates for the node model, which will differ significantly (but relate to) the pixel coordinates
		model_x = 0
		model_y = 0
		
		prev_y = 0
		
		pixel_index = 0
		
		while pixel_index < len(pixel_data):
			pixel_greyscale = pixel_data[pixel_index]
			
			x = pixel_index % field_width
			y = int(pixel_index / field_width)
			
			new_node_key = self.to_coord_str(model_x, model_y)
			# Create a new node for the model_x and model_y. model_x and model_y are not physical-pixel-based but node-based instead.
			# Retain the original pixel values to be able to convert back into an image later.
			type = self.get_node_type_by_pixel_greyscale(pixel_greyscale)
			
			pixel_node = PixelNode(model_x, model_y, node_width, node_height, type)
			pixel_node.set_original_pixel_values(x, y)
			
			self.pixel_nodes[new_node_key] = pixel_node
			
			# Skip all other pixels that are within this node's width, we only want 1 node object regardless of the # of pixels it is represented by
			pixel_index += node_width
			
			model_x += 1
			new_y = int(pixel_index / field_width)
			
			if new_y != prev_y:
				# We're on a new column, skip all pixels that are part of the height of a recently processed node
				pixel_index += (node_height - 1) * field_width
				new_y = int(pixel_index / field_width)
				
				model_y += 1
				model_x = 0
				
				## Alternate the node height between wall- and empty-space height. The reason for this is based on the way mazes are spaced.
				## Mazes with spacing typically have a few pixels of "dead room" between two empty spaces, which is where a wall would be injectable.
				## Since we want to observe the presence/absense of a wall, we need to check the this dead room where a wall could be.
				## Next to that, we also want to observe empty nodes for supporting blocked off sections with all-wall and no empty spaces.
				## Due to this, we iterate over every potential-wall spot and every potential-empty-room spot to ensure we're creating the model appropriately.
				node_height = wall_height if node_height == empty_height else empty_height
			else:
				# We're not at the end of the row yet, keep going. See comment-block above for information about the statement below.
				node_width = wall_width if node_width == empty_width else empty_width
		
			prev_y = new_y
		
		return {
			"initial": self.pixel_nodes["0,0"], 
			"final": self.pixel_nodes[new_node_key]
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
		last_y = 0
		for key, node in self.pixel_nodes.items():
			if node.y != last_y:
				output += "\n"
		
			if hasattr(node, "visited") and node.visited == True:
				output += "-"
			elif node.type == PixelNode.WALL:
				output += "X"
			else:
				output += " "
				
			last_y = node.y
		
		print (output)
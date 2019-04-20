from pixelnode import PixelNode

class Maze:
	def __init__(self, width, height, pixel_data):
		if len(pixel_data) != width * height:
			raise ValueError("Invalid construction of Maze class: Pixel data length does not equal width * height")
		
		self.pixel_nodes = []
		
		for index, pixel_greyscale in enumerate(pixel_data):
			x = int(index / width)
			y = index % width
			
			if pixel_greyscale == 0:
				pixel_node = PixelNode(x, y, PixelNode.WALL)
			elif pixel_greyscale == 255:
				pixel_node = PixelNode(x, y, PixelNode.EMPTY)
			else:
				raise ValueError("Invalid pixel color %s on coordinates %s, %s" % (pixel_greyscale, x, y))
			
			# Attach previously processed neigbours (top and left) to this new pixel_node as neighbour
			# Attach this new pixel_node to previously processed neighbours (right and bottom) as neighbour
			if y > 0:
				left_neighbour = self.pixel_nodes[index - 1]
				
				pixel_node.set_neighbour("left", left_neighbour)
				left_neighbour.set_neighbour("right", pixel_node)
			if x > 0:
				top_neighbour = self.pixel_nodes[index - width]
				
				pixel_node.set_neighbour("top", top_neighbour)
				top_neighbour.set_neighbour("bottom", pixel_node)
			
			# Add this pixel node to the list/
			self.pixel_nodes.append(pixel_node)
			
			# Set this maze's starting point to the first empty pixel we can find on the first row
			if pixel_node.type == PixelNode.EMPTY and x == 0 and not hasattr(self, 'start_pixel_node'):
				self.start_pixel_node = pixel_node
			
			# Set this maze's ending point to the first empty pixel we can find on the last row  (-1 to correct zero-based numbering)
			if pixel_node.type == PixelNode.EMPTY and x == (height - 1):
				self.end_pixel_node = pixel_node
				
		if not hasattr(self, 'start_pixel_node'):
			raise ValueError("No maze entrypoint could be identified - they're all walls :o")
	
		if not hasattr(self, 'end_pixel_node'):
			raise ValueError("No maze exit point could be identified - they're all walls :o")
	
	def get_pixel_nodes(self):
		return self.pixel_nodes

	def get_start_pixel_node(self):
		return self.start_pixel_node
		
	def get_end_pixel_node(self):
		return self.end_pixel_node
	
	## DEBUGGING METHODS HENCEFORTH ##
	
	def debug_neighbour_sanity(self):
		output_list = [[]]
		node = self.pixel_nodes[0]
		node_traversal_direction = "right"
		while True:
			if node.type == PixelNode.WALL:
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
			full_output += ''.join(line_char_list) + '\n'
			
		print (full_output)
	
	def debug_pixel_nodes_chronology_sanity(self):
		output = ''
		last_x = 0
		for node in self.pixel_nodes:
			if node.x != last_x:
				output += '\n'
		
			if hasattr(node, 'visited') and node.visited == True:
				output += '-'
			elif node.type == PixelNode.WALL:
				output += 'X'
			else:
				output += ' '
				
			last_x = node.x
		
		print (output)
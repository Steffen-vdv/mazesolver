class PixelNode:
	WALL = "wall"
	EMPTY = "empty"
	
	def __init__(self, x, y, width, height, type):
		self.validate(x, y, type)
		
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.type = type
		self.neighbours = { "top": None, "right": None, "bottom": None, "left": None }
	
	def validate(self, x, y, type):
		if x < 0 or y < 0:
			raise ValueError("Coordinates out of bounds: %s,%s" % (x, y))
		
		if type not in [self.WALL, self.EMPTY]:
			raise ValueError("Unknown type %s" % type)
	
	def set_neighbour(self, side, neighbour_node = None):
		self.neighbours[side] = neighbour_node
	
	def set_original_pixel_values(self, original_x, original_y):
		self.original_x = original_x
		self.original_y = original_y
	
	def __eq__(self, other):
		if not isinstance(other, PixelNode):
			return NotImplementedError
		
		return self.x == other.x and self.y == other.y
		
	def __str__(self):
		return "Model: " + str(self.x) + "," + str(self.y) + " -- Original: " + str(self.original_x) + "," + str(self.original_y) + " -- Type: " + self.type
	
	## DEBUGGING METHODS HENCEFORTH ##
	
	def get_neighbour(self, type):
		return self.neighbours[type]
	
	def get_neighbours(self):
		return self.neighbours
		
	def get_coordinates(self):
		return str(self.x) + ',' + str(self.y)
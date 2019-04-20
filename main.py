import argparse

from maze import Maze
from PIL import Image
from utility import GenericUtility
from factory import SolverFactory

def get_arguments():
	parser = argparse.ArgumentParser()
	
	parser.add_argument("-m", "--method")
	parser.add_argument("-i", "--input", type=GenericUtility.file_exists)
	parser.add_argument("-o", "--output", type=GenericUtility.file_not_exists)
			
	return parser.parse_args()

		
def solve_maze(input_image, output_image, solve_method):
	image = Image.open(input_image)
	
	image_width = image.size[0]
	image_height = image.size[1]
	
	# Obtain a list of image pixel data where we only fetch the R (in RGB) values (signified by band index 0)
	# We're not interested in any particular band as we're working solely with black and white
	# This means we only expect 0 or 255 as values, anything else is invalid as per business rules
	maze_pixel_data = list(image.getdata(0))
	
	maze = Maze(image_width, image_height, maze_pixel_data)
	
	solveFactory = SolverFactory()
	solver = solveFactory.create(solve_method)
	
	path = solver.solve(maze)
	
	for node in path:
		print (str(node.x) + ',' + str(node.y))
	
def main():
	try:
		args = get_arguments()
		solve_maze(args.input, args.output, args.method)
	except Exception as e: 
		print (e.strerror)		
	
# Run the main method if ran from the command line
if __name__ == "__main__":
	main()
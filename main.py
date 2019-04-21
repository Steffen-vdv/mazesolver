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

		
def solve_maze(input_image_path, solve_method):
	image = Image.open(input_image_path)
	
	image_width = image.size[0]
	image_height = image.size[1]
	
	# Obtain a list of image pixel data where we only fetch the R (in RGB) values (signified by band index 0)
	# We're not interested in any particular band as we're working solely with black and white
	# This means we only expect 0 or 255 as values, anything else is invalid as per business rules
	maze_pixel_data = list(image.getdata(0))
	
	# Construct the maze, which will create a model for the playingfield, including all squares and their neighbours 
	maze = Maze(image_width, image_height, maze_pixel_data)
	
	# Construct the solver based on the input method
	solveFactory = SolverFactory()
	solver = solveFactory.create(solve_method)
	
	# Solve the maze and return the result
	return solver.solve(maze)
	
def handle_maze_solution(path, original_image_path, output_image_path):
	image = Image.open(original_image_path)
	
	# Maze could not be solved, exit immediately
	if path == False:
		print ("Maze could not be solved :-(")
		return False
		
	# Create a new image based on the input image and load the image pixel data
	image = image.convert("RGB")
	image_pixel_data = image.load()
	
	# Draw the path in the image as red pixels
	for node in path:
		image_pixel_data[node.x, node.y] = (255, 0, 0)
		
	# Save the image to the path given path
	image.save(output_image_path, "PNG")
	
def main():
	try:
		args = get_arguments()
		path = solve_maze(args.input, args.method)
		handle_maze_solution(path, args.input, args.output)
	except Exception as e: 
		print (e.strerror)		
	
# Run the main method if ran from the command line
if __name__ == "__main__":
	main()
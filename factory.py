from dijkstra import Dijkstra;
from astar import AStar;

class SolverFactory:
	def create(self, method_name):
		if method_name == "dijkstra":
			return Dijkstra()
		elif method_name == "astar":
			return AStar()
		else:
			return AStar()
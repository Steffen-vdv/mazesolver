from dijkstra import Dijkstra;

class SolverFactory:
	def create(self, method_name):
		if method_name == "dijkstra":
			return Dijkstra()
		else:
			return Dijkstra()
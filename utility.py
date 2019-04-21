import argparse
from pathlib import Path

class GenericUtility:
	def file_exists(file_path):
		if (Path(file_path)).is_file():
			return file_path
			
		raise argparse.ArgumentTypeError("'%s' is not a reference to an existing file's path" % file_path)

	def file_not_exists(file_path):
		if not (Path(file_path)).is_file():
			return file_path
			
		raise argparse.ArgumentTypeError("'%s' already exists" % file_path)
		
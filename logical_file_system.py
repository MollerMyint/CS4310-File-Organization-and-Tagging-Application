# Import statements
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from basic_file_system import BasicFileSystem
from uuid import UUID, uuid4
from typing import Self

class FileType(Enum):
	TXT = 1
	PNG = 2

@dataclass
class Directory:
	directory_name: str
	parent_directory: Self | None

@dataclass
class FileControlBlock:
	file_name: str
	file_id: UUID
	file_type: FileType
	modified_date: date
	size: int
	parent_dir: Directory
	
class LogicalFileSystem:
	def __init__(self, block_size: int = 1024, memory_size: int = 1024):
		'''	Initializes the logical file system given the block size and memory size.
			Tracks free blocks with tuple ranges; initially all blocks are free from 0 (inclusive) to memory length (exclusive).
			Tracks files stored in memory with a dictionary of file names and tuple ranges indicating where the file blocks are stored.
			:param block_size: block size with a default of 1024 bytes
			:type block_size: int
			:param memory_size: memory size with a default of 1024 blocks
			:type memory_size: int
		'''
		self._file_system = BasicFileSystem(block_size, memory_size)
		self.fcb_table: list[FileControlBlock] = []
		self.directory_table: list[Directory] = []
		self.directory_table.append(Directory("root", None))

	def create_file(self, file_name: str, file_path: str, directory_path: str = "root") -> bool:
		'''	Reads the file from the given file path and creates the file in the given directory in the file system.
			:param file_name: the name of the file to be created
			:type file_name: str
			:param file_path: the path of the file to be read
			:type file_path: str
   			:param directory_path: the path to the file's parent directory
			:type directory_path: str
			:returns boolean True if successful, else False
		'''
		# Return false if the parent directory cannot be found.
		parent_directory = self.find_directory(directory_path)
		if not parent_directory:
			return False
		# Return false if a file of the same name already exists in the given directory.
		if self.find_file(directory_path + "/" + file_name):
			return False
		# Determine the file type.
		file_type = FileType.TXT
		if file_path.endswith("png"):
			file_type = FileType.PNG
		# Store the file data.
		with open(file_path, "rb") as file:
			file_data = file.read()
			fcb = FileControlBlock(file_name, uuid4(), file_type, datetime.now(), len(file_data), parent_directory)
			if self._file_system.store_data(file_data, fcb.file_id):
				self.fcb_table.append(fcb)
				return True
		return False

	def get_file(self, file_name: str, file_path: str) -> bool:
		'''	Get the file from the given file path in the system and output it as a file in the output directory.
			:param file_name: the name of the file to be created
			:type file_name: str
			:param file_path: the path of the file to be taken from the system, separated by '/'s and starting with 'root/'
			:type file_path: str
			:returns boolean True if successful, else False
		'''
		file = self.find_file(file_path)
		if not file:
			return False
		with open(f"output/{file_name}.{file.file_type.name.lower()}", "wb") as f:
			data = self._file_system.get_data(file.file_id)
			if data:
				f.write(data)
				return True
			else:
				return False

	def delete_file_from_path(self, file_path: str) -> bool:
		'''	Deletes the file with the given path from the system.
			:param file_path: the path to the file to be deleted
			:type file_path: str
		'''
		file = self.find_file(file_path)
		if not file:
			return False
		return self.delete_file(file)

	def delete_file(self, file: FileControlBlock) -> bool:
		'''	Deletes the given file from the system.
			:param file: the file to be deleted
			:type file: FileControlBlock
		'''
		if self._file_system.delete_data(file.file_id):
			self.fcb_table.remove(file)
			return True
		return False

	def list_files(self, directory_path: str = ""):
		'''	Lists all file control blocks for files in the given directory.
   			:param directory_path: the path to the directory to list files for, default: all files.
			:type directory_path: str
			:returns a list of file control blocks
		'''
		if not directory_path:
			return self.fcb_table
		given_dir = self.find_directory(directory_path)
		file_list = []
		for fcb in self.fcb_table:
			if fcb.parent_dir == given_dir:
				file_list.append(fcb)
		return file_list

	def create_directory(self, directory_name: str, parent_directory_path: str = "root") -> bool:
		'''	Creates a directory with the given directory name and parent directory.
   			:param directory_name: the name of the directory to be created
			:type directory_name: str
			:param parent_directory_path: the path to the new directory's parent directory, default: root directory.
			:type parent_directory_path: str
			:returns bool True if successful, else False
		'''
		parent_directory = self.find_directory(parent_directory_path)
		if not parent_directory:
			return False
		if self.find_directory(parent_directory_path + "/" + directory_name):
			return False
		self.directory_table.append(Directory(directory_name, parent_directory))
		return True

	def delete_directory_from_path(self, directory_path: str) -> bool:
		'''	Deletes the directory at the given path from the system, as well as all child directories and files.
			:param directory_path: the path to the directory to be deleted
			:type directory_path: str
		'''
		given_dir = self.find_directory(directory_path)
		if not given_dir:
			return False
		return self.delete_directory(given_dir)

	def delete_directory(self, directory: Directory) -> bool:
		'''	Deletes the directory at the given path from the system, as well as all child directories and files.
			:param directory_path: the path to the directory to be deleted
			:type directory_path: str
		'''
		# Find and delete child directories.
		for child_directory in self.directory_table:
			if child_directory.parent_directory == directory:
				self.delete_directory(child_directory)
		# Find and delete child files.
		for fcb in self.fcb_table:
			if fcb.parent_dir == directory:
				self.delete_file(fcb)
		self.directory_table.remove(directory)
		return True


	def list_directories(self, directory_path: str = ""):
		'''	Lists all directories in the given directory.
   			:param directory_path: the path to the directory to list directories for, default: all directories
			:type directory_path: str
			:returns a list of file control blocks
		'''
		if not directory_path:
			return self.directory_table
		given_dir = self.find_directory(directory_path)
		if not given_dir:
			return []
		directory_list = []
		for directory in self.directory_table:
			if directory.parent_directory and directory.parent_directory == given_dir:
				directory_list.append(directory)
		return directory_list

	def find_file(self, file_path: str):
		path_parts = list(reversed(file_path.split("/")))
		for fcb in self.fcb_table:
			if fcb.file_name == path_parts[0]:
				current_directory = fcb.parent_dir
				for dir_name in path_parts[1:]:
					if current_directory and dir_name == current_directory.directory_name:
						current_directory = current_directory.parent_directory
					else:
						break
				else:
					if not current_directory:
						return fcb
		return None

	def find_directory(self, dir_path: str):
		path_parts = list(reversed(dir_path.split("/")))
		for dir in self.directory_table:
			if dir.directory_name == path_parts[0]:
				current_directory = dir.parent_directory
				for dir_name in path_parts[1:]:
					if current_directory and dir_name == current_directory.directory_name:
						current_directory = current_directory.parent_directory
					else:
						break
				else:
					if not current_directory:
						return dir
		return None

def __test():
	lfs = LogicalFileSystem(1024, 1024)
	print(lfs.create_file("Test File", "input.txt"))
	print(lfs.list_files())
	print(lfs.create_directory("New Directory"))
	print(lfs.list_directories())
	print(lfs.list_directories("root"))
	print(lfs.create_file("Test File 2", "/Users/anada/Downloads/sad cat.png", "New Directory"))
	print(lfs.get_file("Test File 2", "root/New Directory/Test File 2"))
	print(lfs.list_files("New Directory"))
	print(lfs.create_file("Test File 2", "input.txt", "Unknown Directory"))
	print(lfs.delete_directory_from_path("root/New Directory"))	
	print(lfs.list_files())
	print(lfs.list_directories())
	print(lfs.get_file("Test File", "root/Test File"))
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

	def create_file(self, file_name: str, file_path: str, directory_name: str = "root") -> bool:
		'''	Reads the file from the given file path and creates the file in the given directory in the file system.
			:param file_name: the name of the file to be created
			:type file_name: str
			:param file_path: the path of the file to be read
			:type file_path: str
   			:param directory_name: the name of the file's parent directory
			:type directory_name: str
			:returns boolean True if successful, else False
		'''
		for fcb in self.fcb_table:
			if fcb.file_name == file_name and fcb.parent_dir.directory_name == directory_name:
				return False
		directory: Directory | None = None
		for dir in self.directory_table:
			if dir.directory_name == directory_name:
				directory = dir
				break
		if not directory:
			return False
		with open(file_path, "rb") as file:
			file_data = file.read()
			fcb = FileControlBlock(file_name, uuid4(), FileType.TXT, datetime.now(), len(file_data), directory)
			if self._file_system.store_data(file_data, fcb.file_id):
				self.fcb_table.append(fcb)
				return True
		return False

	def get_file(self, file_name: str, file_path: str = "") -> bool:
		'''	Get the file from the given file path in the system and output it as a file in the output directory.
			:param file_name: the name of the file to be created
			:type file_name: str
			:param file_path: the path of the file to be taken from the system, separated by '/'s and starting with 'root/', Default: all files with that name.
			:type file_path: str
			:returns boolean True if successful, else False
		'''
		file_found = False
		for fcb in self.fcb_table:
			if fcb.file_name == file_name:
				path_parts = reversed(file_path.split("/"))
				current_directory = fcb.parent_dir
				for dir_name in path_parts:
					if current_directory and dir_name == current_directory.directory_name:
						current_directory = current_directory.parent_directory
					elif file_path != "":
						break
				else:
					if not current_directory or file_path == "":
						try:
							with open(f"output/{file_name}", "xb") as f:
								data = self._file_system.get_data(fcb.file_id)
								if data:
									f.write(data)
									if file_path == "":
										file_found = True
									else:
										return True
								else:
									return False
						except FileExistsError:
							return False
		return file_found

	def delete_file(self, file_name: str) -> bool:
		'''	Deletes the file with the given name from the system.
			:param file_name: the name of the file to be deleted
			:type file_name: str
		'''
		for fcb in self.fcb_table:
			if fcb.file_name == file_name:
				if self._file_system.delete_data(fcb.file_id):
					self.fcb_table.remove(fcb)
					return True
				else:
					return False
		return False

	def list_files(self, directory_name: str = ""):
		'''	Lists all file control blocks for files in the given directory.
   			:param directory_name: the name of the directory to list files for, default: all files.
			:type directory_name: str
			:returns a list of file control blocks
		'''
		if not directory_name:
			return self.fcb_table
		file_list = []
		for fcb in self.fcb_table:
			if fcb.parent_dir.directory_name == directory_name:
				file_list.append(fcb)
		return file_list

	def create_directory(self, directory_name: str, parent_directory_name: str = "root") -> bool:
		'''	Creates a directory with the given directory name and parent directory.
   			:param directory_name: the name of the directory to be created
			:type directory_name: str
			:param parent_directory_name: the name of the new directory's parent directory, default: root directory.
			:type parent_directory_name: str
			:returns bool True if successful, else False
		'''
		parent_directory: Directory | None = None
		for dir in self.directory_table:
			if dir.directory_name == parent_directory_name:
				parent_directory = dir
				# Continue searching for a directory of the same name with the same parent.
			elif dir.directory_name == directory_name and dir.parent_directory and dir.parent_directory.directory_name == parent_directory_name:
				return False
		if not parent_directory:
			return False
		self.directory_table.append(Directory(directory_name, parent_directory))
		return True

	def delete_directory(self, directory_name: str) -> bool:
		'''	Deletes the directory with the given name from the system, as well as all child directories and files.
			:param directory_name: the name of the file to be deleted
			:type directory_name: str
		'''
		for del_directory in self.directory_table:
			if del_directory.directory_name == directory_name:
				# Find and delete child directories.
				for child_directory in self.directory_table:
					if child_directory.parent_directory and child_directory.parent_directory.directory_name == directory_name:
						self.delete_directory(child_directory.directory_name)
				# Find and delete child files.
				for fcb in self.fcb_table:
					if fcb.parent_dir.directory_name == directory_name:
						self.delete_file(fcb.file_name)
				self.directory_table.remove(del_directory)
				return True
		return False

	def list_directories(self, directory_name: str = ""):
		'''	Lists all directories in the given directory.
   			:param directory_name: the name of the directory to list directories for, default: all directories
			:type directory_name: str
			:returns a list of file control blocks
		'''
		if not directory_name:
			return self.directory_table
		directory_list = []
		for directory in self.directory_table:
			if directory.parent_directory and directory.parent_directory.directory_name == directory_name:
				directory_list.append(directory)
		return directory_list

def __test():
	lfs = LogicalFileSystem(10, 10)
	print(lfs.create_file("Test File.txt", "input.txt"))
	print(lfs.list_files())
	print(lfs.create_directory("New Directory"))
	print(lfs.list_directories())
	print(lfs.list_directories("root"))
	print(lfs.create_file("Test File 2.txt", "input.txt", "New Directory"))
	print(lfs.list_files("New Directory"))
	print(lfs.create_file("Test File 2.txt", "input.txt", "Unknown Directory"))
	print(lfs.delete_directory("New Directory"))	
	print(lfs.list_files())
	print(lfs.list_directories())
	print(lfs.get_file("Test File.txt"))
__test()
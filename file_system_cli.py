from logical_file_system import Directory, LogicalFileSystem
from shlex import split

class CommandLineInterface():
	def __init__(self, block_size: int = 1024, memory_size: int = 1024):
		'''	Initializes the file system given the block size and memory size.
			:param block_size: block size with a default of 1024 bytes
			:type block_size: int
			:param memory_size: memory size with a default of 1024 blocks
			:type memory_size: int
		'''
		self._file_system = LogicalFileSystem(block_size, memory_size)
		self._directory_path: list[Directory] = [self._file_system.list_directories()[0]]
	
	def path_to_string(self):
		path = self._directory_path[0].directory_name
		for dir in self._directory_path[1:]:
			path +=  "/" + dir.directory_name
		return path

	def start(self):
		print("Starting File System...")
		print("System started. Welcome!")
		running = True
		# Main user interaction loop.
		while (running):
			user_input = split(input(f"{[dir.directory_name for dir in self._directory_path]} 🦆 "))
			if user_input:
				match user_input[0].lower():
					case "help":
						print("~~~Command List~~~\nhelp - displays commands\ncd :dir - enter directory dir\nls -fd - list files (f) and/or directories (d) in current directory, default both\nget :fileName o:newFileName - puts the given file in the output directory, optional new file name\nmkfile :filePath o:fileName - adds the file from the given file path to the current directory, optional file name\nmkdir :dirName - makes a directory with the given name in the current directory\nrmfile :fileName - deletes the file in the current directory with the given name\nrmdir :dirName - deletes the directory in the current directory with the given name, as well as all of its contents\nexit - exits the program")
					# Case for entering a different directory.
					case "cd":
						if len(user_input) == 1:
							print("Error: No directory given")
						else:
							if user_input[1] == "..":
								if len(self._directory_path) > 1:
									self._directory_path.pop()
							else:
								directory = self._file_system.find_directory(self.path_to_string() + "/" + user_input[1])
								if directory:
									self._directory_path.append(directory)
								else:
									print(f"Error: Directory '{user_input[1]}' not found in current directory")
					# Case for listing files or directories in the current directory.
					case "ls":
						if len(user_input) == 1:
							user_input.append("-fd")
						flags = user_input[1]
						match flags:
							case "-d":
								for dir in self._file_system.list_directories(self.path_to_string()):
									print(f"{'Dir:':5} {dir.directory_name}")
							case "-f":
								for file in self._file_system.list_files(self.path_to_string()):
									print(f"{'File:':5} {file.file_name}.{file.file_type.name} {file.modified_date} {file.size}")
							case "-fd" | "-df":
								for dir in self._file_system.list_directories(self.path_to_string()):
									print(f"{'Dir:':5} {dir.directory_name}")
								for file in self._file_system.list_files(self.path_to_string()):
									print(f"{'File:':5} {file.file_name}.{file.file_type.name} {file.modified_date} {file.size}")
							case _:
								print("Error: Flags not recognized")
					# Case for retrieving a file and putting it in the output directory.
					case "get":
						if len(user_input) == 1:
							print("Error: No file given")
						elif len(user_input) > 3:
							print("Error: Too many parameters given for command get (maximum 3)")
						else:
							if len(user_input) == 3:
								file_name = user_input[2]
							else:
								file_name = user_input[1]
							path = self.path_to_string() + "/" + user_input[1]
							if self._file_system.get_file(file_name, path):
								print(f"Success: File '{file_name}' retrieved")
							else:
								print(f"Error: File '{user_input[1]}' not found at path '{path}'")		
					# Case for adding a file to the file system.
					case "mkfile":
						if len(user_input) == 1:
							print("Error: No file path given")
						elif len(user_input) > 3:
							print("Error: Too many parameters given for command mkfile (maximum 3)")
						else:
							if len(user_input) == 3:
								file_name = user_input[2]
							else:
								file_name = user_input[1].split("/")[-1].removesuffix(".png").removesuffix(".txt")
							if self._file_system.create_file(file_name, user_input[1], self.path_to_string()):
								print(f"Success: file '{file_name}' created")
							else:
								print(f"Error: Unable to create file '{file_name}'")
					# Case for adding a directory to the file system.
					case "mkdir":
						if len(user_input) == 1:
							print("Error: No directory name given")
						else:
							for dir_name in user_input[1:]:	
								if self._file_system.create_directory(dir_name, self.path_to_string()):
									print(f"Success: directory '{dir_name}' created")
								else:
									print(f"Error: Unable to create directory '{dir_name}' - directory already exists")
					case "rmfile":
						if len(user_input) == 1:
							print("Error: No file name given")
						elif self._file_system.delete_file_from_path(f"{self.path_to_string()}/{user_input[1]}"):
								print(f"Success: file '{user_input[1]}' deleted")
						else:
							print(f"Error: Unable to delete file {user_input[1]}")
					case "rmdir":
						if len(user_input) == 1:
							print("Error: No directory name given")
						elif self._file_system.delete_directory_from_path(f"{self.path_to_string()}/{user_input[1]}"):
								print(f"Success: directory '{user_input[1]}' deleted")
						else:
							print(f"Error: Unable to delete directory {user_input[1]}")			
					# Case for exiting the program.
					case "exit":
						print("System shutting down...")
						print("See you next time!")
						running = False
     				# Case for unknown user input.
					case _:
						print(f"Error: Unknown command - '{user_input[0]}'")
					
if __name__ == "__main__":
	cli = CommandLineInterface()
	cli.start()
# Import statements
from memory_system import MemorySystem
from math import ceil

class FileSystem:
	def __init__(self, block_size: int = 1024, memory_size: int = 1024):
		'''	Initializes the file system given the block size and memory size.
			Tracks free blocks with tuple ranges; initially all blocks are free from 0 (inclusive) to memory length (exclusive).
			Tracks files stored in memory with a dictionary of file names and tuple ranges indicating where the file blocks are stored.
			:param block_size: block size with a default of 1024 bytes
			:type block_size: int
			:param memory_size: memory size with a default of 1024 blocks
			:type memory_size: int
		'''
		self._memory_system = MemorySystem(block_size, memory_size)
		self._free_blocks = [(0, memory_size)]
		self._file_table: dict[str, list[tuple[int, int]]] = {}
	
	def store_file(self, file_data: bytes, file_name: str):
		'''	Stores the given file data in memory and adds it to the file table.
			:param file_data: the file data in bytes
			:type file_data: int
			:param file_name: the file name
			:type file_name: str
			:returns boolean True if successful, else False
		'''
		# Return false if a file of the same name is already in memory.
		if self._file_table.get(file_name):
			return False
		num_blocks = ceil(len(file_data) / self._memory_system.block_size)
		# Check if there is enough space to accomodate the file data.
		if not self.__check_space(num_blocks):
			return False
		blocks_used: list[tuple[int, int]] = []
		# While the file data is not entirely stored:
		while num_blocks != 0:
			# Search for a free block that is big enough to store the file data.
			for free_block in self._free_blocks:
				if free_block[1] - free_block[0] >= num_blocks:
					# Store the file data in the block and 
					result = self.__store_blocks(file_data, free_block)
					assert isinstance(result, tuple)
					blocks_used.append(result)
					num_blocks = 0
					self._free_blocks.remove(free_block)
					if free_block[1] != result[1]:
						self._free_blocks.append((result[1], free_block[1]))
					break
			# If no block big enough is found then store as much data as possible in the largest free block and repeat.
			if num_blocks != 0:
				free_block = self._free_blocks.pop()
				result = self.__store_blocks(file_data, free_block)
				assert isinstance(result, bytes)
				blocks_used.append(free_block)
				file_data = result
				num_blocks = ceil(len(file_data) / self._memory_system.block_size)
		self._file_table.update([(file_name, blocks_used)])
		self.__sort_free_blocks()
		return True
   
	def get_file(self, file_name: str):
		'''	Gets the file data associated with the given file name.
			:param file_name: the file name
			:type file_data: str
			:returns the file data if the file exists, else False
		'''
		file_blocks = self._file_table.get(file_name)
		if not file_blocks:
			return False
		return self.__get_blocks(file_blocks)
		
	def delete_file(self, file_name: str):
		'''	Deletes the file data associated with the given file name.
			:param file_name: the file name
			:type file_data: str
			:returns boolean True if successful, else False
		'''
		file_blocks = self._file_table.get(file_name)
		if not file_blocks:
			return False
		if not self.__empty_blocks(file_blocks):
			# THROW ERROR HERE
			return False
		for block_range in file_blocks:
			for free_block in self._free_blocks:
				if free_block[1] == block_range[0]:
					self._free_blocks.remove(free_block)
					self._free_blocks.append((free_block[0], block_range[1]))
					break
				elif free_block[0] == block_range[1]:
					self._free_blocks.remove(free_block)
					self._free_blocks.append((block_range[0], free_block[1]))
					break
			else:
				self._free_blocks.append(block_range)
		self._file_table.pop(file_name)
		self.__sort_free_blocks()
		return True

	def __check_space(self, num_blocks: int) -> bool:
		for free_block in reversed(self._free_blocks):
			num_blocks -= free_block[1] - free_block[0]
			if num_blocks <= 0:
				return True
		return False

	def __store_blocks(self, file_data: bytes, block_range: tuple[int, int]):
		for block in range(block_range[0], block_range[1]):
			self._memory_system.fill_block(block, file_data[:self._memory_system.block_size])
			file_data = file_data[self._memory_system.block_size:]
			if not file_data:
				return (block_range[0], block + 1)
		return file_data	

	def __get_blocks(self, block_ranges: list[tuple[int, int]]):
		data = bytes()
		for block_range in block_ranges:
			for block in range(block_range[0], block_range[1]):
				result = self._memory_system.get_block(block)
				if not result:
					return False
				data += result
		return data

	def __empty_blocks(self, block_ranges: list[tuple[int, int]]):
		for block_range in block_ranges:
			for block in range(block_range[0], block_range[1]):
				result = self._memory_system.empty_block(block)
				if not result:
					return False
		return True

	def __sort_free_blocks(self):	
		self._free_blocks.sort(key=lambda tup: tup[1] - tup[0])
  
  
def __test():
	fs = FileSystem(10, 10)
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
	print(fs.store_file(bytes("This is a string.", "utf-8"), "File Name"))
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
	print(fs.get_file("File Name"))
	print(fs.store_file(bytes("This is a string.", "utf-8"), "File Name"))
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
	print(fs.store_file(bytes("This is another string that's pretty long and takes space.", "utf-8"), "File Name 2"))
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
	print(fs.delete_file("File Name"))
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
	print(fs.store_file(bytes("This is a string again.", "utf-8"), "File Name 3"))
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
	print(fs.delete_file("File Name 2"))
	print(fs._file_table)
	print(fs._free_blocks)
	print(fs._memory_system._memory)
 
__test()
class MemorySystem:
	'''	Class that simulates a memory system with a fixed size list and block size.
	'''
    
	def __init__(self, block_size: int = 1024, memory_size: int = 1024):
		'''	Initializes the memory given the block size and memory size.
			:param block_size: block size with a default of 1024 bytes
			:type block_size: int
			:param memory_size: memory size with a default of 1024 blocks
			:type memory_size: int
		'''
		self.block_size = block_size
		self.memory_size = memory_size
		self.memory:list[bytes|None] = [None] * memory_size

	def validIndex(self, index:int):
		'''	Checks if the given index is a valid index in memory.
			:param index: the index to be checked
			:type block_size: int
		'''
		if index < 0 or index >= self.memory_size:
			return False
		else:
			return True

	def fillBlock(self, index:int, data:bytes):
		'''	Fills the block at the given index
			:param index: the index of the block to be filled
			:type block_size: int
			:param data: the data with which to fill the block
			:type data: bytes
		'''
		if not self.validIndex(index):
			return 1
		if len(data) > self.block_size:
			return 2
		block = data
		self.memory[index] = block
		return 0
	
	def getBlock(self, index:int):
		'''	Returns the block at the given index
			:param index: the index of the block to be returned
			:type block_size: int
		'''
		if not self.validIndex(index):
			return 1
		block = self.memory[index]
		return block
 
	def emptyBlock(self, index:int):
		'''	Empties the block at the given index
			:param index: the index of the block to be emptied
			:type block_size: int
		'''
		if not self.validIndex(index):
			return 1
		self.memory[index] = None
		return 0
	
def test():
	'''	Tests all functions and outputs of the MemorySystem methods.
	'''
	format_string = "{0:55}{1:<10}{2}"
	print("********************* Beginning Testing *********************")
	print("ms = MemorySystem(10, 10)")
	ms = MemorySystem(10, 10)
	print(format_string.format("Call", "Expected", "Actual"))
	print(format_string.format("ms.fillBlock(0, bytes('Test1', 'utf-8'))", 0, ms.fillBlock(0, bytes('Test1', 'utf-8'))))
	print(format_string.format("ms.fillBlock(1, bytes('Test2', 'utf-8'))", 0, ms.fillBlock(1, bytes('Test2', 'utf-8'))))
	print(format_string.format("ms.fillBlock(0, bytes('Test3', 'utf-8'))", 0, ms.fillBlock(0, bytes('Test3', 'utf-8'))))
	block1 = ms.getBlock(0)	
	print("block1 = ms.getBlock(0)")
	print(format_string.format("block1.decode() if block1 and block1 != 1 else None", "Test3", block1.decode() if block1 and block1 != 1 else None))
	block2 = ms.getBlock(1)	
	print("block2 = ms.getBlock(1)")
	print(format_string.format("block2.decode() if block2 and block2 != 1 else None", "Test2", block2.decode() if block2 and block2 != 1 else None))
	print(format_string.format("ms.fillBlock(1, bytes('Test4', 'utf-8'))", 0, ms.fillBlock(1, bytes('Test4', 'utf-8'))))
	block3 = ms.getBlock(1)	
	print("block3 = ms.getBlock(1)")
	print(format_string.format("block3.decode() if block3 and block3 != 1 else None", "Test4", block3.decode() if block3 and block3 != 1 else None))
	print(format_string.format("ms.emptyBlock(0)", 0, ms.emptyBlock(0)))
	print(format_string.format("ms.fillBlock(1,bytes('Str too long','utf-8'))", 2, ms.fillBlock(1, bytes('Str too long', 'utf-8'))))	
	block4 = ms.getBlock(0)	
	print("block4 = ms.getBlock(0)")
	print(format_string.format("block4.decode() if block4 and block4 != 1 else None", "None", block4.decode() if block4 and block4 != 1 else None))	
	print(format_string.format("ms.fillBlock(10, bytes('Test5', 'utf-8'))", 1, ms.fillBlock(10, bytes('Test5', 'utf-8'))))
	print(format_string.format("ms.getBlock(10)", 1, ms.getBlock(10)))
	print(format_string.format("ms.emptyBlock(10)", 1, ms.emptyBlock(10)))
	print("{0:25} {1}".format("Expected Final Memory:", "[None, b'Test4', None, None, None, None, None, None, None, None]"))
	print("{0:25} {1}".format("Final Memory:", ms.memory))
 
if (__name__ == "__main__"):
	test()
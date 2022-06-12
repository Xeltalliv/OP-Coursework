import random

class BinFile:
	# Спроба відкрити файл та знайти його розмір
	def __init__(self, name, mode="r+b"):
		try:
			myFile = open(name, mode)
			self.myFile = myFile
			myFile.seek(0,2)
			self.size = myFile.tell()
			self.ok = True
		except IOError:
			self.ok = False


	# Зчитування одного числа на позиції pos
	def getInt32(self, pos):
		self.myFile.seek(pos)
		arr = self.myFile.read(4)
		return ((arr[3]*256+arr[2])*256+arr[1])*256+arr[0]


	# Зчитування amount чисел починаючи з позиції pos
	def getInts32(self, pos, amount):
		self.myFile.seek(pos)
		arr = self.myFile.read(amount*4)
		outputs = []
		for i in range(0, len(arr), 4):
			outputs.append(((arr[i+3]*256+arr[i+2])*256+arr[i+1])*256+arr[i])
		return outputs


	# Запис одного числа на позиції pos
	def setInt32(self, pos, value):
		self.myFile.seek(pos)
		arr = []
		for i in range(4):
			arr.append(value % 256)
			value //= 256
		self.myFile.write(bytearray(arr))


	# Запис маисву чисел починаючи з позиції pos
	def setInts32(self, pos, values):
		self.myFile.seek(pos)
		arr = []
		for j in range(len(values)):
			value = values[j]
			for i in range(4):
				arr.append(value % 256)
				value //= 256
		self.myFile.write(bytearray(arr))
	

	# Закриття файлу
	def close(self):
		self.myFile.close()


	# Задання вмісту файла на випадкові числа
	def randomize(self, size, valFrom, valTo):
		for pos in range(size):
			self.setInt32(pos*4, random.randint(valFrom, valTo))
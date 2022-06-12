#!/bin/env python3

import os
from BinFile import BinFile


class Sort1:
	def __init__(self, fileToSort):
		self.binFile = fileToSort
		self.tmpFile = BinFile("tmp.bin","x+b")
		self.statsMerges = 0
		self.statsLevels = 0
		self.statsRuns = 0


	def sort(self):
		# Цей масив зберігає набір значень що можуть бути:
		#   1. масивом з 2х елементів, що позначає проміжок
		#   2. число 0, що позначає відсутність проміжку
		self.sections = []

		# Проходження по всім числам в файлі та знаходження
		# вже відсортованих секцій. Коли кінець відсортованої
		# секції знайдено, вона подається у метод doLevel на
		# 1й рівень.
		f = self.binFile
		pos = 0
		size = self.binFile.size
		lastValue = -1
		start = 0
		while pos < size:
			curValue = f.getInt32(pos)
			if curValue < lastValue:
				self.statsRuns += 1
				self.doLevel([start, pos], 0)
				start = pos
			lastValue = curValue
			pos += 4

		self.doLevel([start, pos], 0)
		self.statsRuns += 1


		# Додання пустих секцій, щоб всі необроблені секції могли обробитися
		for level in range(len(self.sections)):
			if self.sections[level] != 0:
				self.doLevel([pos, pos], level)


	# Отримуючи секцію та рівень, цей метод
	# перевіряє, чи є на тому рівні вже інша секція.
	# Якщо ні, то вона записується у той рівень.
	# Якщо так, то вона зливається з вже існуючою
	# секцією на тому рівні та секція-результат передається
	# у doLevel на наступний рівень.
	def doLevel(self, section, level):
		if level > self.statsLevels:
			self.statsLevels = level

		if len(self.sections) == level:
			self.sections.append(0)

		if self.sections[level] == 0:
			self.sections[level] = section
		else:
			i1 = self.sections[level][0]
			i2 = section[0]
			e1 = self.sections[level][1]
			e2 = section[1]
			done = 0
			pos = self.sections[level][0]

			# Перевірка чи секція 1 - пуста
			if i1 == e1:
				v1 = 999999999999999
				done += 1
			else:
				v1 = self.binFile.getInt32(i1)

			# Перевірка чи секція 2 - пуста
			if i2 == e2:
				v2 = 999999999999999
				done += 1
			else:
				v2 = self.binFile.getInt32(i2)

			self.statsMerges += 1

			while done < 2:
				# Обрання найменшого значення
				if v1 > v2:
					# Запис поточного значення і перехід на наступне
					self.tmpFile.setInt32(pos, v2)
					i2 += 4
					# Перевірка чи секція 2 скінчилася
					if i2 >= e2:
						v2 = 99999999999999
						done += 1
					else:
						v2 = self.binFile.getInt32(i2)
				else:
					# Запис поточного значення і перехід на наступне
					self.tmpFile.setInt32(pos, v1)
					i1 += 4
					# Перевірка чи секція 1 скінчилася
					if i1 >= e1:
						v1 = 99999999999999
						done += 1
					else:
						v1 = self.binFile.getInt32(i1)
				pos += 4

			start = self.sections[level][0]
			end = section[1]

			# Копіювання з тимчасового файлу у основний
			length = pos
			pos = self.sections[level][0]
			while pos < length:
				self.binFile.setInt32(pos, self.tmpFile.getInt32(pos))
				pos += 4

			self.sections[level] = 0
			# Результат на наступний рівень
			self.doLevel([start, end], level+1)


	# Метод для отримання статистики сортування
	def getResult(self):
		return "Метод: Природне злиття\nКількість секцій (runs): "+str(self.statsRuns)+"\nКількість злиттів: "+str(self.statsMerges)+"\nКількість рівнів: "+str(self.statsLevels)


	def __del__(self):
		self.tmpFile.close()
		os.remove("tmp.bin")
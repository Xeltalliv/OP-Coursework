#!/bin/env python3

import os

from BinFile import BinFile


class Sort2:
	def __init__(self, fileToSort, runSize, fileCount):
		self.binFile = fileToSort
		self.runSize = runSize
		self.fileCount = fileCount
		self.runCount = 0
		self.runSizes = [] # Однорівневий масив, що зберігає
		# довжини всіх секцій послідовно постійно змінюючи файл
		self.statsMerges = 0
		self.statsIterations = 0


	# Основний метод сортування, що викликає всі інші дії по черзі
	def sort(self):
		self.createFiles()
		self.fillInitialRuns()
		self.actualSorting()
		self.resultToInputFile()
		self.clearTemporaryFiles()


	# Розбиває основний файл на секції заданого розміру та заповнює тимчасові файли приблизно однаково
	def fillInitialRuns(self):
		f = self.binFile
		outIndex = 0
		posFrom = 0
		posTo = 0
		runCount = 0
		while posFrom < f.size:
			run = self.insertionSort(f.getInts32(posFrom, self.runSize))
			self.aFiles[outIndex].setInts32(posTo, run)
			self.runSizes.append(len(run))
			outIndex += 1
			runCount += 1
			posFrom += 4 * self.runSize
			if outIndex == self.fileCount:
				outIndex = 0
				posTo += 4 * self.runSize
		self.runCount = runCount


	# Виконання ітерацій поки все не буде злито в 1 секцію.
	# В кінці ітерації відбувається обмін файлів
	def actualSorting(self):
		while self.runCount > 1:
			self.statsIterations += 1
			self.singeSortingIteration()
			self.aFiles, self.bFiles = self.bFiles, self.aFiles


	# 1 ітерація передбачає повтор злиття одного рівня для всіх рівнів
	def singeSortingIteration(self):
		self.runOffset = 0
		self.outPos = [0 for i in range(self.fileCount)]
		self.outFile = 0
		self.filePos = [0 for i in range(self.fileCount)]
		self.posStart = [0 for i in range(self.fileCount)]
		newRunCount = 0
		newRunSizes = []
		while self.runCount > 0:
			newRunSizes.append(self.mergeLayerOfRuns())
			newRunCount += 1
		self.runCount = newRunCount
		self.runSizes = newRunSizes


	# Злиття 1-го рівня передбачає озяття по 1й ще не
	# обробленій секції з кожного файлу та злитті їх у 1
	# велику секцію у поточному вихідному файлі, після
	# чого, зміна вихідного файла на інший.
	def mergeLayerOfRuns(self):
		#print("layer")
		self.statsMerges += 1
		lengthOfResultingRun = 0
		idxMin = 1
		while idxMin > -1:
			# Циклом пройтись по всім обробюемим секціям та обрати найменше значення
			idxMin = -1
			valMin = 9999999999
			for i in range(min(self.fileCount, self.runCount)):
				if self.runOffset + i < len(self.runSizes):
					thisSize = self.runSizes[self.runOffset + i] * 4
				else:
					thisSize = 0

				if self.filePos[i] < self.posStart[i] + thisSize:
					val = self.aFiles[i].getInt32(self.filePos[i])
					if val < valMin:
						valMin = val
						idxMin = i
			
			# Якщо знайдено, записати
			if idxMin > -1:
				self.filePos[idxMin] += 4
				self.bFiles[self.outFile].setInt32(self.outPos[self.outFile], valMin)
				self.outPos[self.outFile] += 4


		for i in range(min(self.fileCount, self.runCount)):
			lengthOfResultingRun += self.runSizes[self.runOffset + i]
			self.posStart[i] += self.runSizes[self.runOffset + i] * 4

		# Зміна місця, з якого буде зчитуватися розмір секцій
		self.runOffset += self.fileCount

		# Перемкнення на наступний файл
		self.outFile += 1
		self.runCount -= self.fileCount
		if self.outFile == self.fileCount:
			self.outFile = 0
			

		return lengthOfResultingRun
		

	# Сортування вставкою
	def resultToInputFile(self):
		fFrom = self.aFiles[0]
		fTo = self.binFile
		pos = 0
		while pos < fTo.size:
			fTo.setInt32(pos, fFrom.getInt32(pos))
			pos += 4


	# Сортування вставкою
	def insertionSort(self, arr):
		for i in range(1, len(arr)):
			current = arr[i]
			j = i
			while arr[j-1] > current and j > 0:
				arr[j] = arr[j-1]
				j -= 1
			arr[j] = current
		return arr


	# Метод для створення тимчасових файлів
	def createFiles(self):
		aFiles = []
		bFiles = []
		for i in range(self.fileCount):
			aFiles.append(BinFile("tmpA"+str(i)+".bin","x+b"))
			bFiles.append(BinFile("tmpB"+str(i)+".bin","x+b"))
		self.aFiles = aFiles
		self.bFiles = bFiles


	# Метод для видалення тимчасових файлів після завершення сортування
	def clearTemporaryFiles(self):
		for i in range(self.fileCount):
			self.aFiles[i].close()
			self.bFiles[i].close()
			os.remove("tmpA"+str(i)+".bin")
			os.remove("tmpB"+str(i)+".bin")


	# Метод для отримання статистики сортування
	def getResult(self):
		return "Метод: Збалансоване багатошляхове злиття\nКількість файлів одної сторони: "+str(self.fileCount)+"\nЗагальна кількість файлів: "+str(self.fileCount*2+1)+"\nРозмір початкових секцій: "+str(self.runSize)+"\nКількість злиттів: "+str(self.statsMerges)+"\nКількість ітерацій: "+str(self.statsIterations)
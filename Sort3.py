#!/bin/env python3

import os
import math

from BinFile import BinFile

class Sort3:
	def __init__(self, fileToSort, runSize, fileCount):
		self.myFile = fileToSort
		self.runSize = runSize
		self.fileCount = fileCount
		self.runCount = math.ceil(fileToSort.size / runSize / 4)
		self.runSizes = [] # Масив з 1-м масивом для кожного з файлів. Кожне число - кількість елементів в секції
		self.statsRuns = 0
		self.statsMerges = 0
		self.statsSwaps = 0


	# Сортування вставкою
	def sort(self):
		self.createFiles()
		self.fillInitialRuns()
		self.actualSorting()
		self.resultToInputFile()
		self.clearTemporaryFiles()


	# Метод знаходження оптимального розподілу секцій між файлами.
	# Повертає масив з числами, де кожне числе відповідає за кількість в файлі
	# Також повертає суму всіх чисел в масиві
	def findDistributions(self):
		# На початку кожен файл має одну секцію
		distr = [1 for x in range(self.fileCount-1)]
		summ = self.fileCount-1

		# Повторювати поки недостатньо
		while summ < self.runCount:
			# Знайти найбільший елемент
			maxi = 0
			maxc = distr[0]
			for i in range(self.fileCount-1):
				if distr[i] > maxc:
					maxi = i
					maxc = distr[maxi]

			# Швидка фармула знаходження суми
			summ += maxc * (self.fileCount-2)

			# Змільшити всі файли на значення найбільшого елемента крім самого елемента
			for i in range(self.fileCount-1):
				if i != maxi:
					distr[i] += maxc
		return (distr, summ)


	# Розбиття оригінального файлу на секції та розкладання
	# їх у файли згідно з розподілом попереднього метода.
	# Дозаповнення залишку пустими секціями
	def fillInitialRuns(self):
		distr, summ = self.findDistributions()
		self.statsRuns = summ
		self.runSizes = [[] for i in range(1, self.fileCount)]
		f = self.myFile
		outIndex = 0
		posFrom = 0
		posTo = 0
		runCount = 0

		# Повторювати до додання потрібної кількості секцій
		while runCount < summ:
			# Якщо файл заповнений, обрати інший
			while distr[outIndex] < 1:
				outIndex += 1
				if outIndex == self.fileCount - 1:
					outIndex = 0
					posTo += 4 * self.runSize

			# Додати відсортовану секцію
			run = self.insertionSort(f.getInts32(posFrom, self.runSize))
			self.aFiles[outIndex].setInts32(posTo, run)
			distr[outIndex] -= 1


			self.runSizes[outIndex].append(len(run))
			# Наступний файл
			outIndex += 1
			runCount += 1
			posFrom += 4 * self.runSize
			# Якщо індекс файлу завелеикий, почати з початку
			if outIndex == self.fileCount - 1:
				outIndex = 0
				posTo += 4 * self.runSize
		self.runCount = runCount


	# Продовжує зливати по одній секції з
	# кожно файлу в одну велику секцію до
	# моменту коли залишиться лише 1 секція
	def actualSorting(self):
		self.outPos = 0
		self.outSizes = []
		self.activeRun = [0 for i in range(self.fileCount-1)] # Номер активної секції в файлі
		self.filePos = [0 for i in range(self.fileCount-1)]   # Мізце зчитування в файлі
		self.runStarts = [0 for i in range(self.fileCount-1)] # Місце початку активної секції
		self.found = 123 # Число > 1 для першого спацювання циклу
		while self.found > 1:
			self.mergeLayerOfRuns()


	def mergeLayerOfRuns(self):
		self.statsMerges += 1
		idxMin = 1
		outputRunLength = 0
		while idxMin > -1:
			self.found = 0
			# Пройтись по всім файлам і знайти найменше
			idxMin = -1
			valMin = 9999999999
			for i in range(self.fileCount-1):
				ar = self.activeRun[i]
				if ar < len(self.runSizes[i]):
					# Збільшити кількість секцій на один, навіть якщо це пуста секція, що занчилася.
					# Але не збільшувати, якщо секції не існує.
					self.found += 1
					if self.filePos[i] < self.runStarts[i] + self.runSizes[i][ar] * 4:
						val = self.aFiles[i].getInt32(self.filePos[i])
						if val < valMin:
							valMin = val
							idxMin = i
			
			# Якщо знайдено, дописати
			if idxMin > -1:
				self.filePos[idxMin] += 4
				self.bFile.setInt32(self.outPos, valMin)
				outputRunLength += 1
				self.outPos += 4

		# Підготовка до опрацювання по 1й наступній секції з кожного файлу
		for i in range(self.fileCount-1):
			ar = self.activeRun[i]
			if ar < len(self.runSizes[i]):
				self.runStarts[i] += self.runSizes[i][ar] * 4
			self.activeRun[i] += 1

		self.outSizes.append(outputRunLength)

		# Перевірка чи портібно змінити файл виводу
		change = -1
		for i in range(self.fileCount-1):
			if self.activeRun[i] >= len(self.runSizes[i]):
				change = i

		if change > -1 and self.found > 1:
			self.statsSwaps += 1
			self.activeRun[change] = 0
			self.filePos[change] = 0
			self.runStarts[change] = 0
			self.runSizes[change] = self.outSizes
			self.aFiles[change], self.bFile = self.bFile, self.aFiles[change]
			self.outSizes = []
			self.outPos = 0


	# Метод для копіювання відсортованого масиву з тимчасового файлу у основний файл
	def resultToInputFile(self):
		fFrom = self.bFile
		fTo = self.myFile
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
		self.bFile = BinFile("tmp0.bin","x+b")
		for i in range(1, self.fileCount):
			aFiles.append(BinFile("tmp"+str(i)+".bin","x+b"))
		self.aFiles = aFiles


	# Метод для видалення тимчасових файлів після завершення сортування
	def clearTemporaryFiles(self):
		self.bFile.close()

		for fl in self.aFiles:
			fl.close()

		for i in range(self.fileCount):
			os.remove("tmp"+str(i)+".bin")


	# Метод для отримання статистики сортування
	def getResult(self):
		return "Кількість тимчасових файлів: "+str(self.fileCount)+"\nЗагальна кількість файлів: "+str(self.fileCount+1)+"\nРозмір початкових секцій: "+str(self.runSize)+"\nКількість секцій: "+str(self.statsRuns)+"\nКількість злиттів: "+str(self.statsMerges)+"\nКількість переключень файлів: "+str(self.statsSwaps)
#!/bin/env python3

import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from BinFile import BinFile
from Sort1 import Sort1
from Sort2 import Sort2
from Sort3 import Sort3
from ViewWindow import ViewWindow

class MainWindow(Gtk.Window):
	def __init__(self):
		super().__init__(title="Курсова робота")

		self.viewWin = None

		# Заповнення вікна елементами
		vbox = Gtk.VBox()
		vbox.set_border_width(10)
		self.add(vbox)

		hbox1 = Gtk.HBox()
		hbox2 = Gtk.VBox()
		hbox3 = Gtk.VBox()
		hbox1.set_border_width(10)
		hbox2.set_border_width(10)
		hbox3.set_border_width(10)

		frame1 = Gtk.Frame()
		frame2 = Gtk.Frame()
		frame3 = Gtk.Frame()

		frame1.set_label("Управління файлом")
		frame2.set_label("Методи сортування")
		frame3.set_label("Резльтати останної дії")

		vbox.pack_start(frame1, True, True, 0)
		vbox.pack_start(frame2, True, True, 0)
		vbox.pack_start(frame3, True, True, 0)
		frame1.add(hbox1)
		frame2.add(hbox2)
		frame3.add(hbox3)

		buttonRandomize = Gtk.Button(label="Перезаповнити")
		buttonRandomize.connect("clicked", self.on_randomize_clicked)
		hbox1.pack_start(buttonRandomize, True, True, 10)
		buttonView = Gtk.Button(label="Продивитись вміст")
		buttonView.connect("clicked", self.on_show_file_clicked)
		hbox1.pack_start(buttonView, True, True, 10)
		buttonDelete = Gtk.Button(label="Видалити")
		buttonDelete.connect("clicked", self.on_delete_clicked)
		hbox1.pack_start(buttonDelete, True, True, 10)
		buttonExport = Gtk.Button(label="Експортувати")
		buttonExport.connect("clicked", self.on_export_clicked)
		hbox1.pack_start(buttonExport, True, True, 10)

		buttonSort1 = Gtk.Button(label="1. Природне злиття")
		buttonSort1.connect("clicked", self.on_sort1_clicked)
		hbox2.pack_start(buttonSort1, True, True, 10)
		buttonSort2 = Gtk.Button(label="2. Збалансоване багатошляхове злиття")
		buttonSort2.connect("clicked", self.on_sort2_clicked)
		hbox2.pack_start(buttonSort2, True, True, 10)
		buttonSort3 = Gtk.Button(label="3. Багатофазне сортування")
		buttonSort3.connect("clicked", self.on_sort3_clicked)
		hbox2.pack_start(buttonSort3, True, True, 10)

		resultLabel = Gtk.Label(label="Відсутні")
		hbox3.pack_start(resultLabel, True, True, 10)

		self.resultLabel = resultLabel

		# Прив'язка дії закриття кнопкою X
		self.connect("destroy", Gtk.main_quit)

		# Показ вікна та всіх елементів в ньому
		self.show_all()



	# Метод для видалення основного файлу у числами
	def on_delete_clicked(self, widget):
		# Перевірка чи вікно відкрите
		if self.viewWin:
			self.errorDialog("Дія заборонена", "Зміна файлу під час його перегляду заборонена")
		else:
			# Спробувати видалити файл, а за помилки видати повідомлення
			try:
				os.remove("numbers.bin")
			except IOError:
				self.errorDialog("Помилка!", "Не вдалося видалити файл.\nМожливо він відсутній?")



	# Метод для експорту чисел з файлу
	def on_export_clicked(self, widget):
		fBin = BinFile("numbers.bin")
		if fBin.ok:
			try:
				# Відкриття текстового файлу
				fTxt = open("numbers.txt","w")
				pos = 0

				# Прохід у циклі і додання по 1-му числу за кожну ітерацію
				while pos < fBin.size:
					fTxt.write(str(fBin.getInt32(pos))+"\n")
					pos += 4
			except:
				self.errorDialog("Помилка!", "Не вдалося відкрити файл numbers.txt")
		else:
			self.errorDialog("Помилка!", "Не вдалося відкрити файл numbers.bin")



	# Метод перезаповнення файлу випадковими числами
	def on_randomize_clicked(self, widget):
		if self.viewWin:
			self.errorDialog("Дія заборонена", "Зміна файлу під час його перегляду заборонена")
		else:
			outputs = self.multiPrompt("Заповнити файл",["Розмір","Від","До"],["32","0","10000"],[1, 0, 0],[16777216, 4294967295, 4294967295])

			if len(outputs) == 3:
				if outputs[1] > outputs[2]:
					self.errorDialog("Не вірне значення", "Значення 'Від' повинно бути меншим за значення 'До'")
				else:
					f = BinFile("numbers.bin", "wb")
					if f.ok:
						f.randomize(outputs[0], outputs[1], outputs[2])
						f.close()
						self.resultLabel.set_label("Файл заповнено "+str(outputs[0])+" числами зі\n значеннями від "+str(outputs[1])+" до "+str(outputs[2])+".")
					else:
						self.errorDialog("Помилка!", "Не вдалося відкрити файл")



	# Метод запуску першого сортування
	def on_sort1_clicked(self, widget):
		if self.viewWin:
			self.errorDialog("Дія заборонена", "Зміна файлу під час його перегляду заборонена")
		else:
			f = BinFile("numbers.bin")
			if f.ok:
				s = Sort1(f)
				s.sort()
				f.close()
				self.resultLabel.set_label(s.getResult())
			else:
				self.errorDialog("Помилка!", "Не вдалося відкрити файл, що повинен сортуватися.\nМожливо він відсутній?")



	# Метод запуску другого сортування
	def on_sort2_clicked(self, widget):
		if self.viewWin:
			self.errorDialog("Дія заборонена", "Зміна файлу під час його перегляду заборонена")
		else:
			outputs = self.multiPrompt("Збалансоване багатошляхове злиття", ["Кількість елементів в проміжку","Кількість файлів (буде x2)"],["4","4"],[1, 2],[65536, 65536])

			if len(outputs) == 2:
				f = BinFile("numbers.bin")
				if f.ok:
					s = Sort2(f, int(outputs[0]), int(outputs[1]))
					s.sort()
					f.close()
					self.resultLabel.set_label(s.getResult())
				else:
					self.errorDialog("Помилка!", "Не вдалося відкрити файл, що повинен сортуватися.\nМожливо він відсутній?")



	# Метод запуску третього сортування
	def on_sort3_clicked(self, widget):
		if self.viewWin:
			self.errorDialog("Дія заборонена", "Зміна файлу під час його перегляду заборонена")
		else:
			outputs = self.multiPrompt("Багатофазне сортування", ["Кількість елементів в проміжку","Кількість файлів"],["4","3"],[1, 3],[65536, 65536])

			if len(outputs) == 2:
				f = BinFile("numbers.bin")
				if f.ok:
					s = Sort3(f, int(outputs[0]), int(outputs[1]))
					s.sort()
					f.close()
					self.resultLabel.set_label(s.getResult())
				else:
					self.errorDialog("Помилка!", "Не вдалося відкрити файл, що повинен сортуватися.\nМожливо він відсутній?")



	# Метод відкриття вікна перегляду вмісту файлу
	def on_show_file_clicked(self, widget):
		if not self.viewWin:
			self.viewWin = ViewWindow(self)



	# Метод, що створює діалогове вікно з декількома зазначеними полями вводу, щщо приймають цілочисельні значення
	# Повертає масив чисел як відповідь
	# Повертає пустий масив при скасуванні
	# Кожне поле має дозволений проміжок, і якщо число не в ньому, видається помилка
	def multiPrompt(self, name, fields, defaults, valFrom, valTo):
		dialog = Gtk.Dialog(name, self, 0)
		dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

		hbox = Gtk.HBox()
		hbox.set_border_width(8)
		dialog.vbox.pack_start(hbox, False, False, 10)

		stock = Gtk.Image(stock=Gtk.STOCK_DIALOG_QUESTION, icon_size=Gtk.IconSize.DIALOG)
		hbox.pack_start(stock, False, False, 10)

		table = Gtk.Table(n_rows=len(fields), n_columns=2, row_spacing=4, column_spacing=4)
		hbox.pack_start(table, True, True, 0)

		# Створення зазначених полів та їх назв
		entries = []
		for i in range(len(fields)):
			label = Gtk.Label()
			label.set_label(fields[i])
			label.set_use_underline(True)
			table.attach(label, 0, 1, i, i+1)
			entry = Gtk.Entry()
			entry.set_text(defaults[i])
			table.attach(entry, 1, 2, i, i+1)
			label.set_mnemonic_widget(entry)
			entries.append(entry)

		dialog.show_all()

		response = dialog.run()
		output = []

		# Обробка відповідей
		if response == Gtk.ResponseType.OK:
			for entry in entries:
				text = entry.get_text()
				try:
					number = int(text)
					if number < valFrom[i]:
						self.errorDialog("Не вірне значення", "Введене число "+text+" є меншим за мінімально дозволене "+str(valFrom[i]))
						break
					elif number > valTo[i]:
						self.errorDialog("Не вірне значення", "Введене число "+text+" є більшим за максимально дозволене "+str(valTo[i]))
						break
					else:
						output.append(number)
				except:
					self.errorDialog("Не вірне значення", "Введене значення '"+text+"' не є цілим числом")
					break

		dialog.destroy()
		return output



	# Метод для створення вікон з повідомленнями про помилки
	def errorDialog(self, name, text):
		dialog = Gtk.Dialog(name, self, 0)
		dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK)

		hbox = Gtk.HBox()
		hbox.set_border_width(8)
		dialog.vbox.pack_start(hbox, False, False, 10)

		stock = Gtk.Image(stock=Gtk.STOCK_DIALOG_ERROR, icon_size=Gtk.IconSize.DIALOG)
		hbox.pack_start(stock, False, False, 10)

		label = Gtk.Label()
		label.set_label(text)
		label.set_use_underline(True)
		hbox.pack_start(label, True, True, 10)

		dialog.show_all()

		dialog.run()

		dialog.destroy()
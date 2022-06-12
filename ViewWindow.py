#!/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from BinFile import BinFile

class ViewWindow(Gtk.Window):
	def __init__(self, main):
		super().__init__(title="Вміст файлу")

		self.main = main

		# Відкриття переглядаємого файлу
		self.myFile = BinFile("numbers.bin")

		# Якщо не вдалося відкрити файл - вивід помилки і видалення вікна
		if not self.myFile.ok:
			self.main.viewWin = None
			self.main.errorDialog("Помилка","Не вдалося відкрити файл.\nМожливо він відсутній?")
			self.destroy()
			return

		self.page = 0
		self.maxPage = self.myFile.size // 4 // 1024

		# Заповнення вікна елементами
		self.set_default_size(width=480, height=360)

		table = Gtk.Table(n_rows=10, n_columns=5, row_spacing=4, column_spacing=4)
		self.add(table)

		textView = Gtk.TextView()
		sw = Gtk.ScrolledWindow()
		sw.add(textView)
		table.attach(sw, 0, 5, 0, 9)
		self.text_buffer = textView.get_buffer()

		self.buttonPrev = Gtk.Button(label="<")
		self.buttonPrev.connect("clicked", self.on_prev_page_clicked)
		table.attach(self.buttonPrev, 0, 1, 9, 10)
		self.buttonNext = Gtk.Button(label=">")
		self.buttonNext.connect("clicked", self.on_next_page_clicked)
		table.attach(self.buttonNext, 1, 2, 9, 10)
		self.pageEntry = Gtk.Entry()
		table.attach(self.pageEntry, 2, 3, 9, 10)
		buttonGo = Gtk.Button(label="Перейти")
		buttonGo.connect("clicked", self.on_go_to_page_clicked)
		table.attach(buttonGo, 3, 4, 9, 10)
		buttonClose = Gtk.Button(label="Закрити")
		buttonClose.connect("clicked", self.on_destroy_clicked)
		table.attach(buttonClose, 4, 5, 9, 10)

		# Задання правильного стану всім змінним елементам
		self.update_page()

		# Прив'язка дії при натисненні X
		self.connect("destroy", self.on_destroy_clicked)

		# Показ вікна
		self.show_all()



	# Функція переходу на введену сторінку
	def on_go_to_page_clicked(self, widget):
		# Зчитування введеної сторінки
		self.page = int(self.pageEntry.get_text())
		# Привід її значення до дозволеного проміжку
		if self.page < 0:
			self.page = 0
		if self.page > self.maxPage:
			self.page = self.maxPage

		# Задання правильного стану всім змінним елементам
		self.update_page()



	# Функція для задання правильного стану всім змінним елементам
	def update_page(self):
		values = self.myFile.getInts32(self.page*1024*4, 1024)
		string = "\n".join([str(x) for x in values])
		self.text_buffer.set_text(string)
		self.buttonPrev.set_sensitive(self.page > 0)
		self.buttonNext.set_sensitive(self.page < self.maxPage)
		self.pageEntry.set_text(str(self.page))



	# Якщо можливо, перехід на наступну сторінку
	def on_next_page_clicked(self, widget):
		if self.page < self.maxPage:
			self.page += 1
			self.update_page()



	# Якщо можливо, перехід на попередню сторінку
	def on_prev_page_clicked(self, widget):
		if self.page > 0:
			self.page -= 1
			self.update_page()



	# Знищення вікна
	def on_destroy_clicked(self, widget=None):
		self.main.viewWin = None
		self.hide()
		self.destroy()

#!/bin/env python3

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from BinFile import BinFile
from Sort1 import Sort1
from Sort2 import Sort2
from Sort3 import Sort3
from MainWindow import MainWindow

# Створення вікна та запуст GTK
def main():
	win = MainWindow()
	Gtk.main()

# Перевірка чи файл запущений як програма
if __name__ == "__main__":
	main()
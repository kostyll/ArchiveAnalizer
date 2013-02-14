# -*- coding: utf-8 -*-
# Сбор данных о файлах архива.


from PyQt4 import QtCore
import sqlite3

class ThrAnaliz(QtCore.QThread):
    """
    При возникновенни ошибки в процессе работы потока, заполняются переменные error и errorMessage.
    """

    archDisk = ""  # Диск с видео архивом.
    dirList = []  # Список директорий с архиами.
    error = False  # Ключ ошибки в работе программы.
    errorMessage = u""  # Сообщение об ошибки.

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        self.emit(QtCore.SIGNAL("progress2(QString)"), str(50))
        QtCore.QThread.sleep(2)





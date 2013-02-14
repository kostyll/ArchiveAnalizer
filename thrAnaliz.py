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
    logging = None  # Ссылка на логирование системы.
    error = False  # Ключ ошибки в работе программы.
    errorMessage = u""  # Сообщение об ошибки.

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def clean(self):
        """
        Очиска переменных для повторного использования.
        """
        self.archDisk = ""
        self.dirList = []
        self.error = False
        self.errorMessage = u""

    def run(self):
        #self.emit(QtCore.SIGNAL("progress2(QString)"), str(50))
        #QtCore.QThread.sleep(2)
        try:
            dbConnect =sqlite3.connect(":memory2:")
            dbCursor = dbConnect.cursor()
        except Exception, e:
            self.error = True
            self.errorMessage = u"Ошибка подключение к базе sqlite: %s" % e
        else:
            pass








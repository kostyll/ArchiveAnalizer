# -*- coding: utf-8 -*-
# Поток менеджера сбора данных об архиве.


from PyQt4 import QtCore
from thrAnaliz import ThrAnaliz

class ThrMng(QtCore.QThread):
    """
    При возникновенни ошибки в процессе работы потока, заполняются переменные error и errorMessage.
    """

    archDisk = ""  # Диск с видео архивом.
    dirList = []  # Список директорий с архиами.
    error = False  # Ключ ошибки в работе программы.
    errorMessage = u""  # Сообщение об ошибки.
    childProgress = 0  # Прогресс выполнения дочернего потока.

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.thrAnaliz = ThrAnaliz()  # Класс анализатора архива.
        self.connect(self.thrAnaliz, QtCore.SIGNAL("progress2(QString)"), self.progress2, QtCore.Qt.QueuedConnection)


    def progress2(self, num):
        """
        Слот для отслеживания прогресса дочернего потока.
        """
        self.childProgress = int(num)

    def run(self):
        # Обнуляем рабочие переменные.
        self.error = False
        self.errorMessage = u""
        self.emit(QtCore.SIGNAL("progress(QString)"), str(0))
        if not self.archDisk or not self.dirList:
            self.error = True
            self.errorMessage = u"Не заполнены обязательные переменные archDisk и dirList"
        else:
            self.emit(QtCore.SIGNAL("progress(QString)"), str(1))
            self.emit(QtCore.SIGNAL("information(QString)"), u"Сбор данных о файлах архива... ")
            self.thrAnaliz.start()
            self.thrAnaliz.wait()
            print "eWait"
            self.emit(QtCore.SIGNAL("progress(QString)"), str(self.childProgress))





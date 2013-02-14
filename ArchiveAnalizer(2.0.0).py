# -*- coding: utf-8 -*-
# Анализ архива ПО "Интеллект".
# Стерликов К. @ 2013


import sys
from ui.ui_main import Ui_main
from PyQt4 import QtCore, QtGui
from kstools import kssys, ksitv, ksqt
#import sqlite3
#import re
import logging
from thrMng import ThrMng


class main(QtGui.QMainWindow):
    """
    Класс основной формы
    """


    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_main()
        self.ui.setupUi(self)
        self.baseDir = kssys.getWorkPath()  # Рабочая директория программы.
        self.threadManager = ThrMng()  # Поток менеджера обработки данных.
        # Слоты.
        self.ui.pushButton_2.clicked.connect(self.clickOpenFileDialog)  # Диалог выбора файла.
        self.ui.pushButton_3.clicked.connect(self.clickProcess)  # Начало процесса создания отчетов.
        self.ui.pushButton_4.clicked.connect(self.clickClearFileLine)  # Очистка поля выбора внешнего файла.
        self.connect(self.threadManager, QtCore.SIGNAL("information(QString)"), self.addLogInform, QtCore.Qt.QueuedConnection)
        self.connect(self.threadManager, QtCore.SIGNAL("progress(QString)"), self.progress, QtCore.Qt.QueuedConnection)
        self.connect(self.threadManager, QtCore.SIGNAL("started()"), lambda: self.formDisabled(True))
        self.connect(self.threadManager, QtCore.SIGNAL("finished()"), self.finishProcess)

    def progress(self, num):
        """
        Установка прогресс бара.
        """
        self.ui.progressBar.setValue(int(num))
        self.ui.progressBar.repaint()

    def addLogInform(self, message):
        """
        Вывод сообщения в информационное окно.
        """
        self.ui.textEdit.append('<span style="color: #505050">%s</span>' % message)

    def addLogOk(self, message):
        """
        Вывод положительного результата в информационное окно.
        """
        self.ui.textEdit.append('<span style="color: #009100">%s</span>' % message)

    def addLogWarning(self, message):
        """
        Вывод предупреждения в информационное окно.
        """
        self.ui.textEdit.append('<span style="color: #919100">%s</span>' % message)

    def addLogError(self, message):
        """
        Вывод ошибки в информационное окно.
        """
        self.ui.textEdit.append('<span style="color: #910000">%s</span>' % message)

    def addLogCommand(self, command):
        """
        Команда для информационного окна.
        """
        if command == "clear":
            self.ui.textEdit.clear()
        else:
            raise ValueError(u"Передана необрабатываемая комманда.")

    def formDisabled(self, disabled=True):
        """
        Блокировка / разблокировка формы.
        """
        elements = (
            self.ui.pushButton,
            self.ui.pushButton_2,
            self.ui.pushButton_3,
            self.ui.pushButton_4,
            self.ui.checkBox,
            self.ui.checkBox_3,
            self.ui.radioButton,
            )
        for item in elements:
            if disabled:
                item.setDisabled(True)
            else:
                item.setEnabled(True)

    def clickClearFileLine(self):
        """
        Очистка пути к файлу с базой.
        """
        self.ui.lineEdit.setText(u"")

    def clickOpenFileDialog(self):
        """
        Диалог выбора файла с внешней базой данных.
        """
        self.formDisabled()
        dirName = "d:\\"
        fileName = QtGui.QFileDialog().getOpenFileName(self, u"Выберите .sql файл...", directory=dirName, filter="*.sql")
        if fileName:
            print fileName
            self.ui.lineEdit.setText(fileName)

    def clickProcess(self):
        """
        Начало процесса создания отчетов.

        ВНИМАНИЕ! Работает только для первого попавшегося диска с вдиое архивом.
        """
        i = self.addLogInform
        w = self.addLogWarning
        e = self.addLogError
        c = self.addLogCommand
        d = logging.debug
        c(u"clear")
        archDisks = ksitv.getArchiveDisks()  # Списки дисков с крхивами.
        if not archDisks:
            w(u"Не найдены жёсткие диски с видео-архивами.")
            ksqt.message(self, "warning", u"Внимание", u"Не найдены жёсткие диски с видео-архивами.")
        else:
            i(u"Обнаружены диски с архивами:  %s" % (", ".join(["%s:" % item for item in archDisks])))
            if len(archDisks) > 1:
                w(u"Обнаружено, что видео архив расположен на нескольких жестких дисках: %s<br>что не поддерживается в текущей версии программы." % (", ".join(["%s:" % item for item in archDisks])))
                ksqt.message(self, "warning", u"Внимание", u"Обнаружено, что видео архив расположен на нескольких жестких дисках: %s\nчто не поддерживается в текущей версии программы." % (", ".join(["%s:" % item for item in archDisks])))
            else:
                # Чтение всех директорий из указанных папок.
                archDisk = archDisks[0]  # Диск с архивом.
                dirList = ksitv.getArchiveFolder(archDisk)  # Список папок в архиве.
                if not dirList:
                    w(u"Видео архив пуст.")
                    ksqt.message(self, "inform", u"Информация", u"Видео архив пуст.")
                else:
                    # Запускаем менеджер обработки данных.
                    self.threadManager.clean()
                    self.threadManager.archDisk = archDisk
                    self.threadManager.dirList = dirList
                    self.threadManager.logging = logging
                    self.threadManager.start()


    def finishProcess(self):
        """
        Слот для окончания работы потока основного процесса.
        """
        if self.threadManager.error:
            self.addLogError(u"<b>%s</b>" % self.threadManager.errorMessage)
            ksqt.message(self, "error", u"Ошибка...", u"В процессе работы программы произошли ошибки:<br>%s" % self.threadManager.errorMessage)
        else:
            self.addLogOk(u"<b>Выполнено!</b>")
        self.formDisabled(False)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s')
    logging.debug(u"****** Начало новой сессии ******")
    app = QtGui.QApplication(sys.argv)
    myapp = main()
    myapp.show()
    try:
        sys.exit(app.exec_())
    except SystemExit:
        pass
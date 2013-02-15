# -*- coding: utf-8 -*-
# Сбор данных о файлах архива.


from PyQt4 import QtCore
from kstools import ksitv
import os

class ThrAnaliz(QtCore.QThread):
    """
    При возникновенни ошибки в процессе работы потока, заполняются переменные error и errorMessage.
    """

    archDisk = ""  # Диск с видео архивом.
    dirList = []  # Список директорий с архиами.
    #dbCursor = None  # Курсор на базу данных SqLite.
    logging = None  # Ссылка на логирование системы.
    error = False  # Ключ ошибки в работе программы.
    errorMessage = u""  # Сообщение об ошибки.
    chancel = False  # Ключ завершения работы потока.
    tableName = ""  # Имя таблицы базы данных.
    sqlQueue = None  # Очередь для добавления данных в БД.

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def errorMsg(self, message):
        """
        Формирование отчёта об ошибке и выход.
        """
        self.error = True
        self.errorMessage = message
        self.logging.debug(message)
        self.chancel = False
        exit()

    def clean(self):
        """
        Очиска переменных для повторного использования.
        """
        self.archDisk = ""
        self.dirList = []
        self.dbCursor = None
        self.error = False
        self.errorMessage = u""
        self.tableName = ""
        self.sqlQueue = None

    def run(self):
        # Чтение файлов в директория.
        cntFiles = len(self.dirList)  # Колличество директорий с архивами.
        self.emit(QtCore.SIGNAL("progress2(QString)"), str(0))
        if cntFiles:
            # Проходим по всем дисам с архивами:
            cntCurrent = 0  # Счетчик текущих обрабатываемых файлов.
            for archPath in self.dirList:  # Проход по папкам архива:
                for archFile in ksitv.getArchiveFiles("%s:\\VIDEO\\%s" % (self.archDisk, archPath)):  # Прохож по всем файлам в архиве:
                    fileFullPath = "%s:\\VIDEO\\%s\\%s" % (self.archDisk, archPath, archFile)  # Путь и имя файла.
                    sql = """
                        INSERT INTO
                            %s
                        VALUES
                            (
                                NULL,
                                '%s',
                                '%s',
                                '%s',
                                %s,
                                %s,
                                %s,
                                %s,
                                '%s',
                                '%s'
                            )
                    """ % (
                        self.tableName,
                        fileFullPath,
                        self.archDisk,
                        ksitv.getDateFromPath(archPath),
                        ksitv.getHourFromPath(archPath),
                        ksitv.getRecFromFileName(archFile),
                        ksitv.getCamFromFileName(archFile),
                        os.path.getsize(fileFullPath),
                        "",
                        ""
                    )
                    if self.chancel:
                        exit()
                    else:
                        self.sqlQueue(sql, block=True)
                        #self.emit(QtCore.SIGNAL("sql2(QString)"), sql)
                self.emit(QtCore.SIGNAL("progress2(QString)"), str(cntCurrent))
                cntCurrent += 1
            #self.emit(QtCore.SIGNAL("progress2(QString)"), str(100))








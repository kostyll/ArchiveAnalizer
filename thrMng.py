# -*- coding: utf-8 -*-
# Поток менеджера сбора данных об архиве.


from PyQt4 import QtCore
from thrAnaliz import ThrAnaliz
import sqlite3


class ThrMng(QtCore.QThread):
    """
    При возникновенни ошибки в процессе работы потока, заполняются переменные error и errorMessage.
    """

    mutex = QtCore.QMutex()
    archDisk = ""  # Диск с видео архивом.
    dirList = []  # Список директорий с архиами.
    logging = None  # Ссылка на логирование системы.
    error = False  # Ключ ошибки в работе программы.
    errorMessage = u""  # Сообщение об ошибки.
    childProgress = 0  # Прогресс выполнения дочернего потока.
    dbConnect = None  # Покдлючение к базе данных.
    dbCursos = None  # Текущий курсор базы данных.
    tableName = "archiv"  # Имя таблицы.
    addSqlError = False  # Ключ ошибки добавления в базу данных.

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.thrAnaliz = ThrAnaliz()  # Класс анализатора архива.
        self.connect(self.thrAnaliz, QtCore.SIGNAL("progress2(QString)"), self.progress2, QtCore.Qt.QueuedConnection)
        self.connect(self.thrAnaliz, QtCore.SIGNAL("sql2(QString)"), self.addSql)

    def progress2(self, num):
        """
        Слот для отслеживания прогресса дочернего потока.
        """
        self.childProgress = int(num)

    def addSql(self, sql):
        """
        Добавление винформации в базу даннх (для дочерних потоков).

        sql - готовый SQL запрос.
        """
        try:
            self.mutex.lock()
            self.dbCursor.execute(sql)
            self.dbConnect.commit()
        except Exception, e:
            self.thrAnaliz.chancel = True
            self.thrAnaliz.error = True
            self.thrAnaliz.errorMessage = u"Ошибка добавления данных в базу данных: %s" % e
        finally:
            self.mutex.unlock()

    def clean(self):
        """
        Очиска переменных для повторного использования.
        """
        self.archDisk = ""
        self.dirList = []
        self.error = False
        self.errorMessage = u""
        self.childProgress = 0
        self.dbConnect = None
        self.dbCursos = None
        self.addSqlError = False

    def errorMsg(self, message):
        """
        Формирование отчёта об ошибке и выход из потока.
        """
        self.error = True
        self.errorMessage = message
        self.logging.debug(message)
        if not self.dbConnect is None:
            self.dbConnect.close()
        #exit()

    def createTable(self, cursor, table_name):
        """
        Создание таюлицы в базе данных.

        Аргументы:
            cursor - текущий курсор в базе данных.
            table_name - имя очищаемой таблицы.
        """
        sql = """
            CREATE TABLE
                %s (
                    id INTEGER PRIMARY KEY,
                    file TEXT,
                    disk TEXT,
                    date TEXT,
                    hour INTEGER,
                    rec INTEGER,
                    cam INTEGER,
                    size INTEGER,
                    date_in_file TEXT,
                    time_in_file TEXT
                    )
            """ % table_name
        try:
            cursor.execute(sql)
            self.dbConnect.commit()
        except Exception:
            raise

    def getDbFileNameBackup(self):
        """
        Возвращает имя файла бэкаба база данных.
        """
        return "backup.sql"


    def run(self):
        self.emit(QtCore.SIGNAL("progress(QString)"), str(0))
        if not self.archDisk or not self.dirList:
            self.error = True
            self.errorMessage = u"Не заполнены обязательные переменные archDisk и dirList"
        else:
            # Подключение к базе данных.
            self.logging.debug(u"Connect db.")
            try:
                self.dbConnect =sqlite3.connect(":memory:")
                self.dbCursor = self.dbConnect.cursor()
                self.createTable(self.dbCursor, self.tableName)
            except Exception, e:
                self.errorMsg(u"Ошибка подключение к базе sqlite: %s" % unicode(e))
            else:
                tA = self.thrAnaliz  # Просто сокращение.
                # Запускаем поток анализа архива.
                self.emit(QtCore.SIGNAL("progress(QString)"), str(1))
                self.emit(QtCore.SIGNAL("information(QString)"), u"Сбор данных о файлах архива... ")
                self.logging.debug(u"START: ThrAnaliz")
                self.thrAnaliz.clean()
                self.thrAnaliz.archDisk = self.archDisk
                self.thrAnaliz.dirList = self.dirList
                self.thrAnaliz.logging = self.logging
                self.thrAnaliz.start()
                self.thrAnaliz.wait()
                QtCore.QThread.sleep(2)
                self.logging.debug(u"FINISH: ThrAnaliz")
                if tA.error:
                    self.errorMsg(tA.errorMessage)
                else:
                    # Создание бэкапа базы данных:
                    self.emit(QtCore.SIGNAL("information(QString)"), u"Создание бэкапа базы данных на диск... ")
                    self.logging.debug(u"START: DB backup")
                    try:
                        with open(self.getDbFileNameBackup(), 'w') as f:
                            for line in self.dbConnect.iterdump():
                                f.write('%s\n' % line)
                    except Exception, e:
                        self.errorMsg(u"Ошибка создания бэкапа базы данных: %s" % e)
                        exit()
                    self.emit(QtCore.SIGNAL("information(QString)"), u"  ...бэкап создан успешно и сохранён в %s." % self.getDbFileNameBackup())
                    self.logging.debug(u"FINISH: DB backup")
                self.dbConnect.close()





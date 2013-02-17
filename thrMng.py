# -*- coding: utf-8 -*-
# Поток менеджера сбора данных об архиве.


from PyQt4 import QtCore
import sqlite3
import Queue
from kstools import ksitv, ksprocent, ksfs
import os
import sys
import xlwt
import socket

class ThrMng(QtCore.QThread):
    """
    При возникновенни ошибки в процессе работы потока, заполняются переменные error и errorMessage.
    """

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.initialize()

    def initialize(self):
        """
        Очиска переменных для повторного использования.
        """
        self.tableName = ""  # Имя таблицы.
        self.cacheDir = ""  # Директория для кэширования.
        self.outDir = ""  # Диретория для выходных файлов.
        self.workDir = ""  # Рабочая директория.
        self.archDisk = ""  # Диск с видео архивом.
        self.dirList = []  # Список директорий с архиами.
        self.logging = None  # Ссылка на логирование системы.
        self.error = False  # Ключ ошибки в работе программы.
        self.errorMessage = u""  # Сообщение об ошибки.
        self.sqlQueue = Queue.Queue()  # Очередь для добавления данных в БД.
        self.chancel = False  # Ключ принудительной остановки работы потока.
        self.report = []  # Списо отчетов.
        self.normalExit = False  # Ключ нормального выхода из потока.
        self.cacheFile = ""  # Файл из кэша.
        self.runAfterComplete = False  # Запустить после формирования отчета.

    def errorMsg(self, message):
        """
        Формирование отчёта об ошибке и выход из потока.
        """
        self.emit(QtCore.SIGNAL("progress(QString)"), str(100))
        self.error = True
        self.errorMessage = message
        self.logging.debug(message)
        if not self.dbConnect is None:
            self.dbConnect.close()

    def deleteTable(self, cursor, name):
        """
        Удаление указанной таблицы, если она существует.

        Аргументы:
            cursor - текущий курсор в базе данных.
            name - имя очищаемой таблицы.
        """
        sql = """
            DROP TABLE
            IF EXISTS
            %s;
        """ % name
        try:
            cursor.execute(sql)
        except Exception:
            raise

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
        except Exception:
            raise

    def getDbFileNameBackup(self):
        """
        Возвращает имя файла бэкаба база данных.
        """
        return "%s/%s/%s_backup.sql" % (self.workDir, self.cacheDir, socket.gethostname())

    def getReportXlsFileName(self, postFix=""):
        """
        Возвращает имя xls файла.
        """
        return "%s/%s/%s.xls" % (self.workDir, self.outDir, socket.gethostname())

    def getCamList(self, dbCursor):
        """
        Возвращает список камер из базы данных.

        Вовращает:
            (list) - списко идентификаторов камер.
        """
        sql = """
            SELECT
                cam
            FROM
                %s
            GROUP BY
                cam
        """ % self.tableName
        data = []
        try:
            for row in dbCursor.execute(sql):
                data.append(row)
        except Exception, e:
            self.errorMsg(u"Ошибка добавления данных в базу данных: %s" % unicode(e))
            sys.exit()
        result = [x[0] for x in data]
        result.sort()
        return result

    def getDays(self, dbCursor):
        """
        Возвращает список всех дат с архивами.
        """
        result = []
        sql = "SELECT date FROM %s GROUP BY date ORDER BY date" % self.tableName
        try:
            for row in dbCursor.execute(sql):
                result.append(row[0])
        except Exception, e:
            self.errorMsg(u"Ошибка запроса к базе данных: %s" % unicode(e))
            sys.exit()
        return sorted(result)

    def getSizeInDay(self, dbCursor):
        """
        Возвращает размер всез записей за все даты.
        """
        result = {}
        sql = 'SELECT date, SUM(size) FROM %s GROUP BY date ORDER BY date' % self.tableName
        try:
            for row in dbCursor.execute(sql):
                date, size = row
                result[date] = size
        except Exception, e:
            self.errorMsg(u"Ошибка запроса к базе данных: %s" % unicode(e))
            sys.exit()
        return result

    def getSizeInHour(self, dbCursor, date, hour):
        """
        Возвращает список камер и размер записей за указанный час.
        """
        result = {}
        sql = 'SELECT cam, SUM(size) FROM %s WHERE date="%s" AND hour=%s GROUP BY cam' % (self.tableName, date, hour)
        try:
            for row in dbCursor.execute(sql):
                cam, size = row
                result[cam] = size
        except Exception, e:
            self.errorMsg(u"Ошибка запроса к базе данных: %s" % unicode(e))
            sys.exit()
        return result

    def getCamSizeOnDay(self, dbCursor, date):
        """
        Возвращает словарь с ключами в виде камер, и значением в виде общего размера в байтах за указанную дату.
        """
        result = {}
        sql = 'SELECT cam, SUM(size) FROM %s WHERE date = "%s" GROUP BY cam' % (self.tableName, date)
        try:
            for row in dbCursor.execute(sql):
                cam, size = row
                result[cam] = size
        except Exception, e:
            self.errorMsg(u"Ошибка запроса к базе данных: %s" % unicode(e))
            sys.exit()
        return result

    def run(self):
        self.logging.debug(u"START: ThrMng")
        curProcent = 0
        self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
        if not self.archDisk or not self.dirList:
            self.error = True
            self.errorMessage = u"Не заполнены обязательные переменные archDisk и dirList"
        else:
            # Подключение к базе данных.
            self.logging.debug(u"Connect db.")
            try:
                dbConnect =sqlite3.connect(":memory:")
                dbCursor = dbConnect.cursor()
                self.deleteTable(dbCursor, self.tableName)
            except Exception, e:
                self.errorMsg(u"Ошибка подключение к базе sqlite: %s" % unicode(e))
                sys.exit()
            else:
                if self.cacheFile and os.path.exists(self.cacheFile):
                    # Восстановление базы из кэша.
                    self.emit(QtCore.SIGNAL("information(QString)"), u"Восстановление из базы %s... " % self.cacheFile)
                    try:
                        f = open(self.cacheFile, "r")
                        fContent = f.read()
                        dbCursor.executescript(fContent)
                        dbConnect.commit()
                    except Exception, e:
                        self.errorMsg(u"Ошибка создания бэкапа базы данных: %s\n%s" % (self.cacheFile, e))
                        sys.exit()
                    self.emit(QtCore.SIGNAL("information(QString)"), u"&nbsp;&nbsp;&nbsp;...восстановлено.")
                else:
                    # Создание новой базы данных.
                    self.createTable(dbCursor, self.tableName)
                    curProcent = 1  # Текущий процент выполненных действий.
                    oldProcent = curProcent  # Предыдущий процент (для уменьшения подачи заявлений на изменение процента)
                    self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                    self.emit(QtCore.SIGNAL("information(QString)"), u"Сбор данных о файлах архива... ")
                    cntFiles = len(self.dirList)  # Колличество директорий с архивами.
                    if not cntFiles:
                        self.errorMsg(u"Архив пуст.")
                    else:
                        self.emit(QtCore.SIGNAL("information(QString)"), u"Обнаружено директорий с архивом: %s" % cntFiles)
                        self.emit(QtCore.SIGNAL("information(QString)"), u"Создание базы данных из видео архива... ")
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
                                    "",
                                    )
                                if self.chancel:
                                    self.errorMsg(u"Прервано пользователем.")
                                    sys.exit()
                                else:
                                    try:
                                        dbCursor.execute(sql)
                                    except Exception, e:
                                        self.errorMsg(u"Ошибка добавления данных в базу данных: %s" % unicode(e))
                                        sys.exit()
                            curProcent = ksprocent.getRelative(cntCurrent, cntFiles, 1, 80)
                            if curProcent != oldProcent:
                                oldProcent = curProcent
                                self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                            cntCurrent += 1
                        curProcent = 80
                        self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                        self.emit(QtCore.SIGNAL("information(QString)"), u"&nbsp;&nbsp;&nbsp;... создано.")
                        # Создание бэкапа базы данных:
                        self.emit(QtCore.SIGNAL("information(QString)"), u"Создание бэкапа базы данных на диск... ")
                        self.logging.debug(u"START: DB backup")
                        try:
                            path = self.getDbFileNameBackup()
                            if not os.path.exists(path):
                                os.mkdir(os.path.dirname(path))
                            with open(path, 'w') as f:
                                for line in dbConnect.iterdump():
                                    f.write('%s\n' % line)
                        except Exception, e:
                            self.errorMsg(u"Ошибка создания бэкапа базы данных: %s" % e)
                            sys.exit()
                        self.emit(QtCore.SIGNAL("information(QString)"), u"&nbsp;&nbsp;&nbsp;...бэкап создан успешно и сохранён в %s." % self.getDbFileNameBackup())
                        self.logging.debug(u"FINISH: DB backup")
                        curProcent = 85
                        self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                # Формирование отчётов:
                curProcent = 85
                self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                wb = xlwt.Workbook()
                if "all_day" in self.report: # Отчет за все камеры в день:
                    self.logging.debug(u"START: report all_day")
                    self.emit(QtCore.SIGNAL("information(QString)"), u"Создание отчета за дни... ")
                    ws = wb.add_sheet('Daily report')
                    row, col = 0, 0
                    # Формирование заголовка:
                    ws.write(row, col, "Day")
                    col += 1
                    ws.write(row, col, "Size Mb")
                    row += 1
                    # Формирование отчета:
                    sizeInDays = self.getSizeInDay(dbCursor)
                    for day in self.getDays(dbCursor):  # Проходим по каждому дню:
                        col = 0
                        ws.write(row, col, day)
                        col =+ 1
                        ws.write(row, col, ksfs.getNumberFormat(sizeInDays[day], "mb"))
                        row += 1
                    self.logging.debug(u"FINISH: report all_day")
                    self.emit(QtCore.SIGNAL("information(QString)"), u"&nbsp;&nbsp;&nbsp;... создан.")
                    curProcent = 88
                    self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                if "cam_in_day" in self.report: # Отчёт по каждой камере за день:
                    self.logging.debug(u"START: report Cam in day")
                    self.emit(QtCore.SIGNAL("information(QString)"), u"Создание отчета по камерам за дени... ")
                    ws = wb.add_sheet('Cam in day')
                    row, col = 0, 1
                    # Формирование заголовка:
                    cams = self.getCamList(dbCursor)
                    for cam in cams:
                        ws.write(row, col, cam)
                        col += 1
                    row += 1
                    # Формирование таблицы по дням.
                    for day in self.getDays(dbCursor):  # Проходим по каждому дню:
                        size = self.getCamSizeOnDay(dbCursor, day)  # Словарь размеров записей с камеры за дату.
                        col = 0
                        ws.write(row, col, day)
                        col += 1
                        for cam in cams:
                            ws.write(row, col, ksfs.getNumberFormat(size[cam], "mb"))
                            col += 1
                        row += 1
                    self.logging.debug(u"FINISH: report Cam in day")
                    self.emit(QtCore.SIGNAL("information(QString)"), u"&nbsp;&nbsp;&nbsp;... создан.")
                    curProcent = 90
                    self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                if "cam_in_hour" in self.report:  # Отчет по казждому часу:
                    self.logging.debug(u"START: report Cam in hour")
                    self.emit(QtCore.SIGNAL("information(QString)"), u"Создание отчета по камерам за часы... ")
                    days = self.getDays(dbCursor)  # Даты с архивом.
                    cams = self.getCamList(dbCursor)  # Список камер.
                    ws = wb.add_sheet('Cam in hour')
                    row, col = 0, 1
                    # Формирование заголовка:
                    for cam in cams:
                        ws.write(row, col, cam)
                        col += 1
                    row += 1
                    # Формирование каркаса для формирования отчета:
                    resultTable = {}  # Таблица в памяти.
                    for day in days:  # Проход по дням:
                        resultTable[day] = {}
                        for hour in range(0, 24):  # Проход по часам:
                            resultTable[day][hour] = {}
                            for cam in cams:  # Прозод по камерам:
                                resultTable[day][hour][cam] = None
                    # Формирование результата:
                    for date in resultTable.keys():  # Проход по дамам:
                        for hour in resultTable[date].keys():  # Проход по часам:
                            sizeInHour = self.getSizeInHour(dbCursor, date, hour)
                            for req in sizeInHour.keys():
                                resultTable[date][hour][req] = sizeInHour[req]
                    # Сохранение результата:
                    for date in sorted(resultTable.keys()):  # Проход по дамам:
                        for hour in sorted(resultTable[date].keys()):  # Проход по часам:
                            col = 0
                            ws.write(row, col, "%s %s:00" % (date, hour))
                            col += 1
                            for cam in sorted(resultTable[date][hour].keys()):
                                ws.write(row, col, ksfs.getNumberFormat(resultTable[date][hour][cam], "mb"))
                                col += 1
                            row += 1
                    self.logging.debug(u"FINISH: report Cam in hour")
                    self.emit(QtCore.SIGNAL("information(QString)"), u"&nbsp;&nbsp;&nbsp;... создан.")
                    curProcent = 99
                    self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                try:
                    wb.save(self.getReportXlsFileName())
                except Exception, e:
                    self.errorMsg(u"Ошибка сохранения файла: %s" % e)
                    sys.exit()
                curProcent = 100
                self.emit(QtCore.SIGNAL("progress(QString)"), str(curProcent))
                # Просмотреть отчёт:
                if self.runAfterComplete:
                    os.system(self.getReportXlsFileName())
            dbConnect.close()
            self.logging.debug(u"FINISH: ThrMgr")
            self.normalExit = True





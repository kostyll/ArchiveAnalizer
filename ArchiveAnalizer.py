# -*- coding: utf-8 -*-
# Анализ архива ПО "Интеллект".
# Стерликов К. @ 2013


import sys
import os
from ui.ui_main import Ui_main
from PyQt4 import QtCore, QtGui
from kstools import kssys, ksitv, ksqt, ksconfig, ksenv
import logging
from thrMng import ThrMng
import lya


class main(QtGui.QMainWindow):
    """
    Класс основной формы
    """
    cfgVersion = "2.0.1"
    cfgYaer = "2013"
    cfgDefaultFileName = "cfg_default.yaml"  # Имя файла конфигурации по умолчанию.
    cfgUserFilename = "cfg_user.yaml"  # Имя фалйа конфигурации пользоателя по умолчанию.

#    tableName = "archiv"  # Имя таблицы.
#    cacheDir = "cache"  # Директория для кэширования.
#    outDir = "out"  # Диретория для выходных файлов.
#    cacheFile = ""  # Имя фафйла с резервной копией базы данных.
    isProcess = False  # Программа находится в процессе работы.
    # Иконка заголовка окнна:
#    configDefault = {  # Конфигурация программы по умолчанию.
#        "report_in_day": True,
#        "report_cam_in_day": True,
#        "report_cam_in_hour": True,
#        "backup_file": "",
#        "exec_after_create": True,
#    }

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_main()
        self.ui.setupUi(self)
        self.baseDir = kssys.getWorkPath()  # Рабочая директория программы.
        self.threadManager = ThrMng()  # Поток менеджера обработки данных.
        # Слоты.
        self.ui.pushButton.clicked.connect(self.clickOpenCacheFolder)  # Открытие папки с кэшэм базы.
        self.ui.pushButton_2.clicked.connect(self.clickOpenFileDialog)  # Диалог выбора файла.
        self.ui.pushButton_3.clicked.connect(self.clickProcess)  # Начало процесса создания отчетов.
        self.ui.pushButton_4.clicked.connect(self.clickClearFileLine)  # Очистка поля выбора внешнего файла.
        self.ui.pushButton_5.clicked.connect(self.clickOpenOutFolder)  # Открытие папки с выходными файлами.
        self.ui.action.triggered.connect(self.clickAbout)  # Информация о прогремме.
        self.ui.action_Qt.triggered.connect(self.clickAboutQt)  # Информация о Qt.
        self.connect(self.threadManager, QtCore.SIGNAL("information(QString)"), self.addLogInform, QtCore.Qt.QueuedConnection)
        self.connect(self.threadManager, QtCore.SIGNAL("progress(QString)"), self.progress, QtCore.Qt.QueuedConnection)
        self.connect(self.threadManager, QtCore.SIGNAL("started()"), lambda: self.formDisabled(True))
        self.connect(self.threadManager, QtCore.SIGNAL("finished()"), self.finishProcess)

        # Ищем конфиг по умолчанию в теущей папке (если нет завершаем работу программы). Ищем пользовательские настройки и
        # наклаываем их на дефаултные.
        try:
            self.cfg = lya.AttrDict.from_yaml(os.path.join(self.baseDir, self.cfgDefaultFileName))
        except IOError, e:
            self.errorMsgCritical(unicode(e.__str__(), "cp1251"))
        else:
            try:
                self.cfg.update_yaml(os.path.join(ksenv.getLocalAppDataPath(), self.cfg.main.dir.app_dir, self.cfgUserFilename))
            except IOError, e:
                logging.error(u"Не удалось прочитать файл пользовательской конфигурации: %s" % unicode(e.__str__(), "cp1251"))
                pass
        self.configToForm()
        # Создание рабочих папок.
        # Кэш созраняется в %ALLUSERSPROFILE%, выходная директория создаётся в "моих документах".
        try:
            dirs = (
                os.path.join(ksenv.getLocalAppDataPath(), self.cfg.main.dir.app_dir),
                os.path.join(ksenv.getAllUsersProfile(), self.cfg.main.dir.app_dir),
                os.path.join(ksenv.getLocationInQt("documents"), self.cfg.main.dir.app_dir),
            )
            for dir in dirs:
                if not os.path.exists(dir):
                    os.mkdir(dir)
        except Exception, e:
            self.errorMsgCritical((u"Невозможно создать директорию.", unicode(e.__str__(), 'cp1251',)))

    def clickAbout(self):
        """
        Информация о программе.
        """
        QtGui.QMessageBox.information(
            self,
            u"О программе...",
u"""
<b>Анализатор видео архива ПО «Интеллект» версии %s</b>
<br>
Автор: Стерликов К.С. @ %s
""" % (self.cfgVersion, self.cfgYaer),
            QtGui.QMessageBox.Information
        )

    def clickAboutQt(self):
        """
        Информация о программе.
        """
        QtGui.QMessageBox.aboutQt(self)


    def clickOpenCacheFolder(self):
        """
        Открыть папку с кэшем.
        """
        path = os.path.join(ksenv.getAllUsersProfile(), self.cfg.main.dir.app_dir)
        try:
            os.startfile(path)
        except Exception, e:
            print e
            self.errorMsg((u"Не удаётся открыть папку с кэшем базы архива", unicode(e.__str__(), "cp1251"),))

    def clickOpenOutFolder(self):
        """
        Открыть папку с выходными файлами.
        """
        path = os.path.join(ksenv.getLocationInQt("documents"), self.cfg.main.dir.app_dir)
        try:
            os.startfile(path)
        except Exception, e:
            self.errorMsg((u"Не удаётся открыть папку с отчётами.", unicode(e.__str__(), "cp1251"),))

    def closeEvent(self, *args, **kwargs):
        """
        Переопределяем событие выхода из формы.
        """
        self.configToFile()
        QtGui.QWidget.closeEvent(self, *args, **kwargs)

    def configToForm(self):
        """
        Установка параметров формы в зависимости от конфигурации.
        """
        self.ui.checkBox_2.setChecked(self.cfg.main.report.in_day)
        self.ui.checkBox.setChecked(self.cfg.main.report.cam_in_day)
        self.ui.checkBox_3.setChecked(self.cfg.main.report.cam_in_hour)
        self.ui.checkBox_4.setChecked(self.cfg.main.triggers.exec_after_create)
        self.ui.checkBox_5.setChecked(self.cfg.main.triggers.each_create_new_cache)
        if len(self.cfg.main.backup.file) and os.path.exists(self.cfg.main.backup.file):
            self.ui.lineEdit.setText(self.cfg.main.backup.file)

    def configToFile(self):
        """
        Сохранение и сохранение текущего значения конфигурации на диск.
        """
        self.cfg.main.report.in_day = self.ui.checkBox_2.checkState() == QtCore.Qt.Checked
        self.cfg.main.report.cam_in_day = self.ui.checkBox.checkState() == QtCore.Qt.Checked
        self.cfg.main.report.cam_in_hour = self.ui.checkBox_3.checkState() == QtCore.Qt.Checked
        self.cfg.main.triggers.exec_after_create = self.ui.checkBox_4.checkState() == QtCore.Qt.Checked
        self.cfg.main.triggers.each_create_new_cache = self.ui.checkBox_5.checkState() == QtCore.Qt.Checked
        self.cfg.main.backup.file = unicode(self.ui.lineEdit.text())
        try:
            f = open(os.path.join(ksenv.getLocalAppDataPath(), self.cfg.main.dir.app_dir, self.cfgUserFilename), "w")
            self.cfg.dump(f)
        except Exception, e:
            self.errorMsg((u"Невозможно сохранить конфигурацию программы", unicode(e.__str__(), "cp1251"),))

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
            self.ui.pushButton_4,
            self.ui.pushButton_5,
            self.ui.checkBox,
            self.ui.checkBox_2,
            self.ui.checkBox_3,
            )
        for item in elements:
            if disabled:
                item.setDisabled(True)
            else:
                item.setEnabled(True)
        self.ui.pushButton_3.setEnabled(True)
        if disabled:
            self.ui.pushButton_3.setText(u"Остановить")
        else:
            self.ui.pushButton_3.setText(u"Сформировать")

    def clickClearFileLine(self):
        """
        Очистка пути к файлу с базой.
        """
        self.ui.lineEdit.setText(u"")
        self.cacheFile = ""

    def clickOpenFileDialog(self):
        """
        Диалог выбора файла с внешней базой данных.
        """
        dirName = os.path.join(ksenv.getAllUsersProfile(), self.cfg.main.dir.app_dir)
        fileName = QtGui.QFileDialog().getOpenFileName(self, u"Выберите .sql файл...", directory=dirName, filter="*.sql")
        if fileName:
            self.ui.lineEdit.setText(fileName)
            self.cacheFile = fileName

    def clickProcess(self):
        """
        Начало процесса создания отчетов.

        ВНИМАНИЕ! Работает только для первого попавшегося диска с вдиое архивом.
        """
        if self.isProcess:  # Поток находится в процессе работы:
            self.threadManager.chancel = True
            self.ui.pushButton_3.setDisabled(True)
        else:
            self.addLogCommand(u"clear")
            archDisks = ksitv.getArchiveDisks()  # Списки дисков с крхивами.
            if not archDisks:
                self.addLogWarning(u"Не найдены жёсткие диски с видео-архивами.")
                ksqt.message(self, "warning", u"Внимание...", u"Не найдены жёсткие диски с видео-архивами.")
            else:
                self.addLogInform(u"Обнаружены диски с архивами:  %s" % (", ".join(["%s:" % item for item in archDisks])))
                if len(archDisks) > 1:
                    self.addLogWarning(u"Обнаружено, что видео архив расположен на нескольких жестких дисках: %s<br>что не поддерживается в текущей версии программы." % (", ".join(["%s:" % item for item in archDisks])))
                    ksqt.message(self, "warning", u"Внимание...", u"Обнаружено, что видео архив расположен на нескольких жестких дисках: %s\nчто не поддерживается в текущей версии программы." % (", ".join(["%s:" % item for item in archDisks])))
                else:
                    # Чтение всех директорий из указанных папок.
                    archDisk = archDisks[0]  # Диск с архивом.
                    dirList = ksitv.getArchiveFolder(archDisk)  # Список папок в архиве.
                    if not dirList:
                        self.addLogWarning(u"Видео архив пуст.")
                        ksqt.message(self, "inform", u"Информация...", u"Видео архив пуст.")
                    else:
                        # Запускаем менеджер обработки данных.
                        self.threadManager.initialize()
                        self.threadManager.archDisk = archDisk
                        self.threadManager.dirList = dirList
                        self.threadManager.logging = logging
                        self.threadManager.cfg = self.cfg
                        self.threadManager.workDir = self.baseDir
                        #self.threadManager.tableName = self.tableName
                        #self.threadManager.cacheDir = self.cacheDir
                        #self.threadManager.outDir = self.outDir

                        if unicode(self.ui.lineEdit.text()) and os.path.exists(unicode(self.ui.lineEdit.text())):
                            self.threadManager.cacheFile = unicode(self.ui.lineEdit.text())
                        if self.ui.checkBox_4.checkState() == QtCore.Qt.Checked:
                            self.threadManager.runAfterComplete = True
                        checked = 0  # Колличество выбранныз отчетов.
                        if self.ui.checkBox_2.checkState() == QtCore.Qt.Checked:
                            self.threadManager.report.append("all_day")
                            checked += 1
                        if self.ui.checkBox.checkState() == QtCore.Qt.Checked:
                            self.threadManager.report.append("cam_in_day")
                            checked += 1
                        if self.ui.checkBox_3.checkState() == QtCore.Qt.Checked:
                            self.threadManager.report.append("cam_in_hour")
                            checked += 1
                        if not checked:
                            ksqt.message(self, "warning", u"Внимание...", u"Необходимо выбрать хотя бы один отчёт.")
                        else:
                            self.threadManager.start()
                            self.isProcess = True

    def finishProcess(self):
        """
        Слот для окончания работы потока основного процесса.
        """
        self.progress(100)
        if self.threadManager.error:
            self.addLogError(u"<b>%s</b>" % self.threadManager.errorMessage)
            ksqt.message(self, "error", u"Ошибка...", u"В процессе работы программы произошли ошибки:<br>%s" % self.threadManager.errorMessage)
        else:
            if not self.threadManager.normalExit:
                self.addLogError(u"<b>Некорректное завершение работы программы.</b>")
            else:
                self.addLogOk(u"<b>Выполнено!</b>")
        self.formDisabled(False)
        self.isProcess = False

    def errorMsg(self, message):
        """
        Формирование отчёта об ошибке.
        """
        if isinstance(message, list) or isinstance(message, tuple):
            logging.debug("ERROR: %s" % "; ".join(message))
            message = u"<ul><li>%s</li></ul>" % u"</li><li>".join(message)
        else:
            logging.debug("ERROR: %s" % message)
            message = u"<ul><li>%s</li></ul>" %  message
        ksqt.message(self, "error", u"Ошибка...", u"В процессе работы программы произошли ошибки:%s" % message)

    def errorMsgCritical(self, message):
        """
        Формирование отчёта об ошибке и выход из программы.
        """
        if isinstance(message, list) or isinstance(message, tuple):
            logging.debug("CRITICAL: %s" % "; ".join(message))
            message = u"<ul><li>%s</li></ul>" % u"</li><li>".join(message)
        else:
            logging.debug("CRITICAL: %s" % message)
            message = u"<ul><li>%s</li></ul>" %  message
        ksqt.message(self, "error", u"Ошибка...", u"В процессе работы программы произошли ошибки:%s<b>Работа программы остановлена!</b>" % message)
        sys.exit(1)



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
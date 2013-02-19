# -*- coding: utf-8 -*-
# Работа с корфигурацией сохраняемой на диск.
# v. 1.0.0 2013.02.19

from configobj import ConfigObj
import logging


class KsConfig():


    config = None  # Объект с конфигурацией.


    def __init__(self, workPath, fileName, configDefault, load=False):
        """
        workPath - абсолютняй путь к файлу конфигурации.
        fileName - имя файла конфигурации.
        configDefault - слофарь с конфигруацией по умолчанию
            {
                "address_remote": "8.8.8.8",
                "sleep": 2,
                ...
            }
        load - произвести ли автоматическую загрузку текущей конфигурации.
        """
        self.workPath = workPath  # Путь к рабочей директории.
        self.fileName = fileName  # Имя файла конфигурации.
        self.configDefault = configDefault  # Конфигурация по умолчанию.
        if load:
            self.load()

    def _check(self):
        """
        Проверяет корркетность работы с конфигурацией, такие как наличие конфигурации,
        корректность вводимых данных.
        """
        if self.config is None:
            raise Exception(u"Невозможно сохранить конфигурацию, т.к. она не загружена или создана.")

    def load(self):
        """
        Загрузка конфигурации из файла или, если файл конфигурации отсутсвует, создаётся
        новая.
        """
        self.config = ConfigObj("%s/%s" % (self.workPath, self.fileName), encoding="utf-8")
        for key in self.configDefault.keys():
            if not key in self.config:
                self.config[key] = self.configDefault[key]
            else:
                if type(self.configDefault[key]) is int:
                    self.config[key] = int(self.config[key])
                elif type(self.configDefault[key]) is float:
                    self.config[key] = float(self.config[key])
                elif type(self.configDefault[key]) is bool:
                    if self.config[key] == u"True":
                        self.config[key] = True
                    else:
                        self.config[key] = False
                elif type(self.configDefault[key]) is unicode:
                    self.config[key] = unicode(self.config[key])
                elif type(self.configDefault[key]) is str:
                    self.config[key] = str(self.config[key])

    def save(self):
        """
        Сохранение конфигурации на диск. Если конфигурация не создана, этот шаг просто пропускается.
        """
        if self.config:
            self.config.write()
        else:
            logging.warning(u"Попытка сохранить конфигурацию, которая ещё не создана.")

    def get(self, key):
        """
        Возвращает значение конфигруации по ключу.
        """
        self._check()
        return self.config[key]

    def set(self, key, value):
        """
        Устанавливает значение конфигруации.
        """
        self._check()
        self.config[key] = value
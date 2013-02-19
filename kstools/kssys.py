# -*- coding: utf-8 -*-
# Список системных утилит.
# v. 1.0.0 2013.02.19


import sys
import os


def getWorkPath():
    """
    Возвращает путь к рабочей директории скрипта (без завершающего слеша).
    """
    return os.path.realpath(os.path.dirname(sys.argv[0]))


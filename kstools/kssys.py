# -*- coding: utf-8 -*-
# Список системных утилит.


import sys
import os


def getWorkPath():
    """
    Возвращает путь к рабочей директории скрипта (без завершающего слеша).
    """
    return os.path.realpath(os.path.dirname(sys.argv[0]))


# -*- coding: utf-8 -*-
# Список системных утилит.
# v. 1.1.0 2013.02.19


import sys
import os


def getWorkPath():
    """
    Возвращает путь к рабочей директории скрипта (без завершающего слеша).
    """
    return os.path.realpath(os.path.dirname(sys.argv[0]))

def getWindowsVersion():
    """ Возвращаем версию ОС Windows

    Возвращает:
        (string) версия ОС Windows:
            ...
            4.0 - Windows NT 4.0
            5.0 - Windows 2000
            5.1 - Windows XP
            5.2 - Windows Server 2003
            6.0 - Windows Vista
            6.1 - Windows 7, Windows Server 2008 R2,
            6.2 - Windows 8
    """
    return "%s.%s" % (sys.getwindowsversion().major, sys.getwindowsversion().minor)




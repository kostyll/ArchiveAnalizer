# -*- coding: utf-8 -*-
# Работа с переменными окружения.
# v. 1.0.0 2013.02.20
#
# Для получения путей к настройкам программы в ОС Windows:
#
# getAppDataPath() - для перемещаемых настроек конкретного пользователя.
# getLocalAppDataPath() - для неперемещаемых настроек конкретного пользователя.
# getAllUsersProfile() - для неперемещаемых настроек всех пользователей.


import os
import kssys


def getAppDataPath():
    """
    Путь к папке с перемещаемыми пользовательскими настройками.
    """
    wv = kssys.getWindowsVersion()
    if wv in ("5.0", "5.1", "5.2"):
        result = os.getenv("APPDATA")
    elif wv in ("6.0", "6.1", "6.2"):
        result = os.getenv("APPDATA")
    else:
        raise ValueError(u"Неопддерживаемая версия Windows %s" % wv)
    return result

def getLocalAppDataPath():
    """
    Путь к папке с НЕперемещаемыми пользовательскими настройками.
    """
    wv = kssys.getWindowsVersion()
    if wv in ("5.0", "5.1", "5.2"):
        result = "%s\\Local Settings\Application Data" % os.getenv("USERPROFILE")
    elif wv in ("6.0", "6.1", "6.2"):
        result = os.getenv("LOCALAPPDATA")
    else:
        raise ValueError(u"Неопддерживаемая версия Windows %s" % wv)
    return result

def getAllUsersProfile():
    """
    Путь к общим настройкам всех пользователей.
    """
    wv = kssys.getWindowsVersion()
    if wv in ("5.0", "5.1", "5.2"):
        result = "%s\\Application Data" % os.getenv("ALLUSERSPROFILE")
    elif wv in ("6.0", "6.1", "6.2"):
        result = os.getenv("ALLUSERSPROFILE")
    else:
        raise ValueError(u"Неопддерживаемая версия Windows %s" % wv)
    return result

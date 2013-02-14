# -*- coding: utf-8 -*-
# Работа с директориями.


import os
import shutil
from win32com.client import GetObject
import kstools


def copyTree(src, dst):
    """
    Рекурсивное копирование директории.

    :param src: директория источника
    :param dst: директория назначения.
    :return:
    """
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copyTree(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
        except Exception:
            raise

def convertBytes(bytes):
    """
    Конвертирование байт в удобное представление.

    Аргументы:
        bytes (int) - колличество байт.

    Возвращает:
        (string) - удобное представление байт.
    """
    try:
        bytes = float(bytes)
    except Exception as exc:
        raise TypeError(u"Передан некорректный формат данных: %s" % exc)
    if bytes >= 1099511627776:
        size = '%.1fTb' % (bytes / 1099511627776)
    elif bytes >= 1073741824:
        size = '%.1fGb' % (bytes / 1073741824)
    elif bytes >= 1048576:
        size = '%.1fMb' % (bytes / 1048576)
    elif bytes >= 1024:
        size = '%.1fKb' % (bytes / 1024)
    else:
        size = '%.1fb' % bytes
    return size

def getNumberFormat(num, unit):
    """
    Возвращает число в указанном формате.

    Аргументы:
        unit (str) - еденицы измерения для сохранения (byte|mbyte|human);
    Возвращает:
        (int|str) - сисло в указанном формате.
    """
    if not num:
        result = ""
    else:
        if unit == "byte":  # Отображение в байтах:
            result = num  # Словарь с доступными камерами.
        elif unit == "mbyte":  # Отображение в мегабайтах:
            result = num / 1000000   # Словарь с доступными камерами.
        elif unit == "human":  # Отображение в человекопонятном виде:
            result = self.convert_bytes(num)
        else:  # Неописанный тип:
            raise Exception(u"Передан неописанный тип представления: %s" % unit)
    return result

def getDiskSizeTotal(diskLeter):
    """
    Определяет размер раздела жёсткого диска.

    Аргументы:
        diskLeter - (string) буква раздела жёстка ("c")

    Возвращает:
        (int) - общий размер жесткого диска в байтах.
    """
    try:
        wmi = GetObject('winmgmts:')
        diskSize = wmi.ExecQuery("SELECT Size FROM Win32_LogicalDisk WHERE DeviceID='%s:'" % diskLeter)
        result = int(diskSize[0].Properties_["Size"].Value)
    except Exception:
        raise
    return result

def getDiskSizeFree(diskLetter):
    """
    Определяет размер свободного места на разделе жёсткого диска в байтах.

    Аргументы:
        (string) diskLeter - буква раздела жёстка ("c")

    Возвращает:
        (int) - размер свободного места жесткого диска в байтах.
    """
    try:
        wmi = GetObject('winmgmts:')
        diskSizeFree = wmi.ExecQuery("SELECT FreeSpace FROM Win32_LogicalDisk WHERE DeviceID='%s:'" % diskLetter)
        result = int(diskSizeFree[0].Properties_["FreeSpace"].Value)
    except Exception:
        raise
    return result

def getDiskSizeFreeProcent(diskLetter):
    """
    Определяет размер свободного места на разделе жёсткого диска в процентах.

    Аргументы:
        diskLetter - (string) буква раздела жёстка ("c")

    Возвращает:
        (int) - размер свободного места жесткого диска в процентах.
    """
    diskTotal = getDiskSizeTotal(diskLetter)
    diskFree = getDiskSizeFree(diskLetter)
    return kstools.getProcent(diskTotal, diskFree)
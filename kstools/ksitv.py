# -*- coding: utf-8 -*-
# Утилиты работы с ПО "Интеллект".


import os
import re
from win32com.client import GetObject


def getArchiveDisks():
    """
    Поиск дисков с архивами.

    Возвращает:
        (list) - списко букв дисков, где расположен архив.
        или исключение WMI
    """
    # Чтение списка жётских дисков на локальном комьпьюетере.
    all_disk = []  # Все диска компьютера.
    archive_disk = []  # Список букв дисков с архивом.
    try:
        wmi = GetObject('winmgmts:')
        diskSizeFree = wmi.ExecQuery("SELECT DeviceID FROM Win32_LogicalDisk WHERE DriveType=3")
        for item in diskSizeFree:
            all_disk.append(item.Properties_["DeviceID"].Value[0])
    except Exception, exc:
        raise
    # Определение дисков с архивами.
    for item in all_disk:
        if os.path.exists("%s:\\VIDEO" % item) and os.path.exists("%s:\\VIDEO\\INDEX" % item):
            archive_disk.append(item)
    return archive_disk

def getArchiveFolder(disk):
    """
    Возвращает список директорий в архиве по указанному диску.

    Аргументы:
        (string) disk - диск с архивом.

    Возвращает:
        (list) - список директорий из указанной папки, вида "18-10-12 08".
    """
    result = []
    for item in os.listdir("%s:\VIDEO" % disk):
        if re.search(r"\d\d-\d\d-\d\d\s\d\d", item):
            result.append(item)
    return result
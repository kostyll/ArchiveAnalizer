# -*- coding: utf-8 -*-
# Утилиты работы с ПО "Интеллект".


import os
import re
from win32com.client import GetObject
import kstools

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

def getArchiveFiles(path):
    """
    Возвращает списко файлов в указаной директроии с архивом.

    Аргументы:
        (str) path - путь к директории с архивом формата (27-10-12 00)

    Возвращает:
        (list) - список файлов с архивными записями.
    """
    result = []
    for item in os.listdir(path):
        if re.search(r"^[0-9A-F]+\._[0-9A-F]+$", item):
            result.append(item)
    return result

def getDateFromPath(path):
    """
    Возарвщает дату создания директроии, казанной в path или None, если дата из пути невозможно извлечь.
    """
    match = re.search(r"(\d\d)\-(\d\d)\-(\d\d)\s(\d\d)$", path)
    if match:
        year = int(match.group(3)) + 2000  # Формирование полного представления года, без учёта 1900 года.
        return "%s-%s-%s" % (year, match.group(2), match.group(1))
    else:
        return None

def getHourFromPath(path):
    """
    Возарвщает час создания директроии, казанной в path или None, если дата из пути невозможно извлечь.
    """
    match = re.search(r"(\d\d)\-(\d\d)\-(\d\d)\s(\d\d)$", path)
    if match:
        return int(match.group(4))
    else:
        return None

def getRecFromFileName(filename):
    """
    Возвращает десятеричный номер записи из имени файла архива.
    """
    match = re.search(r"^([0-9a-fA-F]+)\._[0-9a-fA-F]+$", filename)
    if match:
        return int("0x%s" % match.group(1), 0)
    else:
        return None


def getCamFromFileName(filename):
    """
    Возвращает десятеричный номер камеры из имени файла архива.
    """
    match = re.search(r"^[0-9a-fA-F]+\._([0-9a-fA-F]+)$", filename)
    if match:
        cam_raw = match.group(1)  # Сырой идентификатор камеры.
        if re.search(r"^[0-9]{1,2}$", cam_raw):  # Камера в пределах 0-99:
            return int(cam_raw)
        elif re.search(r"^[0-9]{3,}$", cam_raw):  # Камера от 3-х символов:
            return int("0x%s" % match.group(1), 0) - 60
        else:  # Камера в пределах от 100:
            return int("0x%s" % match.group(1), 0) - 60
    else:
        return None

def getFileInfo(name):
    """
    Чтение информации из видео файла.

    Аргументы:
        (str) name - абсолютный путь к файлу.
    Возвращает:
        {} - словарь с информацией о файле.
    """

    result = {}  # Результат работы.
    try:
        file = open(name,'rb')
        file_data = file.read(80)
        file.close()
    except Exception:
        raise
    else:
        if len(file_data) < 80:
            return None
        result["year"] =  kstools.hexToIntLite(file_data[4], file_data[5])
        result["month"] = kstools.hexToIntLite(file_data[6], file_data[7])
        result["day"] = kstools.hexToIntLite(file_data[8], file_data[9])
        result["hour"] =  kstools.hexToIntLite(file_data[10], file_data[11])
        result["minute"] =  kstools.hexToIntLite(file_data[12], file_data[13])
        result["second"] =  kstools.hexToIntLite(file_data[14], file_data[15])
        result["date"] = "%s-%02d-%02d" % (result["year"], result["month"], result["day"])
        result["time"] = "%02d:%02d:%02d" % (result["hour"], result["minute"], result["second"])
        # Проверка (по косвенным признакам):
        if (result["hour"] >= 0  or result["hour"] < 24) and (result["minute"] >= 0  or result["minute"] <= 60):
            return result
        else:
            return None
# -*- coding: utf-8 -*-
# Различные вспомогательные функции.



def getProcent(total, current):
    """
    Определение текущего процента от заданных значений.

    Аргументы:
        total (int, float) - общее значение.
        current (int, float) - текущее значение.

    Возвращает:
        (int) округлённое значение вычесленных роцентов,
    """
    try:
        total = float(total)
        current = float(current)
    except Exception:
        raise TypeError(u"Передан некорректный тип входных данных total: %s, currnt: %s" % (total, current))
    if current > total:
        raise ValueError(u"Общая сумма %s меньше текущего значения %s" % (total, current))
    elif total < 0 or current < 0:
        raise ValueError(u"Переданные значения меньше 0 - total: %s, currnt: %s" % (total, current))
    else:
        try:
            result = int((float(current)/float(total)) * 100)
        except ZeroDivisionError:
            result = 0
        return result


def hexToIntLite(hex1, hex2=None):
    """
    Преобразоваление шеснадцатеричного значения в двоичное.
    Если нужно сложить 2 числа (из файла), то воодить их нужно друг за другом, а не в обратном порядке.
    """
    if hex2 is None:
        return ord(hex1)
    else:
        return (ord(hex2) * 256) + ord(hex1)




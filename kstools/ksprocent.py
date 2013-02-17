# -*- coding: utf-8 -*-
# Работа с процентами.


def get(total, current):
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

def getRelative(pCurrent, pAll, pMin, pMax):
    """
     Возвращает текущий реальный процент из указанных относительных границ.

     Аргументы:
         pCurrent - текущее значение едениц из pAll.
         pAll - абщее колличество, от чего будет высчитываться процент;
         pMin - начальная значение отсчёта процента;
         pMax - максимальная точка допустимого процента;
         pLen - длинна прогресс бара в единицах.

     Возвращает:
         (int) текущее значение процента.
    """
    lenCur = pMax - pMin  # Длинна отрезка, в пределах которого нужно вычислить текущий процент.
    procCurr = int((float(pCurrent) / float(pAll)) * 100)  # Процент относительно вычисляемого процента.
    procDiff = int((float(lenCur) / 100) * float(procCurr))  # Процент относительно выделенного отрезка.
    procAbs = pMin + procDiff
    return procAbs



# -*- coding: utf-8 -*-
# Список системных утилит.

from PyQt4 import QtCore, QtGui


def message(parent, type_, title, text):
    """
    type_ - тип сообщения (inform|warning|error)
    """
    message = QtGui.QMessageBox(parent)
    message.setText(text)
    message.setWindowTitle(title)
    try:
        message.setIcon({
            "inform": QtGui.QMessageBox.Information,
            "warning": QtGui.QMessageBox.Warning,
            "error": QtGui.QMessageBox.Critical,
        }[type_])
    except KeyError:
        raise ValueError(u"Передан некорректный аргументв icon.")
    message.exec_()

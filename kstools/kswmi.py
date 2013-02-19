# -*- coding: utf-8 -*-
# Работа с различными параметрами через WMI.
# v. 1.0.0 2013.02.19


import wmi
import re

class KsWmi():
    """
    Работа с компьютером через WMI.
    """
    def __init__(self):
        self.wmi = wmi.WMI()

    def getNetIpList(self, active=True):
        """
        Возвращает списко IP с активных сетевых интерфесов.

        active - True - только активные адаптеры, False - все адаптеры.
        """
        result = []
        sql = 'SELECT * FROM Win32_NetworkAdapterConfiguration'
        if active:
            sql += ' WHERE IPEnabled=1'
        for interface in self.wmi.query(sql):
            for ip_address in interface.IPAddress:
                if ip_address != '0.0.0.0':
                    result.append(ip_address)
        return result

    def getNetAdapterList(self, active=True):
        """
        Получает информацию о работающих (в режиме online) сетевых адаптеров.

        active - True - только активные адаптеры, False - все адаптеры.

        Возвращает список словарей:
            description - описание интерфейса.
            ipv4 - список IP адресов v4.
            gateway - IP адресс шлюза.
            dns - список DNS серверов.
            mask - маска подсети.
        """
        interfaceList = []  # Кортеж списков с описаниями сетевых адаптеров.
        sql = 'SELECT * FROM Win32_NetworkAdapterConfiguration'
        if active:
            sql += ' WHERE IPEnabled=1'
        for interface in self.wmi.query(sql):
            result = dict()  # Сбор данный по адаптеру.
            result["description"] = interface.Description
            result["ipv4"] = [item for item in interface.IPAddress if item != "0.0.0.0" and re.search(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", item)]
            try:
                result["gateway"] = interface.DefaultIPGateway[0]
            except TypeError:
                result["gateway"]= ""
            try:
                result["dns"] = [item for item in interface.DNSServerSearchOrder]
            except TypeError:
                result[""] = ()
            try:
                result["mask"] = interface.IPSubnet[0]
            except TypeError:
                result["mask"] = ""
            interfaceList.append(result)
        return interfaceList

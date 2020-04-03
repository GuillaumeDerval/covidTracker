""" This is a very stupid protection against nefarious opponents. For now, it should do. """
from datetime import datetime, date
from cachetools import TTLCache, LRUCache
from flask import request


class IPBan:
    def __init__(self, limit=10, maxsize=16777216, ttl=None, add_day_to_key=False):
        if ttl is None:
            self.__submissions_per_ip = LRUCache(maxsize=maxsize)
        else:
            self.__submissions_per_ip = TTLCache(maxsize=maxsize, ttl=ttl)
        self.__add_day_to_key = add_day_to_key
        self.__limit = limit

    def __gen_key(self, ip):
        if self.__add_day_to_key:
            return ip, date.today()
        return ip

    def __get_ip(self, base_ip=None):
        if base_ip is not None:
            return base_ip
        return request.remote_addr

    def is_ok(self, ip=None):
        ip = self.__get_ip(ip)
        return self.__submissions_per_ip.get(self.__gen_key(ip), 0) <= self.__limit

    def incr(self, ip=None):
        ip = self.__get_ip(ip)
        key = self.__gen_key(ip)
        self.__submissions_per_ip[key] = self.__submissions_per_ip.get(key, 0) + 1

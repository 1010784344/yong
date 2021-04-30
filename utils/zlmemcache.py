# -*- coding: utf-8 -*-
import memcache

mem = memcache.Client(['127.0.0.1:11211'],debug=True)

def set(email, captcha, timeout=60):
    mem.set(email,captcha,time=timeout)

def get(email):
    # 其实不太清楚为什么要加 return，调用又没有接收他的值
    return mem.get(email)

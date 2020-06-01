# coding=utf-8
import time

def content_parse(content):
    content = eval(content.replace("null", "None").replace("false", "False").replace("true", "True"))
    if "data" not in content:
        raise Exception("Data not in response!")
    return content

def get_cache_time():
    return int(time.time() * 1000)

def get_today():
    return time.strftime("%Y%m%d")
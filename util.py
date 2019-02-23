''' 
Biblioteca de utilitarios
'''
import datetime
import time

def escape_str(text):
    t = text.replace('"', '\\"')
    return t

def get_utc_now():
    return datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

def get_utc_hora_min(ts):
    tst = datetime.datetime.fromtimestamp(ts)
    #print(type(tst),tst)
    utc_time = datetime.datetime.strftime(tst, '%Y-%m-%dT%H:%M:%S')
    #print(type(utc_time),utc_time)
    #print (utc_time[11:16])
    return utc_time[11:16]

def get_seg_epoch_now():
    return datetime.datetime.now().timestamp()
    
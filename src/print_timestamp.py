import datetime

# imprime timestamp de "ahora"
utc_time = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
print (utc_time)
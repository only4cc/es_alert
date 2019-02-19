''' 
print ( criterio )
print ("------------------")
print ( criterio['hits']['hits'][0] )
print ( criterio['hits']['hits'][0].items())
print ( criterio['hits']['hits'][0].values())
print ( criterio['hits']['hits'][0].keys())
print ("------------------") '''

import util as util

query = '{ "query" : { "match" : { "variable": " + varname + " } } }'
qq = util.escape_str(query)
print(qq)

import datetime
utc_time = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
utc_hora = utc_time[11:16]


lapso = criterio['hits']['hits'][0]['_source']['lapse']
if len(lapso) == 0:
    print("vacia")
else:
    print(lapso)

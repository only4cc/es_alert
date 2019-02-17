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


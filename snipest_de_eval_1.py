
def isnull(v, default):
    try: v
    except NameError: v = None
    if v is None:
        v = default

try: x
except NameError: x = None
if x is None:
    x = 'default'

print(x)
print ( isnull(y,1) )


'''
try: lapso
except NameError: lapso = None
if ( lapso is None ): 
    lapso     = 60 # Minutos   
else:
    lapso     = criterio['hits']['hits'][0]['_source']['lapse']  

print(lapso)



import util 

def get_pronostico(t_seg_epoch):
    utc_hhmm = util.get_utc_hora_min(t_seg_epoch)   # Horas:Minutos
    return utc_hhmm
    
utc_time      = util.get_utc_now()
seg_timestamp = util.get_seg_epoch_now()
print("utc_time:",utc_time, "seg_timestamp:",seg_timestamp)

print ("get_pronostico")
hhmm = get_pronostico(seg_timestamp)
print(hhmm)

print ( criterio )
print ("------------------")
print ( criterio['hits']['hits'][0] )
print ( criterio['hits']['hits'][0].items())
print ( criterio['hits']['hits'][0].values())
print ( criterio['hits']['hits'][0].keys())
print ("------------------") 
'''

'''
import util 
t = util.get_seg_epoch()
y = eval(" 0.505050 * t + 0.5757575")
print("y:",y)

query = '{ "query" : { "match" : { "variable": " + varname + " } } }'
qq = util.escape_str(query)
print(qq)

lapso = criterio['hits']['hits'][0]['_source']['lapse']
if len(lapso) == 0:
    print("vacia")
else:
    print(lapso)


'''


# Monitoreo y evaluacion
# Obs. : Ajustar nodos segun cluster  
# 
# Falta implementar como evaluar ... :)
# 

from elasticsearch import Elasticsearch
import datetime
import pprint
import alert
import yaml

DEBUG = True

# Lee configuraciones
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

for section in cfg:
    print(section)
nodos        = cfg['cluster_es']['nodos']
clustername  = cfg['cluster_es']['clustername']

# Coneccion al cluster
es = Elasticsearch( nodos )

# Variable a evaluar (tenant es nulo si es una variable del cluster)
tenant  = 'test'
varname = 'tot_docs'

# Obtiene definiciones de criterio de la variable (por el momento sin uso de tenant)
def get_criterio( tenant, varname ):
    # falta agregar el tenant si amerita 
    query = "{ \"query\" : { \"match\" : { \"variable\": \"" + varname + "\"} } }"
    if DEBUG : print ("buscando con la consulta:", query, " ...")
    criterio = es.search(index='alert_criteria',doc_type='def', body=query )
    return criterio


def get_pronostico( tenant, varname, utc_hora ):
    query = "{ \"query\" : { \"match\" : { \"variable\": \"" + varname + "\"} } }"
    pronostico = es.search(index='alert_criteria', body=query ) #doc_type='prono',
    return pronostico

criterio = get_criterio( tenant, varname )

if DEBUG : print ( criterio['hits']['hits'][0]['_source']['query'] )

# Obtiene valor actual para la variable mediante la query almacenada en criterio
query    = criterio['hits']['hits'][0]['_source']['query']
# Ejecuta la consulta para traer el valor actual de la variable 
res      = es.search(body=query)
value    = res['hits']['total'] 

# Timestamp ahora
utc_time = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
utc_hora = utc_time[11:13]
print ("en: ", utc_time, " el valor medido es:", value, " la hora es:", utc_hora )

# Obtiene el Pronostico para esa variable en esa hora
pronostico = get_pronostico( tenant, varname, utc_hora )
if DEBUG:
    pp = pprint.PrettyPrinter(indent=6)
    pp.pprint( pronostico['hits']['hits'][1]['_source']['prono'][0])

ti = pronostico['hits']['hits'][1]['_source']['prono'][0]['timestamp_init']
ev = pronostico['hits']['hits'][1]['_source']['prono'][0]['estimated_value']
print("instante inicial:", ti, "valore estimado:", ev)

umbral        = 1   #<---- Debe venir de criterio
variable_desc = criterio['hits']['hits'][0]['_source']['variable_desc']

# Evaluacion
if ( value > umbral ):
    alert.alarma(tenant, varname, variable_desc, value , umbral)




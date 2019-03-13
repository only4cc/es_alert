# 

from elasticsearch import Elasticsearch
import datetime
import yaml

DEBUG = True

# Lee configuraciones
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

for section in cfg:
    print(section)
nodos        = cfg['cluster_es']['nodos']
clustername  = cfg['cluster_es']['clustername']

if DEBUG: print("nodos:", nodos, "clustername:", clustername )

es = Elasticsearch( nodos )

if DEBUG: 
    print(es.info())

# Obtiene total de documentos en ES
total_docs = es.search( body={ "query": {"match_all": {}} })
if DEBUG: print( "total documentos : ", total_docs['hits']['total'] )

# Registra el total de documentos en el indice es-stat 
utc_time = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
stat={
    "es_clustername"    : clustername,
    "timestamp"         : utc_time,
    "total_docs"        : total_docs['hits']['total'],
}
res = es.index(index='es-stat', doc_type='stat_log', body=stat )

if DEBUG: print(res)
if DEBUG: print("resultado:", res['result'])
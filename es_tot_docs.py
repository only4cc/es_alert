# 

from elasticsearch import Elasticsearch
import datetime
import configparser

DEBUG = True

# Lee configuraciones
config = configparser.ConfigParser()
config.readfp(open(r'config.ini'))
nodos       = config.get('cluster_es', 'nodos')
clustername = config.get('cluster_es', 'clustername')

if DEBUG: print("nodos:", nodos, "clustername:", clustername )

es = Elasticsearch( nodos )
if DEBUG; print(es.info())

# Obtiene total de documentos en ES
total_docs = es.search( body={ "query": {"match_all": {}} })
print( "total documentos : ", total_docs['hits']['total'] )

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
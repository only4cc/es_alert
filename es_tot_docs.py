# Ajustar nodos y clustername 

from elasticsearch import Elasticsearch
import datetime


nodos       = ["10.33.32.107:9200", "10.33.32.108:9200", "10.33.32.109:9200"]
clustername = 'DEV-ECO-6X'
es = Elasticsearch( nodos )

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
res = es.index(index='es-stat',doc_type='stat_log', body=stat )

print(res)
print("resultado:", res['result'])
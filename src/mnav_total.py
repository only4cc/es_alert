# 

from elasticsearch import Elasticsearch
import yaml
import os, sys

DEBUG = True

# Lee configuraciones
try:
    currdir = os.getcwd()
    with open(currdir + "/config.yml", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
except Exception as e:
    print("Error fatal, no se pudo leer el archivo de las configuraciones")
    print(e)
    exit()

nodos        = cfg['cluster_es']['nodos']
clustername  = cfg['cluster_es']['clustername']
nodos        = '192.168.161.101'

# Coneccion al cluster
try:
    es = Elasticsearch(nodos, timeout=3)
except Exception as e:
    print(e)
    sys.exit("No se pudo conectar.")

# Query para obtener valor de la metrica
body_query = """ {
    "aggs": {
        "range": {
            "date_range": {
                "field": "date",
                "format": "yyyy-MM-dd HH",
                "ranges": [
                    { "to": "now+0H/H" },
                    { "from": "now-1H/H" }
                ]
            }
        }
    }
} """

#print("ejecutando:",body_query)

resp = es.search(index='be-mnav-2019*', body=body_query)
#print("resp :", resp["hits"]["total"] )
print( str(resp["hits"]["total"]).rstrip(), end="" )


# Creacion indice es-stat para estadisticas de Elasticsearch

# DELETE es-stat

PUT es-stat
{
  "mappings": {
    "stat_log": { 
       "properties": { 
          "es_clustername"  : { "type": "keyword" }, 
          "timestamp"       : { "type": "date" },
          "total_docs"      : { "type": "float" }
        }
    }
  }
}





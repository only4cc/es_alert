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
import util

DEBUG = True

# Lee configuraciones
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

nodos        = cfg['cluster_es']['nodos']
clustername  = cfg['cluster_es']['clustername']

# Coneccion al cluster
es = Elasticsearch( nodos )

# Variable a evaluar (tenant es nulo si es una variable del cluster)
tenant  = 'ES'
varname = 'tot_docs'

# Obtiene definiciones de criterio de la variable (por el momento sin uso de tenant)
def get_criterio( tenant, varname ):
    query = ('{'
            '"query": {'
            '    "bool": {'
            '    "must": ['
            '        { "term": {"tenant": "'  + tenant + '"}}, '
            '        { "term": {"variable": "'+ varname + '"}}'
            '    ]'
            '    }'
            '}}'
        )
    #if DEBUG: print ("buscando con la consulta:", query, " ...")
    criterio = es.search(index='criteria', body=query )
    return criterio


def get_pronostico( tenant, varname, utc_hora ):
    inicio = utc_hora  # Simula
    fin    = utc_hora  # Simula
    query = ('{'
            '"query": {'
            '    "bool": {'
            '    "must": ['
            '        { "term": {"tenant": "'  + tenant + '"}}, '
            '        { "term": {"variable": "'+ varname + '"}},'
            '        { "range": { "timestamp_init": { "gte": "'+inicio+'", "lte": "'+fin+'" } } }'
            '    ]'
            '    }'
            '}}'
        )
    if DEBUG: print ("buscando pronostico con la consulta:", query, " ...")
    pronostico = es.search(index='criteria', body=query ) #doc_type='prono',
    return pronostico


def main():
    criterio = get_criterio( tenant, varname )

    if DEBUG: 
        print ( "Query recuperada para buscar valor actual de ",tenant,".",varname,":", criterio['hits']['hits'][0]['_source']['query'] )
        # Impresion formateada Pretty
        #pp = pprint.PrettyPrinter(indent=6)
        #pp.pprint( criterio )

    # Obtiene valor actual para la variable mediante la query almacenada en criterio
    query    = criterio['hits']['hits'][0]['_source']['query']

    # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
    res      = es.search(body=query)
    value    = res['hits']['total'] 

    # Timestamp ahora
    utc_time = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    utc_hora = utc_time[11:13]
    print ("en: ", utc_time, " el valor medido es:", value, " la hora es:", utc_hora )

    # Obtiene el Pronostico para esa variable en esa hora
    pronostico = get_pronostico( tenant, varname, utc_hora )

    if DEBUG:
        print("\nPronostico:")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint( pronostico )
        print("\nTotal filas recuperadas:", pronostico['hits']['total'] )
    
    total_retr = pronostico['hits']['total']
    if (  total_retr > 0 ):
        ti = pronostico['hits']['hits'][1]['_source']['prono'][0]['timestamp_init']
        ev = pronostico['hits']['hits'][1]['_source']['prono'][0]['estimated_value']
        print("instante inicial:", ti, "valore estimado:", ev)
    else:
        print("No se encontraron pronosticos para:", tenant, varname, " hora:", utc_hora)

    umbral        = 1   #<---- Debe venir de criterio
    variable_desc = criterio['hits']['hits'][0]['_source']['variable_desc']

    # Evaluacion
    if ( value > umbral ):
        alert.alarma(tenant, varname, variable_desc, value , umbral)



if __name__ == '__main__':
    main()
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


# Obtiene definiciones de criterio de la variable (por el momento sin uso de tenant)
def get_criterio( tenant, varname ):
    query = ('{'
            '"query": {'
            '    "bool": {'
            '    "must": ['
            '        { "exists": { "field": "query" } },'
            '        { "term": {"tenant": "'  + tenant  + '"}}, '
            '        { "term": {"variable": "'+ varname + '"}}'
            '    ]'
            '    }'
            '}}'
            )
    if DEBUG: print ("buscando con la consulta:", query, " ...")
    criterio = es.search(index='criteria', body=query )
    return criterio


def get_pronostico( criterio, utc_hhmm ):
    tenant   = criterio['hits']['hits'][0]['_source']['tenant']
    varname  = criterio['hits']['hits'][0]['_source']['variable']
    lapso    = 60 #criterio['hits']['hits'][0]['_source']['lapse'] 
    
    inicio_i = int(utc_hhmm[:2])*lapso    
    inicio   = str( inicio_i )
    # print("recibi:", utc_hhmm, "slice:",utc_hhmm[0:2], "inicio:", inicio)
    fin    = str( inicio_i + lapso )      
    query = ('{'
            '"query": {'
            '    "bool": {'
            '    "must": ['
            '        { "term": {"tenant": "'  + tenant + '"}}, '
            '        { "term": {"variable": "'+ varname + '"}},'
            '        { "range": { "ini": { "gte": "'+inicio+'", "lte": "'+fin+'" } } }'
            '    ]'
            '    }'
            '}}'
            )
    if DEBUG: print ("buscando pronostico con la consulta:", query, " ...")
    pronostico = es.search(index='criteria', body=query ) #doc_type='prono',
    return pronostico


def main():
    # Variable a evaluar (tenant es nulo si es una variable del cluster)
    tenant  = 'ES'          # Cuando la variable es "interna"
    varname = 'tot_docs'    # total de documentos en ES
    criterio = get_criterio( tenant, varname )

    if DEBUG: 
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint( criterio )
        print ( "Query recuperada para buscar valor actual de tenant:[",tenant,"] variable:[",varname,"]")
        print ("Criterio:", criterio['hits']['hits'][0]['_source']['query'] )
        # Impresion formateada Pretty
        #pp = pprint.PrettyPrinter(indent=6)
        #pp.pprint( criterio )

    # Obtiene valor actual para la variable mediante la query almacenada en criterio
    query_criterio = criterio['hits']['hits'][0]['_source']['query']

    # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
    res      = es.search(body=query_criterio)
    value    = res['hits']['total'] 

    # Timestamp de Ahora
    utc_time     = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    utc_hora_min = utc_time[11:16]   # Horas:Minutos
    print ("A las: [", utc_time, "] el valor medido es:[", value, "] la hora es:", utc_hora_min )

    # Obtiene el Pronostico para esa variable en esa hora
    pronostico = get_pronostico( criterio, utc_hora_min )

    if DEBUG:
        print("\nPronostico:")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint( pronostico )
        print("\nTotal filas recuperadas:", pronostico['hits']['total'] )
    
    total_retr = pronostico['hits']['total']
    if (  total_retr == 1 ):
        ti = pronostico['hits']['hits'][0]['_source']['ini']
        ev = pronostico['hits']['hits'][0]['_source']['estimated_value']
        print("instante inicial:", ti, "valore estimado:", ev)
    else:
        if ( total_retr < 1):
            print("No se encontraron pronosticos para:", tenant, varname, " hora:", utc_hora_min)
        else:
            print("Se encontro mas de un pronostico para:", tenant, varname, " hora:", utc_hora_min)

    umbral        = 1   #<---- Debe venir de criterio para ese rango de hora y la variable monitoreada
    variable_desc = criterio['hits']['hits'][0]['_source']['variable_desc']

    # Evaluacion
    if ( value > umbral ):
        alert.alarma(tenant, varname, variable_desc, value , umbral)



if __name__ == '__main__':
    main()
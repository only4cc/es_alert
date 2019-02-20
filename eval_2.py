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

class Variable:
    def __init__(self, tenant, varname):
        self.tenant  = tenant
        self.varname = varname

# Obtiene definiciones de criterio de la variable (por el momento sin uso de tenant)
    def get_criterio(self):   
        query = ('{'
                '"query": {'
                '    "bool": {'
                '    "must": ['
                '        { "exists": { "field": "query" } },'
                '        { "term": {"tenant": "'  + self.tenant  + '"}}, '
                '        { "term": {"variable": "'+ self.varname + '"}}'
                '    ]'
                '    }'
                '}}'
                )
        if DEBUG: print ("buscando con la consulta:", query, " ...")
        self.criterio      = es.search(index='criteria', body=query )
        self.variable_desc = self.criterio['hits']['hits'][0]['_source']['variable_desc']
        return self.criterio

# Obtiene valor actual para la variable mediante la query almacenada en criterio
    def get_current_value(self):
        query_criterio = self.criterio['hits']['hits'][0]['_source']['query']
        # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
        res    = es.search(body=query_criterio)
        self.val    = res['hits']['total'] 
        return self.val

    def get_pronostico(self, utc_hhmm):
        #tenant   = criterio['hits']['hits'][0]['_source']['tenant']
        tenant   = self.criterio
        #varname  = criterio['hits']['hits'][0]['_source']['variable']
        varname  = self.varname
        lapso    = 60 #criterio['hits']['hits'][0]['_source']['lapse'] 
        
        inicio_i = int(utc_hhmm[:2])*lapso    
        inicio   = str( inicio_i )
        # print("recibi:", utc_hhmm, "slice:",utc_hhmm[0:2], "inicio:", inicio)
        fin    = str( inicio_i + lapso )      
        self.query_pronostico = ('{'
                                    '"query": {'
                                    '    "bool": {'
                                    '    "must": ['
                                    '        { "term": {"tenant": "'  + self.tenant + '"}}, '
                                    '        { "term": {"variable": "'+ self.varname + '"}},'
                                    '        { "range": { "ini": { "gte": "'+ inicio+'", "lte": "'+fin+'" } } }'
                                    '    ]'
                                    '    }'
                                    '}}'
                )
        if DEBUG: print ("buscando pronostico con la consulta:", self.query_pronostico, " ...")
        self.pronostico = es.search(index='criteria', body=self.query_pronostico ) #doc_type='prono',
        return self.pronostico

    def get_numretrieved_pronostico(self):
        self.total_retr = self.pronostico['hits']['total']
        return self.total_retr

    def get_pronostico_init(self):
        if ( self.total_retr == 1 ):
            self.ti = self.pronostico['hits']['hits'][0]['_source']['ini']
        else:
            self.ti = None
        return self.ti

    def get_pronostico_estimated_value(self):
        if ( self.total_retr == 1 ):
            self.ev = pronostico['hits']['hits'][0]['_source']['estimated_value']
        else:
            self.ev = None
        return self.ev

    def get_umbral(self):
        # Rellenar este codigo ...
        umbral = self.tenant + self.varname
        return umbral

def main():

    # Variable a evaluar (tenant es nulo si es una variable del cluster)
    tenant  = 'ES'          # Cuando la variable es "interna" ie Elasticsearch
    varname = 'tot_docs'    # Nombre de la variable: total de documentos en ES

    var = Variable(tenant, varname)
    
    # Obtiene "criterio" definido para la variable
    criterio = var.get_criterio()

    if DEBUG: 
         # Impresion formateada Pretty
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint( criterio )
        print ("Query recuperada para buscar valor actual de tenant:[",tenant,"] variable:[",varname,"]")
        print ("Criterio:", criterio['hits']['hits'][0]['_source']['query'] )

    # Consulta el valor actual de la variable usando la definicion de "criterio"   
    value = var.get_current_value()

    # Timestamp de Ahora
    utc_time     = datetime.datetime.strftime(datetime.datetime.utcnow(), '%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    utc_hora_min = utc_time[11:16]   # Horas:Minutos
    print ("A las: [", utc_time, "] el valor medido es:[", value, "] la hora es:", utc_hora_min )

    # Obtiene el Pronostico para esa variable en esa hora y minutos HH:MM
    pronostico = var.get_pronostico( utc_hora_min )

    if DEBUG:
        print("\nPronostico:")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint( pronostico )
        print("\nTotal filas recuperadas:", pronostico['hits']['total'] )
    
    total_retr = var.get_numretrieved_pronostico() #pronostico['hits']['total']
    ti = var.get_pronostico_init()
    ev = var.get_pronostico_estimated_value()

    if (  total_retr == 1 ):
        ti = var.get_pronostico_init()
        ev = var.get_pronostico_estimated_value()
        print("instante inicial:", ti, "valore estimado:", ev)
    else:
        if ( total_retr < 1):
            print("No se encontraron pronosticos para:", tenant, varname, " hora:", utc_hora_min)
        else:
            print("Se encontro mas de un pronostico para:", tenant, varname, " hora:", utc_hora_min)

    umbral  = var.get_umbral()   #<---- Debe venir de criterio para ese rango de hora y la variable monitoreada    
    
    # Evaluacion
    print("comparando el valor actual: [",value,"] con el umbral [",umbral,"]")
    if ( value > umbral ):
        alert.alarma(tenant, varname, var.variable_desc, value , umbral)



if __name__ == '__main__':
    main()
# Monitoreo y evaluacion
#

from elasticsearch import Elasticsearch
import datetime
import pprint
import alert
import yaml
import util
import sys


DEBUG = False
DEMO  = True

# Lee configuraciones
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

nodos        = cfg['cluster_es']['nodos']
clustername  = cfg['cluster_es']['clustername']

# Coneccion al cluster
es = Elasticsearch( nodos )

class Variable:
    # La entrada es tenant + varname 
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
        try:
            self.criterio      = es.search(index='criteria', body=query )
            self.varname_desc  = self.criterio['hits']['hits'][0]['_source']['variable_desc']
            self.formula       = " 5 *t + 33 " # self.criterio['hits']['hits'][0]['_source']['formula']" 
            self.veces_alarmas = 0    # Inicializa las alarmas en cero 
            self.veces_warn    = cfg['defaults']['veces_warn'] 
            self.veces_alert   = cfg['defaults']['veces_alert'] 
            self.prono_type    = cfg['defaults']['prono_type']  # 'F' =  Formula
            self.umbral_type   = cfg['defaults']['umbral_type'] # 'porcentual' / 'fix'
            self.percent       = 0.01 
            try:
                self.lapso         = self.criterio['hits']['hits'][0]['_source']['lapse']
            except:
                self.lapso         = cfg['defaults']['lapse']               
            
            if DEBUG: 
                # Impresion formateada Pretty
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.criterio )
                print ("Query recuperada para buscar valor actual de tenant:[",self.tenant,"] variable:[",self.varname,"]")
                print ("Criterio:", self.criterio['hits']['hits'][0]['_source']['query'] )            
        except:
            print("Error:\nNo se recupero el criterio para la variable ["+self.varname+"] tenant ["+self.tenant+"]")
            print("Se aborta monitoreo.")
            exit()
                
        return self.criterio

    # Obtiene valor actual para la variable mediante la query almacenada en criterio
    def get_current_value(self):
        query_criterio = self.criterio['hits']['hits'][0]['_source']['query']
        # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
        res               = es.search(body=query_criterio)
        self.currval      = res['hits']['total'] 
        self.time_currval = util.get_seg_epoch_now()
        return self.currval

    def get_pronostico(self, t_seg_epoch):
        utc_hhmm = util.get_utc_hora_min(t_seg_epoch)   # en Horas:Minutos
        if ( self.prono_type == 'F'):
            self.ev = self.get_pronostico_estimated_value(t_seg_epoch)
            return self.ev
        else:            
            inicio_i = int(utc_hhmm[:2])*self.lapso    
            inicio   = str( inicio_i )               # HHMM de Inicio del Lapso
            fin    = str( inicio_i + self.lapso )    # HHMM de Fin del Lapso
            self.query_pronostico = ('{'
                                        '"query": {'
                                        '    "bool": {'
                                        '    "must": ['
                                        '        { "term": {"tenant": "'  + self.tenant + '"}}, '
                                        '        { "term": {"variable": "'+ self.varname + '"}},'
                                        '        { "range": { "ini": { "gte": "'+inicio+'", "lte": "'+fin+'" } } }'
                                        '    ]'
                                        '    }'
                                        '}}'
                    )
            if DEBUG: print ("buscando pronostico con la consulta:", self.query_pronostico, " ...")
            self.pronostico = es.search(index='criteria', body=self.query_pronostico ) #doc_type='prono',
            #---------------------------------------------------------------------------------------------------
            if DEBUG:
                print("\nPronostico:")
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.pronostico )
                print("\nTotal filas recuperadas:", self.pronostico['hits']['total'] )
            
            total_retr = self.get_numretrieved_pronostico() #pronostico['hits']['total']
            ti = self.get_pronostico_ts_ini()
            ev = self.get_pronostico_estimated_value( t_seg_epoch )

            utc_time = util.get_utc_hora_min(t_seg_epoch)
            if (  total_retr == 1 ):
                ti = self.get_pronostico_ts_ini()
                ev = self.get_pronostico_estimated_value(t_seg_epoch)
                self.ev = ev
                print("instante inicial:", ti, "valore estimado:", ev)
            else:
                if ( total_retr < 1):
                    print("No se encontraron pronosticos para:", self.tenant, self.varname, " hora:", utc_time)
                else:
                    print("Se encontro mas de un pronostico para:", self.tenant, self.varname, " hora:", utc_time)
            #---------------------------------------------------------------------------------------------------
        return  self.ev

    def get_numretrieved_pronostico(self):
        self.total_retr = self.pronostico['hits']['total']
        return self.total_retr

    def get_pronostico_ts_ini(self):
        if ( self.total_retr == 1 ):
            self.ti = self.pronostico['hits']['hits'][0]['_source']['ini']
        else:
            self.ti = None
        return self.ti

    def get_pronostico_estimated_value(self, t):
        self.ev = eval( self.formula )    
        print ("*** valor estimado de [",self.varname,"] *** usando formula = ", self.formula,":", self.ev, "en t[seg epoch]: ",t)
        return self.ev

    def get_umbral(self, seg_timestamp):
        
        if self.umbral_type == 'fix':
            try:
                delta_max_1 = self.criterio['hits']['hits'][0]['_source']['delta_max_1']
            except:
                delta_max_1 = 0
            
            try:
                delta_min_1 = self.criterio['hits']['hits'][0]['_source']['delta_min_1']
            except:
                delta_min_1 = 0
        else:
            delta_max_1 = self.percent * self.ev
            delta_min_1 = self.percent * self.ev

        umbral_max = self.ev + delta_max_1
        umbral_min = self.ev - delta_min_1
        return [umbral_max, umbral_min]

    def acumula(self):
        self.veces_alarmas = self.veces_alarmas + 1

    def reduce(self):
        self.veces_alarmas = self.veces_alarmas - 1

    def veces(self):
        return self.veces_alarmas

    def get_veces_warn(self):
        return self.veces_warn

    def get_veces_alert(self):
        return self.veces_alert
        

def main():
    # Variable a evaluar (tenant es nulo si es una variable del cluster)
    tenant  = sys.argv[1]    # Cuando la variable es "interna" ie Elasticsearch
    varname = sys.argv[2]    # Nombre de la variable: total de documentos en ES

    if DEMO:
        tenant  = 'ES'          
        varname = 'tot_docs'   

    var = Variable(tenant, varname)
    
    # Obtiene "criterio" definido para la variable
    var.get_criterio()

    # Consulta el valor ACTUAL de la variable monitoreada usando la definicion de "criterio"   
    value         = var.get_current_value()    
    # Timestamp de Ahora
    seg_timestamp = util.get_seg_epoch_now()
    
    if DEBUG: 
        utc_time      = util.get_utc_now()
        print ("A las: [", utc_time, "] el valor medido es:[", value, "]\nEpoch timestamp seg:", seg_timestamp )

    # Obtiene el Pronostico para la variable en ese timestamp
    value = var.get_pronostico( seg_timestamp )
    [umbral_max, umbral_min] = var.get_umbral(seg_timestamp) #<-- Debe obtenerse de criterio para el rango de hora y la variable monitoreada    

    # Evaluacion
    print("comparando el valor actual: [",value,"] con umbrales min: [",umbral_min,"] y max: [", umbral_max,"]")
    if ( value < umbral_max and value > umbral_min ):
        print("Ok")
        var.reduce()
    else:
        var.acumula()

        veces_warn  = var.get_veces_warn()
        veces_alert = var.get_veces_alert()

        # Nivel de alarma
        nivel = "NORMAL"        
        if ( var.veces() > veces_warn ):
            nivel = "ALERTA"
        if ( var.veces() > veces_alert ):
            nivel = "ERROR"

        if ( var.currval >= umbral_max ):
            msg = "valor actual "+str(var.currval)+" mayor o igual a "+str(umbral_max)
        if ( var.currval < umbral_min ):
            msg = "valor actual "+str(var.currval)+" menor a "+ str(umbral_min)		
        
        if ( nivel != 'NORMAL' ):
            alert.alarma(nivel, tenant, varname, var.varname_desc, var.currval, seg_timestamp, msg)
        else:
            if DEBUG:
                print("Nivel :",nivel," ...")
	

if __name__ == '__main__':
    main()
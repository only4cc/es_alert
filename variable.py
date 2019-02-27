''' 
Biblioteca con Variable
'''
from elasticsearch import Elasticsearch
import datetime, sys, yaml, pprint, os
import alert
import util

DEBUG = False   # Verbosidad

def alert_internal_problem(tenant,varname):
    nivel = 'INTERNAL'
    alert.alarma(nivel, tenant, varname, '', '', util.get_seg_epoch_now(), "Error interno. tenant:"+tenant+" variable:"+varname)
    exit()

class Variable:
    # El identificadir de cada Variable es tenant + varname 
    def __init__(self, tenant, varname):
        ''' Obtiene parametros por defecto y Se conecta a ES '''
        self.tenant  = tenant
        self.varname = varname
        # Lee configuraciones
        try:
            currdir = os.getcwd()
            with open(currdir + "/config.yml", 'r') as ymlfile:
                self.cfg = yaml.load(ymlfile)
        except:
            print("Error fatal, no se pudo leer el archivo de las configuraciones")
            exit()

        self.nodos        = self.cfg['cluster_es']['nodos']
        self.clustername  = self.cfg['cluster_es']['clustername']
        
        # Coneccion al cluster         
        try:
            print("coneccion a ES ...", end=" ")
            self.es = Elasticsearch(self.nodos, timeout=3)
        except Exception as e:
            print("No se pudo conectar, se aborta.")
            print(e)
            sys.exit("No se pudo conectar, se aborta.")        

    def get_criterio(self):   
        # Obtiene definiciones de criterio de la variable
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
        
        if DEBUG: 
            print("Buscando definicion de criterio con :\n",query)
        
        try: self.criterio = self.es.search(index='criteria', body=query )
        except: 
            print("Error fatal no se puedo recuperar la query del criterio")
            exit()
        
        try:
            try:    self.varname_desc = self.criterio['hits']['hits'][0]['_source']['variable_desc']
            except: self.varname_desc = "Sin descripcion"

            try:    self.prono_type   = self.criterio['hits']['hits'][0]['_source']['prono_type']
            except: self.prono_type   = self.cfg['defaults']['prono_type']  # 'F' =  Formula / "D" = Discreto          
            
            try:    
                self.formula       = self.criterio['hits']['hits'][0]['_source']['formula'] 
                if ( len(self.formula) == 0 and self.prono_type == 'F' ):
                    self.formula   = " 3 * t + 33333 "
                    if DEBUG: print ("formula:", self.formula)
            except:
                if ( len(self.formula) == 0 and self.prono_type == 'F' ):
                    self.formula   = " 5 * t + 33333 "
                    print ("formula:", self.formula)

            try:    self.lapso         = self.criterio['hits']['hits'][0]['_source']['lapse']
            except: self.lapso         = self.cfg['defaults']['lapse']               

            self.veces_alarmas = 0    # Inicializa las alarmas en cero             
            self.veces_warn    = self.cfg['defaults']['veces_warn'] 
            self.veces_alert   = self.cfg['defaults']['veces_alert'] 
            self.umbral_type   = self.cfg['defaults']['umbral_type'] # 'porcentual' / 'fix'
            self.percent       = 0.01 
            #self.pronostico    = []
            
            if DEBUG: 
                # Impresion formateada de criterio 
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.criterio )
                print ("Query recuperada para buscar valor actual, tenant:[",self.tenant,"] variable:[",self.varname,"]")
                print ("Criterio:", self.criterio['hits']['hits'][0]['_source']['query'] )            
        except:
            print("Error:\nNo se recupero toda la info necesaria para la variable ["+self.varname+"] tenant ["+self.tenant+"]")
            alert_internal_problem(self.tenant, self.varname)                

        return self.criterio
    
    def get_current_value(self):
        # Obtiene valor actual para la variable mediante la query almacenada en criterio
        query_criterio = self.criterio['hits']['hits'][0]['_source']['query']
        # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
        res               = self.es.search(body=query_criterio)
        self.currval      = res['hits']['total'] 
        self.time_currval = util.get_seg_epoch_now()
        return self.currval

    def get_pronostico(self, t_seg_epoch):
        # Obtiene valor pronosticado para ese instante o intervalo de tiempo 
        # ------------------------------------------------------------------
        utc_hhmm = util.get_utc_hora_min(t_seg_epoch)   # en Horas:Minutos
        if ( self.prono_type == 'F'):                   
            # Pronostico basado en Formula
            t = t_seg_epoch
            self.ev = eval( self.formula )
            print ("*** valor estimado de [",self.varname,"] ", " tenant: [", self.tenant,"]")
            print ("*** usando formula : [", self.formula," ] = ", self.ev)
            print ("*** en t[seg epoch]: ", t, " | hh:mm:", util.get_utc_hora_min(t) )
            return self.ev
        else:
            # Pronostico basado en registros en ES            
            inicio_i = int(utc_hhmm[:2]) * self.lapso    
            inicio   = str( inicio_i )                 # HHMM de Inicio del Lapso
            fin      = str( inicio_i + self.lapso )    # HHMM de Fin del Lapso
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
            self.pronostico = self.es.search(index='criteria', body=self.query_pronostico ) #doc_type='prono',
            #---------------------------------------------------------------------------------------------------
            if DEBUG:
                print("\nPronostico:")
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.pronostico )
                print("\nTotal filas recuperadas:", self.pronostico['hits']['total'] )
            
            self.total_retrieved = self.pronostico['hits']['total']
            if (  self.total_retrieved > 0 ):
                self.ev = self.pronostico['hits']['hits'][0]['_source']['prono_value']
            else:
                utc_time = util.get_utc_hora_min(t_seg_epoch)
                print("No se encontraron pronosticos para:", self.tenant, self.varname, " hora:", utc_time)
            #---------------------------------------------------------------------------------------------------
        return  self.ev

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
        if ( self.veces_alarmas < 0 ):
            self.veces_alarmas = 0

    def veces(self):
        return self.veces_alarmas

    def get_veces_warn(self):
        return self.veces_warn

    def get_veces_alert(self):
        return self.veces_alert

    def get_formula(self):
        return self.formula

    def get_lapse(self):
        return self.lapso

    def insert_prono(self, pronostic ):
        res = self.es.index(index='criteria', doc_type='_doc', body=pronostic ) 
        return res

    def create_criterio(self, varname_desc, query, prono_type, formula, lapso, umbral_type='P', umbral_percent=None ):   
        if (varname_desc is None):
            print("varname_desc es obligatoria, se aborta registro")
            return 
        
        if (query is None):
            print("query es obligatoria, se aborta registro")
            return 
    
        prono_type    = prono_type  # 'F' =  Formula / "D" = Discreto                  
        
        if ( prono_type == 'F'):
            if ( formula is None):
                print("dado qe el pronostico es por formula, esta es obligatoria, se abora registro")
                return 
        
        if ( lapso is None ):
            lapso = self.cfg['defaults']['lapse']
        
        #if ( veces_warn is None):         
            veces_warn    =  self.cfg['defaults']['times_warn'] 
        #if ( veces_alert is None):
            veces_alert   =  self.cfg['defaults']['times_alert'] 
        
        umbral_type   =  umbral_type # 'porcentual' / 'fix'
        if ( umbral_type == 'P'):
            percent       = 0.01 
            
        body = {
                "tenant"            : self.tenant,
                "varname"           : self.varname,
                "varname_desc"      : varname_desc,
                "query"             : query,
                "prono_type"        : prono_type,
                "formula"           : formula,
                "lapse"             : lapso,
                "times_alert"       : veces_alert,
                "times_warn"        : veces_warn,
                "alert_count"       : veces_alert,
                "umbral_type"       : umbral_type,
                "umbral_percent"    : umbral_percent,
                "alarm_count"       : 0    # Inicializa las alarmas en cero    
        }
        
        try:
            resp = self.es.index(index='criteria', doc_type='_doc',body=body )
        except Exception as e:
            print(e)
            print("Error:\nNo se pudo crear la definicion de la variable ["+self.varname+"] tenant ["+self.tenant+"]")
        return resp

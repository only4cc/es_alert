<<<<<<< HEAD
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
    ''' 
        Variable para la cual se requiere alertar
        El identificador de cada Variable es tenant + varname
    ''' 
    
    def __init__(self, tenant, varname):
        ''' Obtiene parametros por defecto y Se conecta a ES '''
        self.tenant  = tenant
        self.varname = varname
        # Lee configuraciones
        try:
            currdir = os.getcwd()
            with open(currdir + "/config.yml", 'r') as ymlfile:
                self.cfg = yaml.safe_load(ymlfile)
        except Exception as e:
            print("Error fatal, no se pudo leer el archivo de las configuraciones")
            print(e)
            exit()

        self.nodos        = self.cfg['cluster_es']['nodos']
        self.clustername  = self.cfg['cluster_es']['clustername']
        
        # Coneccion al cluster         
        try:
            #print("coneccion a ES ...")
            self.es = Elasticsearch(self.nodos, timeout=3)
        except Exception as e:
            print(e)
            sys.exit("No se pudo conectar, se aborta.")
                
    def get_criterio(self):   
        # Obtiene definiciones de criterio de la variable
        query_get_query = (
                    '{'
                    '  "query": {'
                    '    "bool": {'
                    '      "must": [ '
                    '           { "exists": { "field": "varname" } },'
                    '			{ "match": {"tenant": "' + self.tenant  +'"}},'
                    '			{ "match": {"varname": "'+ self.varname + '"}'
                    '        }'
                    '      ]'
                    '    }'
                    '  }'
                    '}' 
        )
        
        if DEBUG: 
            print("Buscando definicion de criterio con :\n",query_get_query)
        
        try: self.definicion = self.es.search(index='var_def', body=query_get_query )
        except Exception as e: 
            print("No se puedo recuperar la definicion de esa variable", tenant, varname)
            print(e)
            exit()

        try: self.query = self.definicion['hits']['hits'][0]['_source']['query']
        except Exception as e: 
            print("No se puedo acceder al valor de la query del criterio")
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint( self.definicion )
            print(e)

        try:
            try:    self.varname_desc = self.definicion['hits']['hits'][0]['_source']['varname_desc']
            except: self.varname_desc = "Sin descripcion"

            try:    self.prono_type  = self.definicion['hits']['hits'][0]['_source']['prono_type']
            except: self.prono_type  = self.cfg['defaults']['prono_type']  # 'F' =  Formula / "D" = Discreto / "E" = External

            print("prono_type:",self.prono_type)

            if ( self.prono_type == 'F' ):
                try:  self.formula = self.definicion['hits']['hits'][0]['_source']['formula'] 
                except Exception as e:
                    print(e)

            try:    self.lapso         = self.definicion['hits']['hits'][0]['_source']['lapse']
            except: self.lapso         = self.cfg['defaults']['lapse']               

            self.veces_alarmas = 0    # Inicializa las alarmas en cero             
            self.veces_warn    = self.cfg['defaults']['times_warn'] 
            self.veces_alert   = self.cfg['defaults']['times_alert'] 
            self.umbral_type   = self.cfg['defaults']['umbral_type'] # 'porcentual' / 'fix'
            self.percent       = 0.01 

            if (self.prono_type == 'E'):
                self.external_eval  = self.definicion['hits']['hits'][0]['_source']['external_eval']
                self.external_prono = self.definicion['hits']['hits'][0]['_source']['external_prono']
           
            if DEBUG: 
                # Impresion formateada de criterio 
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.definicion )
                print ("Query recuperada para buscar valor actual, tenant:[",self.tenant,"] variable:[",self.varname,"]")
                print ("Criterio:", self.definicion['hits']['hits'][0]['_source']['query'] )            
        except Exception as e:
            print("Error:\nNo se recupero toda la info necesaria para la variable ["+self.varname+"] tenant ["+self.tenant+"]")
            print(e)
            alert_internal_problem(self.tenant, self.varname)                

        return self.definicion
    
    def get_current_value(self):
        # Obtiene valor actual para la variable mediante la query almacenada en criterio
        if ( self.prono_type == 'F'):  
            query_criterio = self.definicion['hits']['hits'][0]['_source']['query']
            # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
            res               = self.es.search(body=query_criterio)
            self.currval      = res['hits']['total'] 

        if ( self.prono_type == 'E'):
            print("evaluando valor actual con "+self.external_eval)
            toexec = "sh " + self.external_eval        #  Ejemplo mnav_total.sh
            #toexec = self.external_eval 
            self.currval = os.popen(toexec).read()  
            self.currval = self.currval.rstrip()

        self.time_currval = util.get_seg_epoch_now()
        return self.currval

    def save_current_value(self):
        # Guarda en forma persistente valor medido (para mantener Historia de la variable)
        history = {
                    "tenant"           : self.tenant,
                    "varname"          : self.varname,
                    "value"            : self.currval,
                    "timestamp"        : self.time_currval
                }
        try:
            res = self.es.index(index='var_hist', doc_type='def', body=history ) 
        except Exception as e:
            print(e.info)
        return res

    def get_pronostico(self, t_seg_epoch):
        # Obtiene valor pronosticado para ese instante o intervalo de tiempo 
        # ------------------------------------------------------------------
        if ( self.prono_type == 'E'):
            #toexec = "python " + self.external_prono + " " + str(t_seg_epoch)
            toexec = self.external_prono + " " + str(t_seg_epoch)
            self.currval = os.popen(toexec).read()
            self.currval = self.currval.rstrip()
  
        if ( self.prono_type == 'F'):                   
            # Pronostico basado en Formula
            t = t_seg_epoch
            try:
                self.ev = eval( self.formula )
                print ("*** valor estimado de [",self.varname,"] ", " tenant: [", self.tenant,"]")
                print ("*** usando formula : [", self.formula," ] = ", self.ev)
                print ("*** en t[seg epoch]: ", t, " | hh:mm:", util.get_utc_hora_min(t) )
            except Exception as e:
                print(e)
                print("Error:\nNo se pudo usar la formula la variable ["+self.varname+"] tenant ["+self.tenant+"]")
                self.ev = 0
        else:
            # Pronostico basado en registros en ES            
            # inicio_i = int(utc_hhmm[:2]) * self.lapso    
            # inicio   = str( inicio_i )                 # HHMM de Inicio del Lapso
            # fin      = str( inicio_i + self.lapso )    # HHMM de Fin del Lapso
            # self.query_pronostico = ('{'
            #                             '"query": {'
            #                             '    "bool": {'
            #                             '    "must": ['
            #                             '        { "term": {"tenant": "'  + self.tenant + '"}}, '
            #                             '        { "term": {"variable": "'+ self.varname + '"}},'
            #                             '        { "range": { "ts_ini": { "gte": "'+inicio+'", "lte": "'+fin+'" } } }'
            #                             '    ]'
            #                             '    }'
            #                             '}}'
            #         )

            t_seg_epoch_str = str(t_seg_epoch)
            self.query_pronostico = ('{ "query": { "bool":  '
                                        '              { "must": [  '
                                        '			  { "match": { "tenant": "'  + self.tenant + '" } }, '
                                        '			  { "match": { "varname": "' + self.varname + '" } }, '
                                        '			  { "range": { "ts_ini": { "lt": "'+t_seg_epoch_str+'" } } }, '
                                        '			  { "range": { "ts_end": { "gt": "'+t_seg_epoch_str+'" } } } '
                                        '						] '
                                        '} } }'
             )
            if DEBUG: print ("buscando pronostico con la consulta:", self.query_pronostico, " ...")
            self.pronostico = self.es.search(index='var_prono', doc_type='prono', body=self.query_pronostico )             
            #---------------------------------------------------------------------------------------------------
            if DEBUG:
                print("\nPronostico para el rango de ese instante:")
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.pronostico )
                print("\n*** Total filas recuperadas:", self.pronostico['hits']['total'] )
            
            self.total_retrieved = self.pronostico['hits']['total']
            if (  self.total_retrieved > 0 ):
                self.ev = self.pronostico['hits']['hits'][0]['_source']['estimated_value']
            else:
                utc_time = util.get_utc_hora_min(t_seg_epoch)
                print("*** No se encontraron pronosticos para:", self.tenant, self.varname, " epoch:",t_seg_epoch," hora:", utc_time)
                self.ev = -1
            #---------------------------------------------------------------------------------------------------
        return  self.ev

    def get_umbral(self, seg_timestamp):
        ''' Obtiene Umbrales para alarmar '''
        if self.umbral_type == 'fix':
            try:
                delta_max_1 = self.definicion['hits']['hits'][0]['_source']['delta_max_1']
            except:
                delta_max_1 = 0
            
            try:
                delta_min_1 = self.definicion['hits']['hits'][0]['_source']['delta_min_1']
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

    def reducer(self):
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

    def insert_prono(self, pronostic):
        res = self.es.index(index='var_prono', doc_type='def', body=pronostic ) 
        return res

    def create_criterio(self, varname_desc, query, prono_type, formula, lapso, umbral_type, umbral_factor_1=None, umbral_factor_2=None ):   
        
        if (varname_desc is None):
            print("varname_desc es obligatoria, se aborta registro")
            return 
        
        if (query is None):
            print("query es obligatoria, se aborta registro")
            return 
        
        if (prono_type is None):
            print("Tipo de pronostico [prono_type] es obligatorio, se aborta registro")
            return 
        
        if ( prono_type == 'F'):
            if ( formula is None ):
                print("dado qe el pronostico es por formula, esta es obligatoria, se abora registro")
                return 
        
        if ( lapso is None ):
            lapso = self.cfg['defaults']['lapse']   # Se usa el default general
        
        #if ( veces_warn is None):         
        veces_warn    =  self.cfg['defaults']['times_warn'] 
        #if ( veces_alert is None):
        veces_alert   =  self.cfg['defaults']['times_alert'] 
        
        #umbral_type'porcentual' / 'fix'
        #if ( umbral_type == 'porcentual'):

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
                "umbral_factor_1"   : umbral_factor_1,
                "umbral_factor_2"   : umbral_factor_2,
                "alarm_count"       : 0    # Inicializa las alarmas en cero    
        }
        
        try:
            self.es.index(index='var_def', doc_type='def',body=body )
        except Exception as e:
            print(e)
            print("Error:\nNo se pudo crear la definicion de la variable ["+self.varname+"] tenant ["+self.tenant+"]")


    def __str__(self):
        try: self.formula
        except: self.formula ='sin formula'

        salida = "tenant:"+self.tenant + ", varname:" + self.varname + ", varname_desc:" \
                + self.varname_desc + ",\nquery:" + self.query \
                + "prono_type: "+self.prono_type + ", formula: " +self.formula + ", umbral_type:" \
                + self.umbral_type
        return salida


    def get_all_vars(self):
        # Obtiene todas las variables
        query_get_all_vars = (
                    '{'
                    '  "query": {'
                    '    "match_all": {}  '
                    '  }'
                    '}' 
        )
        try: variables = self.es.search(index='var_def', body=query_get_all_vars )
        except Exception as e: 
            print("Error fatal no se pudieron recuperar las variables")
            print(e)
            exit()

        return variables

    def save_evaluation(self, evaluation):
        history = {
                    "tenant"           : self.tenant,
                    "varname"          : self.varname,
                    "value"            : self.currval,
                    "timestamp"        : self.time_currval,
                    "evaluation"       : evaluation
                }
        res = self.es.index(index='var_hist', doc_type='def', body=history ) 
        return res

    def get_last_ts(self):
        query_get_last_ts = (
                                '{'
                                '  "query": { '
                                '    "bool": {'
                                '    "must": ['
                                '        { "match": { "tenant": "' + self.tenant  +'" }}, '
                                '        { "match": { "varname": "'+ self.varname +'" }}'
                                '           ] '
                                '     }'
                                '  }, "size": 1,'
                                '  "sort": [ {"timestamp": {"order": "desc"} } ]'
                                '}'
                            )
        #print(query_get_last_ts)
        last_ts = 0
        try:
            lts = self.es.search(index='var_hist', body=query_get_last_ts )
            last_ts = lts['hits']['hits'][0]['_source']['timestamp']
        except Exception as e: 
            print("Error fatal no se pudo recuperar ultima medicion")
            print(e)
        
        return last_ts

    def get_prono_type(self):
        return self.prono_type
=======
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
    ''' Variable para la cual se requiere alertar
        El identificador de cada Variable es tenant + varname ''' 
    
    def __init__(self, tenant, varname):
        ''' Obtiene parametros por defecto y Se conecta a ES '''
        self.tenant  = tenant
        self.varname = varname
        # Lee configuraciones
        try:
            currdir = os.getcwd()
            with open(currdir + "/config.yml", 'r') as ymlfile:
                self.cfg = yaml.safe_load(ymlfile)
        except Exception as e:
            print("Error fatal, no se pudo leer el archivo de las configuraciones")
            print(e)
            exit()

        self.nodos        = self.cfg['cluster_es']['nodos']
        self.clustername  = self.cfg['cluster_es']['clustername']
        
        # Coneccion al cluster         
        try:
            #print("coneccion a ES ...")
            self.es = Elasticsearch(self.nodos, timeout=3)
        except Exception as e:
            print(e)
            sys.exit("No se pudo conectar, se aborta.")
                
    def get_criterio(self):   
        # Obtiene definiciones de criterio de la variable
        query_get_query = (
                    '{'
                    '  "query": {'
                    '    "bool": {'
                    '      "must": [ '
                    '           { "exists": { "field": "varname" } },'
                    '			{ "match": {"tenant": "' + self.tenant  +'"}},'
                    '			{ "match": {"varname": "'+ self.varname + '"}'
                    '        }'
                    '      ]'
                    '    }'
                    '  }'
                    '}' 
        )
        
        if DEBUG: 
            print("Buscando definicion de criterio con :\n",query_get_query)
        
        try: self.criterio = self.es.search(index='var_def', body=query_get_query )
        except Exception as e: 
            print("Error fatal no se puedo recuperar la query del criterio")
            print(e)
            exit()

        try: self.query = self.criterio['hits']['hits'][0]['_source']['query']
        except Exception as e: 
            print("Error fatal no se puedo acceder al valor de la query del criterio")
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint( self.criterio )
            print(e)
            exit()

        try:
            try:    self.varname_desc = self.criterio['hits']['hits'][0]['_source']['varname_desc']
            except: self.varname_desc = "Sin descripcion"

            try:    self.prono_type   = self.criterio['hits']['hits'][0]['_source']['prono_type']
            except: self.prono_type   = self.cfg['defaults']['prono_type']  # 'F' =  Formula / "D" = Discreto          
            
            if ( self.prono_type == 'F' ):
                try:  self.formula = self.criterio['hits']['hits'][0]['_source']['formula'] 
                except Exception as e:
                    print(e)

            try:    self.lapso         = self.criterio['hits']['hits'][0]['_source']['lapse']
            except: self.lapso         = self.cfg['defaults']['lapse']               

            self.veces_alarmas = 0    # Inicializa las alarmas en cero             
            self.veces_warn    = self.cfg['defaults']['times_warn'] 
            self.veces_alert   = self.cfg['defaults']['times_alert'] 
            self.umbral_type   = self.cfg['defaults']['umbral_type'] # 'porcentual' / 'fix'
            self.percent       = 0.01 

            if (self.prono_type == 'E'):
                self.external = self.criterio['hits']['hits'][0]['_source']['external']
           
            if DEBUG: 
                # Impresion formateada de criterio 
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.criterio )
                print ("Query recuperada para buscar valor actual, tenant:[",self.tenant,"] variable:[",self.varname,"]")
                print ("Criterio:", self.criterio['hits']['hits'][0]['_source']['query'] )            
        except Exception as e:
            print("Error:\nNo se recupero toda la info necesaria para la variable ["+self.varname+"] tenant ["+self.tenant+"]")
            print(e)
            alert_internal_problem(self.tenant, self.varname)                

        return self.criterio
    
    def get_current_value(self):
        # Obtiene valor actual para la variable mediante la query almacenada en criterio
        if ( self.prono_type == 'F'):  
            query_criterio = self.criterio['hits']['hits'][0]['_source']['query']
            # Ejecuta la consulta para traer el valor actual de la variable monitoreada 
            res               = self.es.search(body=query_criterio)
            self.currval      = res['hits']['total'] 

        if ( self.prono_type == 'E'):
            #toexec = "bash /home/es_alert/src/" + self.external # mnav_total.sh
            toexec = "bash " + self.external
            self.currval = os.popen(toexec).read()  
            self.currval = self.currval.rstrip()

        self.time_currval = util.get_seg_epoch_now()
        return self.currval

    def save_current_value(self):
        # Guarda en forma persistente valor medido (para mantener Historia de la variable)
        history = {
                    "tenant"           : self.tenant,
                    "varname"          : self.varname,
                    "value"            : self.currval,
                    "timestamp"        : self.time_currval
                }
        try:
            res = self.es.index(index='var_hist', doc_type='def', body=history ) 
        except Exception as e:
            print(e.info)
        return res

    def get_pronostico(self, t_seg_epoch):
        # Obtiene valor pronosticado para ese instante o intervalo de tiempo 
        # ------------------------------------------------------------------
        if ( self.prono_type == 'F'):                   
            # Pronostico basado en Formula
            t = t_seg_epoch
            try:
                self.ev = eval( self.formula )
                print ("*** valor estimado de [",self.varname,"] ", " tenant: [", self.tenant,"]")
                print ("*** usando formula : [", self.formula," ] = ", self.ev)
                print ("*** en t[seg epoch]: ", t, " | hh:mm:", util.get_utc_hora_min(t) )
            except Exception as e:
                print(e)
                print("Error:\nNo se pudo usar la formula la variable ["+self.varname+"] tenant ["+self.tenant+"]")
                self.ev = 0
        else:
            # Pronostico basado en registros en ES            
            # inicio_i = int(utc_hhmm[:2]) * self.lapso    
            # inicio   = str( inicio_i )                 # HHMM de Inicio del Lapso
            # fin      = str( inicio_i + self.lapso )    # HHMM de Fin del Lapso
            # self.query_pronostico = ('{'
            #                             '"query": {'
            #                             '    "bool": {'
            #                             '    "must": ['
            #                             '        { "term": {"tenant": "'  + self.tenant + '"}}, '
            #                             '        { "term": {"variable": "'+ self.varname + '"}},'
            #                             '        { "range": { "ts_ini": { "gte": "'+inicio+'", "lte": "'+fin+'" } } }'
            #                             '    ]'
            #                             '    }'
            #                             '}}'
            #         )

            t_seg_epoch_str = str(t_seg_epoch)
            self.query_pronostico = ('{ "query": { "bool":  '
                                        '              { "must": [  '
                                        '			  { "match": { "tenant": "'  + self.tenant + '" } }, '
                                        '			  { "match": { "varname": "' + self.varname + '" } }, '
                                        '			  { "range": { "ts_ini": { "lt": "'+t_seg_epoch_str+'" } } }, '
                                        '			  { "range": { "ts_end": { "gt": "'+t_seg_epoch_str+'" } } } '
                                        '						] '
                                        '} } }'
             )
            if DEBUG: print ("buscando pronostico con la consulta:", self.query_pronostico, " ...")
            self.pronostico = self.es.search(index='criteria', doc_type='prono', body=self.query_pronostico )             
            #---------------------------------------------------------------------------------------------------
            if DEBUG:
                print("\nPronostico para el rango de ese instante:")
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint( self.pronostico )
                print("\n*** Total filas recuperadas:", self.pronostico['hits']['total'] )
            
            self.total_retrieved = self.pronostico['hits']['total']
            if (  self.total_retrieved > 0 ):
                self.ev = self.pronostico['hits']['hits'][0]['_source']['estimated_value']
            else:
                utc_time = util.get_utc_hora_min(t_seg_epoch)
                print("*** No se encontraron pronosticos para:", self.tenant, self.varname, " epoch:",t_seg_epoch," hora:", utc_time)
                self.ev = -1
            #---------------------------------------------------------------------------------------------------
        return  self.ev

    def get_umbral(self, seg_timestamp):
        ''' Obtiene Umbrales para alarmar '''
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

    def reducer(self):
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

    def insert_prono(self, pronostic):
        res = self.es.index(index='var_prono', doc_type='def', body=pronostic ) 
        return res

    def create_criterio(self, varname_desc, query, prono_type, formula, lapso, umbral_type, umbral_factor_1=None, umbral_factor_2=None ):   
        
        if (varname_desc is None):
            print("varname_desc es obligatoria, se aborta registro")
            return 
        
        if (query is None):
            print("query es obligatoria, se aborta registro")
            return 
        
        if (prono_type is None):
            print("Tipo de pronostico [prono_type] es obligatorio, se aborta registro")
            return 
        
        if ( prono_type == 'F'):
            if ( formula is None ):
                print("dado qe el pronostico es por formula, esta es obligatoria, se abora registro")
                return 
        
        if ( lapso is None ):
            lapso = self.cfg['defaults']['lapse']   # Se usa el default general
        
        #if ( veces_warn is None):         
        veces_warn    =  self.cfg['defaults']['times_warn'] 
        #if ( veces_alert is None):
        veces_alert   =  self.cfg['defaults']['times_alert'] 
        
        #umbral_type'porcentual' / 'fix'
        #if ( umbral_type == 'porcentual'):

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
                "umbral_factor_1"   : umbral_factor_1,
                "umbral_factor_2"   : umbral_factor_2,
                "alarm_count"       : 0    # Inicializa las alarmas en cero    
        }
        
        try:
            self.es.index(index='var_def', doc_type='def',body=body )
        except Exception as e:
            print(e)
            print("Error:\nNo se pudo crear la definicion de la variable ["+self.varname+"] tenant ["+self.tenant+"]")


    def __str__(self):
        try: self.formula
        except: self.formula ='sin formula'

        salida = "tenant:"+self.tenant + ", varname:" + self.varname + ", varname_desc:" \
                + self.varname_desc + ",\nquery:" + self.query \
                + "prono_type: "+self.prono_type + ", formula: " +self.formula + ", umbral_type:" \
                + self.umbral_type
        return salida


    def get_all_vars(self):
        # Obtiene todas las variables
        query_get_all_vars = (
                    '{'
                    '  "query": {'
                    '    "match_all": {}  '
                    '  }'
                    '}' 
        )
        try: variables = self.es.search(index='var_def', body=query_get_all_vars )
        except Exception as e: 
            print("Error fatal no se pudieron recuperar las variables")
            print(e)
            exit()

        return variables

    def save_evaluation(self, evaluation):
        history = {
                    "tenant"           : self.tenant,
                    "varname"          : self.varname,
                    "value"            : self.currval,
                    "timestamp"        : self.time_currval,
                    "evaluation"       : evaluation
                }
        res = self.es.index(index='var_hist', doc_type='def', body=history ) 
        return res

    def get_last_ts(self):
        query_get_last_ts = (
                                '{'
                                '  "query": { '
                                '    "bool": {'
                                '    "must": ['
                                '        { "match": { "tenant": "' + self.tenant  +'" }}, '
                                '        { "match": { "varname": "'+ self.varname +'" }}'
                                '           ] '
                                '     }'
                                '  }, "size": 1,'
                                '  "sort": [ {"timestamp": {"order": "desc"} } ]'
                                '}'
                            )
        #print(query_get_last_ts)
        last_ts = 0
        try:
            lts = self.es.search(index='var_hist', body=query_get_last_ts )
            last_ts = lts['hits']['hits'][0]['_source']['timestamp']
        except Exception as e: 
            print("Error fatal no se pudo recuperar ultima medicion")
            print(e)
        
        return last_ts
>>>>>>> 14497f84242fff000429a47d7da72266289b7678

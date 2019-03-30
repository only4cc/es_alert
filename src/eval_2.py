# Monitoreo y evaluacion, 
# invocacion modulo de alerta para notificacion en caso que corresponde
# usa las definiciones y pronosticos desde el index : criteria
#


import datetime, sys, yaml, pprint
import util
import variable
import pprint

def main(tenant, varname):
    DEBUG = False   # Verbosidad
    DEMO  = False   # Para No digitar tenant, varname :)

    if DEMO:
        tenant  = 'ES'        
        varname = 'tot_docs'   

    # Crea la instancia de la clase "Variable"
    var = variable.Variable(tenant, varname)
    
    # Obtiene "criterio" definido para la variable
    # --------------------------------------------
    var.get_criterio()
    if DEBUG: print (var)

    # Consulta el valor ACTUAL de la variable monitoreada usando la definicion de "criterio"   
    # --------------------------------------------------------------------------------------
    value = var.get_current_value()    
    
    # Almacena registro persistente para la Historia
    print("registrando valor actual para ...")
    print("tenant   :", tenant)
    print("varname  :", varname)
    print("timestamp:", var.time_currval)
    print("currval  :", var.currval)
    var.save_current_value()
    
    # Timestamp de Ahora
    seg_timestamp = util.get_seg_epoch_now()

    if DEBUG: 
        utc_time      = util.get_utc_now()
        print ("A las: [", utc_time, "] el valor medido es:[", value, "]\nEpoch timestamp seg:", seg_timestamp )

if __name__ == '__main__':
    # Variables a evaluar 
    if ( len(sys.argv) == 3 ):
        tenant  = sys.argv[1]    # Cuando la variable es "interna" ie Elasticsearch
        varname = sys.argv[2]    # Nombre de la variable: "tot_docs" que corresponde a total de documentos en ES

    main(tenant, varname)

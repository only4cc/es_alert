#
# Monitoreo y evaluacion, 
# invocacion modulo de alerta para notificacion en caso que corresponde
# usa las definiciones y pronosticos desde el index : criteria
#

import datetime, sys, yaml, pprint
import util
import variable
import pprint
import logging

logging.basicConfig(level = logging.INFO, filename = "/log/eval_2.log", format = '%(asctime)s  %(levelname)-10s %(processName)s  %(name)s %(message)s')

def main(tenant, varname):
    DEBUG = True   # Verbosidad

    # Crea la instancia de la clase "Variable"
    var = variable.Variable(tenant, varname)
    
    # Obtiene "criterio" definido para la variable
    # --------------------------------------------
    var.get_criterio()

    # Consulta el valor ACTUAL de la variable monitoreada usando la definicion de "criterio"   
    # --------------------------------------------------------------------------------------
    value = var.get_current_value()    
    
    # Almacena registro persistente para la Historia
    logging.info("registrando valor actual para ...")
    logging.info("tenant   :"+ tenant)
    logging.info("varname  :"+ varname)
    logging.info("timestamp:"+ str(var.time_currval))
    logging.info("currval  :"+ str(var.currval))

    var.save_current_value()
    
    # Timestamp de Ahora
    seg_timestamp = util.get_seg_epoch_now()

    if DEBUG: 
        utc_time = util.get_utc_now()
        print ("A las: [", utc_time, "] el valor medido es:[", value, "]\nEpoch timestamp seg:", seg_timestamp )
        logging.info("A las: ["+ str(utc_time)+ "] el valor medido es:["+ str(value) + "]\nEpoch timestamp seg:"+ str(seg_timestamp) )

if __name__ == '__main__':
    # Variables a evaluar 
    if ( len(sys.argv) == 3 ):
        tenant  = sys.argv[1]    # ES Cuando la variable es "interna" ie Elasticsearch
        varname = sys.argv[2]    # Nombre de la variable: "tot_docs" que corresponde a total de documentos en ES

    main(tenant, varname)

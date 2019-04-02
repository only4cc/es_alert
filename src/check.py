#
# Verificacion
# invocacion modulo de alerta para notificacion en caso que corresponde
# usa las definiciones y pronosticos desde el index : criteria
#

import datetime, sys, yaml, pprint
import alert
import util
import variable
import pprint
import logging 

logging.basicConfig(level = logging.INFO, filename = "/log/check.log", format = '%(asctime)s  %(levelname)-10s %(processName)s  %(name)s %(message)s')


def main(tenant, varname):

    DEBUG = False   # nivel de Verbosidad

    # Crea la instancia de la clase "Variable"
    var = variable.Variable(tenant, varname)
    
    # Obtiene "criterio" definido para la variable
    # --------------------------------------------
    var.get_criterio()
    if DEBUG: print (var)

    # Consulta el valor ACTUAL de la variable monitoreada usando la definicion de "criterio"   
    # --------------------------------------------------------------------------------------
    value = var.get_current_value()    
       
     # Timestamp de Ahora
    seg_timestamp = util.get_seg_epoch_now()
    
    if DEBUG: 
        utc_time      = util.get_utc_now()
        print ("A las: [", utc_time, "] el valor medido es:[", value, "]\nEpoch timestamp seg:", seg_timestamp )
        logging.info("A las: ["+ str(utc_time)+ "] el valor medido es:["+str(value)+ "]\nEpoch timestamp seg:"+str(seg_timestamp))

    # Obtiene el Pronostico para la variable en ese timestamp
    # -------------------------------------------------------
    value_pron = var.get_pronostico(seg_timestamp)
    if ( value_pron > 0 ):
        [umbral_max, umbral_min] = var.get_umbral(seg_timestamp) 
    else:
        print("Sin pronostico en el lapso de ese instante: ",seg_timestamp)
        logging.info("Sin pronostico en el lapso de ese instante: "+str(seg_timestamp))
        exit()

    # Comparacion
    # -----------
    print("*** comparando el valor actual: [",value,"] con umbrales min: [",umbral_min,"] y max: [", umbral_max,"]")
    print("*** variaciones respecto ubral: %6.4f y %6.4f" % ( (100*value / umbral_min), (100*value / umbral_max) ) )
    if ( value < umbral_max and value > umbral_min ):
        var.reducer()
        print("anomalias consecutivas:",var.veces())
        print("Ok")
    else:
        var.acumula()
        veces_warn  = var.get_veces_warn()
        veces_alert = var.get_veces_alert()
        print("anomalias consecutivas:",var.veces())
        
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
	
    evaluation = 'pendiente ...'
    var.save_evaluation(evaluation)


if __name__ == '__main__':

    if ( len(sys.argv) == 3 ):
        tenant  = sys.argv[1]    # ES (tenant)
        varname = sys.argv[2]    # Nombre de la variable: "tot_docs" que corresponde a total de documentos en ES
    else:
        logging.error("Error, se esperan 2 parametros: tenant y varname")
        exit()

    main(tenant, varname)

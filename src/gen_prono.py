#
# Genera e Inserta Pronosticos
# Parametros:
#   tenant
#   varname
#   timestamp desde y timestamp hasta en segundos epoch
#   lapso : cada cuanto generar otro intervalo
#

import datetime, sys, yaml, pprint
import util
import variable

def insert_pronostico(var, tenant, varname, ti, tf, valor_pronostico):
    """ insert_pronostico : Crear en ES con los valores pronosticados """
    print("Insertando en ES:", tenant, varname, ti, tf, valor_pronostico)
    pronostic = {
                    "tenant"           : tenant,
                    "varname"          : varname,
                    "estimated_value"  : valor_pronostico,
                    "ts_ini"           : ti,
                    "ts_end"           : tf
                }
    print("Pronostico:\n",pronostic)
    try:
        resp = var.insert_prono(pronostic)   
    except Exception as e:
        print("Error:\n",e)
    return resp


def genera_pronostico(var, tenant, varname, ti_from, tf_to, lapso):
    ''' 
       genera_pronostico : Crea las entradas en ES con los valores pronosticados
       para cada lapso de tiempo en el intervalo desde-hasta
    ''' 

    tipo_prono = var.get_prono_type()
    print("tipo pronostico:", tipo_prono)
    #if ( tipo_prono == 'F' ):
    #   fn  = var.get_formula()
    #   if ( len(fn) < 2 ):
    #       print("No esta definida la formula, no se puede generar el pronostico")
    #       exit()

    t = ti_from
    while ( t < tf_to):
        tt = util.get_utc_hora_min(t)
        #if ( tipo_prono == 'F' ):
        #    valor_pronostico = eval(fn)
        #if ( tipo_prono == 'E' ):
        valor_pronostico = var.get_pronostico(t)  

        print(tenant, varname, ' : ', tt, end = "\t")
        print(datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'), end = "\t")
        print("pronostico:", valor_pronostico)
        t_sig = t + lapso
        insert_pronostico(var, tenant, varname, t, t_sig, valor_pronostico)
        t = t_sig 
            

def main(tenant, varname, ti_from, tf_to, lapso):
    try:
        var = variable.Variable(tenant, varname)
    except Exception as e:
        print(e, "no se pudo conectar a ES")
        exit()

    var.get_criterio()
    print(var)  
    ti_from = int(ti_from)
    tf_to   = int(tf_to)
    print ("generacion de pronosticos para "+tenant+"."+varname+" desde:",ti_from, " hasta:",tf_to )
    print ("desde:",util.get_utc_hora_min(ti_from)," hasta:",util.get_utc_hora_min(tf_to) )

    genera_pronostico(var, tenant, varname, ti_from, tf_to, lapso )


if __name__ == '__main__':

    DEMO  = False    # Para No digitar parametros ...  tenant, varname, etc.  
    if DEMO:
        tenant  = 'ES'          
        varname = 'tot_docs'
        ti_from = datetime.datetime.now().timestamp()
        tf_to   = ti_from + (24*60*60)   # 24 es para 24 Horas
        lapso   = 600  # Cada 10 min

    #for i in range (0, len(sys.argv)):
    #    print(i,sys.argv[i])

    if ( len(sys.argv) == 6 ):
        tenant  = sys.argv[1]    # Cuando la variable es "interna" ie Elasticsearch
        varname = sys.argv[2]    # Nombre de la variable
        ti_from = sys.argv[3]    # Fecha desde en epoch segundos <----
        tf_to   = sys.argv[4]    # Fecha hasta en epoch segundos <----
        lapso   = int(sys.argv[5])    # lapso en segundos
    else:
        print(tenant, varname, ti_from, tf_to, lapso)
        print("se aborta. numero de parametros:", len(sys.argv), " se esperan 6")
        exit()

    main(tenant, varname, ti_from, tf_to, lapso)

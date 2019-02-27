#
# Genera e Inserta Pronosticos
# Parametros:
#   tenant, 
#   varname
#   timestamp desde y timestamp hasta en segundos epoch
#
import datetime, sys, yaml, pprint
import util
import variable

def insert_pronostico(var, tenant, varname, ti, tf, valor_pronostico):
    print("Insertando en ES:", tenant, varname, ti, tf, valor_pronostico)
    pronostic = {
                "tenant"           : tenant,
                "varname"          : varname,
                "estimated_value"  : valor_pronostico,
                "ini"              : ti,
                "fin"              : tf
        }
    print("Pronostico:\n",pronostic)
    try:
        resp = var.insert_prono(pronostic)   
    except Exception as e:
        print("Error:\n",e)
    return resp


def genera_pronostico(var, tenant, varname, ti_from, tf_to):
    ''' genera_pronostico : Crea las entradas en ES con los valores pronosticados
    para cada lapso de tiempo (dese-hasta)''' 
    var.get_criterio()
    fn      = var.get_formula()
    lapse   = var.get_lapse()
    t = ti_from
    while ( t < tf_to):
        tt = util.get_utc_hora_min(t)
        valor_pronostico = eval(fn)
        print(tenant, varname, ' : ', tt, end = "\t")
        print(datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'), end = "\t")
        print(valor_pronostico)
        t_sig = t + lapse*60 # Para llevarlo a segundos
        insert_pronostico(var, tenant, varname, t, t_sig, valor_pronostico)
        t = t_sig 
            

def main():
    DEMO  = True    # Para No digitar tenant, varname :)

    if ( len(sys.argv) == 4 ):
        tenant  = sys.argv[1]    # Cuando la variable es "interna" ie Elasticsearch
        varname = sys.argv[2]    # Nombre de la variable: 
        ti_from = sys.argv[3]    # Fecha desde en epoch segundos <----
        tf_to   = sys.argv[4]    # Fecha hasta en epoch segundos <----

    if DEMO:
        tenant  = 'ES'          
        varname = 'tot_docs'
        ti_from = datetime.datetime.now().timestamp()
        tf_to   = ti_from + (2*60*60)   # 2 es para 2 Horas

        print("Prueba con tiempos y fechas.")
        fecha = "2018-10-31T13:30" 
        ts    = util.get_seg_epoch_from_date(fecha)
        print("fecha:", fecha, "ts:", ts)
        print("HH:MM :",util.get_utc_hora_min(ts))
        
    try:
        var = variable.Variable(tenant, varname)
    except Exception as e:
        print(e, "no se pudo conectar a ES")

    print ("generacion de pronosticos para "+tenant+"."+varname+" desde:",ti_from, util.get_utc_hora_min(ti_from),"hasta:",tf_to, util.get_utc_hora_min(tf_to))
    genera_pronostico(var, tenant, varname, ti_from, tf_to )


if __name__ == '__main__':
    main()
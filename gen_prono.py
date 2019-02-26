#
# Genera e Inserta Pronosticos
# Parametros:
# tenant, varname
# timestamp desde y timestamp hasta
#
import datetime, sys, yaml, pprint
import util
import variable

def insert_pronostico(tenant, varname, t, valor_pronostico):
    print("insertando en ES: ", tenant, varname, t, valor_pronostico)
    pass

def gen_pronostic(tenant, varname, ti_from, tf_to):
    var     = variable.Variable(tenant, varname)    
    var.get_criterio()
    fn 	    = var.get_formula()
    lapse 	= var.get_lapse()
    t = ti_from
    while ( t < tf_to):
        tt = util.get_utc_hora_min(t)
        print(tenant, varname, ' : ', tt, end = "\t")
        print(datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S'), end = "\t")
        valor_pronostico = eval(fn)
        print(valor_pronostico)
        insert_pronostico(tenant, varname, t, valor_pronostico)
        t = t + lapse*60 # Para llevarlo a segundos
			
def main():
	DEMO  = True    # Para No digitar tenant, varname :)

	if ( len(sys.argv) == 4 ):
		tenant  = sys.argv[1]    # Cuando la variable es "interna" ie Elasticsearch
		varname = sys.argv[2]    # Nombre de la variable: 
		ti_from = sys.argv[3]    # Fecha desde en epoch segundos
		tf_to   = sys.argv[4]	 # Fecha hasta en epoch segundos

	if DEMO:
		tenant  = 'ES'          
		varname = 'tot_docs'   	
		ti_from = datetime.datetime.now().timestamp()
		tf_to   = ti_from + 2 * 60 * 60 

	print ("generacion de pronosticos para "+tenant+"."+varname+" desde:",ti_from, util.get_utc_hora_min(ti_from),"hasta:",tf_to, util.get_utc_hora_min(tf_to))
	gen_pronostic(tenant, varname, ti_from, tf_to )


if __name__ == '__main__':
    main()
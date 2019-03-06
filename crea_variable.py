import easygui
import variable

DEBUG = False

title = 'Creacion de Definiciones de Variables'

tenant       = 'BE'          
varname      = 'alguna_metrica'
varname_desc = 'Alguna Metrica de Ejemplo'
query        = 'la consulta aca ...'
prono_type   = 'F|D - F:Formula| D:Discreto' 
formula      = 'ejemplo: 1000 * t - 555  (t representa el timestamp en segundos epoch)'
umbral_type  = 'percent' 
umbral_factor_1 = 1.001
umbral_factor_2 = 1.010
lapso        = (15*60)

fieldNames = [ 'tenant', 'varname', 'varname_desc', 'query', 'prono_type', \
               'formula', 'umbral_type', 'umbral_factor_1', 'umbral_factor_2' ]

fieldValues = [ tenant, varname, varname_desc, query, prono_type, \
                formula, umbral_type, umbral_factor_1, umbral_factor_2 ]

# validaciones

errmsg = ""
fieldValues = easygui.multenterbox(errmsg, title, fieldNames, fieldValues)

if DEBUG:
    print ("La respuesta fue:", fieldNames, fieldValues)

var = variable.Variable(tenant, varname)
res = var.create_criterio(varname_desc, query, prono_type, formula, lapso, \
                            umbral_type, umbral_factor_1, umbral_factor_2)   

print(res)
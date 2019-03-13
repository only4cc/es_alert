import easygui
import variable

DEBUG = False

title = 'Creacion de Definiciones de Variables'

# Definicion de Campos y sus Defaults
tenant       = 'BE'          
varname      = 'alguna_metrica'
varname_desc = 'Alguna Metrica de Ejemplo'
query        = 'aca va la consulta en formato DSL de ES ... escapar los "'
prono_type   = 'F|D - F:Formula| D:Discreto' 
formula      = 'ejemplo: 1000 * t - 555  (t representa el timestamp en segundos epoch)'
umbral_type  = 'percent' 
umbral_factor_1 = 1.001
umbral_factor_2 = 1.010
lapse           = (5*60)

fieldNames = [ 'tenant', 'varname', 'varname_desc', 'query', 'prono_type', \
               'formula', 'umbral_type', 'umbral_factor_1', 'umbral_factor_2', 'lapse' ]

fieldValues = [ tenant, varname, varname_desc, query, prono_type, \
                formula, umbral_type, umbral_factor_1, umbral_factor_2, lapse ]





errmsg = ""
fieldValues = easygui.multenterbox(errmsg, title, fieldNames, fieldValues)

if DEBUG:
    print ("La respuesta fue:", fieldNames, fieldValues)

#for f in range(len(fieldNames)):
#	print ("f:",f, fieldNames[f], fieldValues[f])
#    toev = fieldNames[f] + '=' + "'"+ str( fieldValues[f] )+ "'"
#    eval( toev )

# Asignacion de valores capturados a variables
tenant          = fieldValues[0]        
varname         = fieldValues[1] 
varname_desc    = fieldValues[2] 
query           = fieldValues[3] 
prono_type      = fieldValues[4] 
formula         = fieldValues[5] 
umbral_type     = fieldValues[6] 
umbral_factor_1 = fieldValues[7] 
umbral_factor_2 = fieldValues[8] 
lapse           = fieldValues[9] 

# validaciones ..

# Crea la variable en ES
var = variable.Variable(tenant, varname)
res = var.create_criterio(varname_desc, query, prono_type, formula, lapse, \
                            umbral_type, umbral_factor_1, umbral_factor_2)   


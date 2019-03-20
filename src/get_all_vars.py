#
# Itera sobre las variables y para c/u ejecutala evaluacion si por tiempo le corresponde
#

from variable import Variable
import util
import os

tenant  = ''
varname = ''
var = Variable(tenant,varname)
variables = var.get_all_vars()

for i in range( 0, len(variables['hits']['hits'])):
    tenant  = variables['hits']['hits'][i]['_source']['tenant']
    varname = variables['hits']['hits'][i]['_source']['varname']
    lapse   = variables['hits']['hits'][i]['_source']['lapse']
    
    print(  variables['hits']['hits'][i]['_source']['tenant'], 
            variables['hits']['hits'][i]['_source']['varname'],
            variables['hits']['hits'][i]['_source']['lapse'] )

    now     = util.get_seg_epoch_now()
    
    var_last_ts = Variable(tenant, varname)
    last_ts = var_last_ts.get_last_ts()  #### <========= obtiene el timestamp de la ultima medicion 
    print ("Ultimo instante:", last_ts)
    if ( now - last_ts >= lapse ):
        print("evaluare :", tenant, varname)
        #ejecutar_eval_2( tenant, varname )
        #print os.system('... docker eval_2.sh tenant varname')


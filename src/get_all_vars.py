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
    
    print(  variables['hits']['hits'][i]['_source']['tenant'], 
            variables['hits']['hits'][i]['_source']['varname'] )

    

from variable import Variable

var = Variable('', '')

variables = var.get_all_vars()

for i in range( 0, len(variables['hits']['hits'])):
    print( variables['hits']['hits'][i]['_source']['tenant'], variables['hits']['hits'][i]['_source']['varname'] )


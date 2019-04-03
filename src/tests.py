import time
import util
from variable import Variable

def print_var(tenant,varname): 
    print("\nusando --> tenant:", tenant," varname:", varname)

class tests:
  
    print("test_FindVariable")
    tenant  = 'ES'
    varname = 'tot_docs'
    print_var(tenant, varname)
    var = Variable(tenant, varname)

    tenant  = 'BE'
    varname = 'mnav_total'
    print_var(tenant, varname)
    var2 = Variable(tenant, varname)

    print("test_GetCurrentValue")
    tenant  = 'ES'
    varname = 'tot_docs'
    var4 = Variable(tenant, varname)
    print_var(tenant, varname)
    var4.get_criterio()
    currvar = int(var4.get_current_value()) 
    print("Valor actual:", currvar)
    print(" ")

    tenant  = 'BE'
    varname = 'mnav_total'
    var5 = Variable(tenant, varname)
    print_var(tenant, varname)
    var5.get_criterio()
    currvar = int(var5.get_current_value()) 
    print("Valor actual:", currvar)

    print("test_Pronosticos")
    tenant  = 'ES'
    varname = 'tot_docs'
    var6 = Variable(tenant, varname)
    print_var(tenant, varname)
    var6.get_criterio()
    ts = util.get_seg_epoch_now()
    prono = var6.get_pronostico(ts)
    print("Valor Pronosticado:", prono)

    print("test_Pronosticos_E")
    tenant  = 'BE'
    varname = 'mnav_total'
    print_var(tenant, varname)
    var7 = Variable(tenant, varname)
    var7.get_criterio()
    ts = util.get_seg_epoch_now()
    prono = var7.get_pronostico(ts)
    print("Valor Pronosticado:", prono)

if __name__ == '__main__':
    tests()

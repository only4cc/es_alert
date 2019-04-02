import unittest
import time
import util
from variable import Variable

def print_var(tenant,varname): 
    print("\nusando --> tenant:", tenant," varname:", varname)

class TestVariable(unittest.TestCase):
  
    def test_FindVariable(self):
        print("test_FindVariable")
        tenant  = 'ES'
        varname = 'tot_docs'
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        self.assertTrue(var,"Existe var")
        self.assertTrue(len(var.get_criterio()) > 3,True)

        tenant  = 'BE'
        varname = 'mnav_total'
        print_var(tenant, varname)
        var2 = Variable(tenant, varname)
        self.assertTrue(var2,"Existe var")
        self.assertTrue(len(var2.get_criterio()) > 3,True)

    def test_NoFindVariable(self):
        print("test_NoFindVariable")
        tenant  = 'ES'
        varname = 'tot_docs_'  
        var3 = Variable(tenant, varname)
        print_var(tenant, varname)
        self.assertTrue(var3,False)

    def test_GetCurrentValue(self):
        print("test_GetCurrentValue")
        tenant  = 'ES'
        varname = 'tot_docs'
        var4 = Variable(tenant, varname)
        print_var(tenant, varname)
        var4.get_criterio()
        currvar = int(var4.get_current_value()) 
        print("Valor actual:", currvar)
        self.assertTrue(currvar > 10000, True)
        print(" ")

        tenant  = 'BE'
        varname = 'mnav_total'
        var5 = Variable(tenant, varname)
        print_var(tenant, varname)
        var5.get_criterio()
        currvar = int(var5.get_current_value()) 
        print("Valor actual:", currvar)
        self.assertTrue(currvar > 10000, True)


    def test_Pronosticos(self):
        print("test_Pronosticos")
        tenant  = 'ES'
        varname = 'tot_docs'
        var6 = Variable(tenant, varname)
        print_var(tenant, varname)
        var6.get_criterio()
        ts = util.get_seg_epoch_now()
        prono = var6.get_pronostico(ts)
        print("Valor Pronosticado:", prono)
        self.assertTrue(int(prono) > 10000, True)

        #time.sleep(10)

    def test_Pronosticos_E(self):
        print("test_Pronosticos_E")
        tenant  = 'BE'
        varname = 'mnav_total'
        print_var(tenant, varname)
        var7 = Variable(tenant, varname)
        var7.get_criterio()
        ts = util.get_seg_epoch_now()
        prono = var7.get_pronostico(ts)
        print("Valor Pronosticado:", prono)
        self.assertTrue(int(prono) > 100, True)

if __name__ == '__main__':
    unittest.main()

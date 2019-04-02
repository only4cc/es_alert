import unittest
import time
import util
from variable import Variable

def print_var(tenant,varname):
    print("usando --> tenant:", tenant," varname:", varname)

class TestVariable(unittest.TestCase):
  
    def test_FindVariable(self):
        print("test_FindVariable")
        tenant  = 'ES'
        varname = 'tot_docs'
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        self.assertTrue(var,"Existe var")
        self.assertTrue(len(var.get_criterio()) > 3,True)
        time.sleep(1)

        tenant  = 'BE'
        varname = 'mnav_total'
        print_var(tenant, varname)
        var = Variable(tenant, varname)
        self.assertTrue(var,"Existe var")
        self.assertTrue(len(var.get_criterio()) > 3,True)
        time.sleep(1)

    def test_NoFindVariable(self):
        print("test_NoFindVariable")
        tenant  = 'ES'
        varname = 'tot_docs_'  # No existe <<<
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        self.assertTrue(var,"No Existe var")
        time.sleep(1)


    def test_GetCurrentValue(self):
        print("test_GetCurrentValue")
        tenant  = 'ES'
        varname = 'tot_docs'
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        var.get_criterio()
        currvar = int(var.get_current_value()) 
        print("Valor actual:", currvar)
        self.assertTrue(currvar > 10000, True)
        time.sleep(1)

        tenant  = 'BE'
        varname = 'mnav_total'
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        var.get_criterio()
        currvar = int(var.get_current_value()) 
        print("Valor actual:", currvar)
        self.assertTrue(currvar > 10000, True)
        time.sleep(1)


    def test_Pronosticos(self):
        print("test_Pronosticos")
        tenant  = 'ES'
        varname = 'tot_docs'
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        var.get_criterio()
        ts = util.get_seg_epoch_now()
        prono = var.get_pronostico(ts)
        print("Valor Pronosticado:", prono)
        self.assertTrue(int(prono) > 10000, True)
        time.sleep(1)

        tenant  = 'BE'
        varname = 'mnav_total'
        var = Variable(tenant, varname)
        print_var(tenant, varname)
        var.get_criterio()
        ts = util.get_seg_epoch_now()
        prono = var.get_pronostico(ts)
        print("Valor Pronosticado:", prono)
        self.assertTrue(int(prono) > 10000, True)

if __name__ == '__main__':
    unittest.main()

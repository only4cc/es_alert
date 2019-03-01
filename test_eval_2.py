import unittest
from variable import Variable

class TestVariable(unittest.TestCase):
  
    def test_FindVariable(self):
        tenant  = 'ES'
        varname = 'tot_docs'
        var = Variable(tenant, varname)

        self.assertTrue(var,"Existe var")
        print("\nlargo de criterio", len(var.get_criterio()))
        self.assertTrue(len(var.get_criterio()) > 3,True)
        self.assertEqual(var.get_current_value() > 10000, True)


if __name__ == '__main__':
    unittest.main()
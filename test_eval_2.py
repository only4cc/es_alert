import unittest
from eval_2 import Variable

class TestVariable(unittest.TestCase):
  
    def test_FindVariable(self):
        tenant  = 'ES'
        varname = 'tot_docs'
        var = Variable(tenant, varname)
        self.assertTrue(var,"Existe var")
        self.assertTrue( len(var.get_criterio()) > 10,"Tiene criterio")
        
#        self.assertIsInstance(self, Variable, "Existe")
#        self.assertEqual(self, 1, "Econtre")

if __name__ == '__main__':
    unittest.main()
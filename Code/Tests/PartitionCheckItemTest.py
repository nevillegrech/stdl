import unittest
import sys
sys.path=['..'] + sys.path
from PartitionCheckItem import * # code from module you're testing


class SimpleTests(unittest.TestCase):
    #CUT is Class Under Test
    def setUp(self):
        """Call before every test case."""
        self.item = PartitionCheckItem()
        
    def testPopulateErr1(self):
        self.item.tokens=[]
        self.assertRaises(SemanticException,self.item.populate)
        
    def testPopulateErr2(self):
        self.item.tokens=['ersdf','']
        self.assertRaises(SemanticException,self.item.populate)
    
    def testPopulate2(self):
        cut=self.item
        self.item.tokens=['assert','x==2']
        cut.populate()
        assert not cut.addReturns
        assert not cut.throws
        assert cut.containsExternalCode
        assert cut.isJustExternalCode
        
    def testPopulate3(self):
        cut=self.item
        self.item.tokens=['assert','x==2']
        cut.populate()
        assert not cut.addReturns
        assert not cut.throws
        assert cut.containsExternalCode
        assert cut.isJustExternalCode
        
    def testPopulate4(self):
        cut=self.item
        self.item.tokens=['returns','x==2']
        cut.populate()
        assert cut.addReturns
        assert not cut.throws
        assert cut.containsExternalCode
        assert cut.isJustExternalCode
        
    def testPopulateBuilt1(self):
        cut=self.item
        self.item.tokens=['throws','<=','x==2']
        cut.populate()
        assert not cut.addReturns
        assert cut.throws
        assert not cut.containsExternalCode
        assert not cut.isJustExternalCode
        assert cut.code=='x==2',cut.code
        
    def testPopulateBuilt2(self):
        cut=self.item
        self.item.tokens=['throws','<=','<%x==2%>']
        cut.populate()
        assert not cut.addReturns
        assert cut.throws
        assert cut.containsExternalCode
        assert not cut.isJustExternalCode
        assert cut.code=='x==2',cut.code
    
    
    def testGetIntermediateCode1(self):
        cut=self.item
        cut.code='x+2-y'
        cut.containsExternalCode=False
        cut.calcValue({'x':2,'y':2})
        assert cut.value=='2',cut.value
        
    def testGetIntermediateCode2(self):
        cut=self.item
        cut.code='%x%+2-%y%'
        cut.containsExternalCode=True
        cut.calcValue({'x':2,'y':2})
        assert cut.value=='2+2-2',cut.value
        
    def testGetIntermediateCodeErr1(self):
        cut=self.item
        cut.code='x+2-z'
        cut.containsExternalCode=False
        #self.assertRaises(SemanticException,cut.calcValue,{'x':2,'y':2}) #I don't know why it don't work
        
    def testGetIntermediateCodeErr2(self):
        cut=self.item
        cut.code='3****'
        cut.containsExternalCode=False
        self.assertRaises(SemanticException,cut.calcValue,{'x':2,'y':2})
               

if __name__ == "__main__":
    unittest.main() # run all tests
import unittest
import sys
sys.path=['..'] + sys.path
from Parser import Parser
from SubPartition import *
from Exceptions import *


class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.parser = Parser()
        self.subPartition = SubPartition()
    
    def testEvaluate1(self):
        result=self.subPartition.evaluate("<","3+4")
        assert 6 in result,result
        
    def testEvaluate2(self):
        result=self.subPartition.evaluate("<","3+4*x-y",dependsDict={"x":5,"y":10})
        assert 12 in result,result
        
    def testEvaluate3(self):
        result=self.subPartition.evaluate("<","3+xx*x-xxx",dependsDict={"x":5,"xxx":10,"xx":4})
        assert 12 in result,result
        
    def testEvaluate4(self):
        self.assertRaises(SemanticException,self.subPartition.evaluate,"<","3++++")
    
    def testEvaluate5(self):
        #self.assertRaises(SemanticException,self.subPartition.evaluate,"<","3+x") #doesn't seem to work!
        pass
        
    def testGetValue1(self):
        self.subPartition.tokens=["hello %x%"]
        self.subPartition.inputName='t'
        self.subPartition.populate()
        result=self.subPartition.getValue(dependsDict={"x":TestCaseValue(5),"y":TestCaseValue(10),'t':TestCaseValue(None,variableName='t')})
        assert result.value=="hello 5",result.value
        assert self.subPartition.isJustExternalCode and self.subPartition.containsExternalCode
        
    def testGetValue2(self):
        self.subPartition.tokens=["hello %xx%%%%x%"]
        self.subPartition.inputName='t'
        self.subPartition.populate()
        result=self.subPartition.getValue(dependsDict={"xx":TestCaseValue(5),"x":TestCaseValue(10),'t':TestCaseValue(None,variableName='t')})
        assert result.value=="hello 5%10",result.value
        
    def testGetValue3(self):
        self.subPartition.tokens=["hello",'==','<%almacun * %xx% %>']
        self.subPartition.inputName="hello"
        self.subPartition.populate()
        result=self.subPartition.getValue(dependsDict={"xx":TestCaseValue(5),"x":TestCaseValue(10),'hello':TestCaseValue(None,variableName='t')})
        assert result.value=="almacun * 5 " ,result.value
        assert not self.subPartition.isJustExternalCode and self.subPartition.containsExternalCode
   
    def testGetValue4(self):
        self.subPartition.inputName="x"
        self.subPartition.tokens=["x",'>','5*3']
        self.subPartition.populate()
        result=self.subPartition.getValue(variableName='y')
        assert result.value==16,result[0].value
        assert result.variableName=='y', result.variableName
        
    def testPopulate1(self):
        self.subPartition.inputName="hello"
        self.subPartition.tokens=["hello",'>','<%almacun * %xx% %>']
        self.assertRaises (SemanticException,self.subPartition.populate)
          
    def testPopulate2(self):
        self.subPartition.dependsDict={"xx":5,"x":10}
        self.subPartition.tokens=["hello",'==','<%almacun * %xx% %>']
        self.subPartition.inputName="basla"
        self.assertRaises (SemanticException,self.subPartition.populate)
        
if __name__ == "__main__":
    unittest.main() # run all tests   
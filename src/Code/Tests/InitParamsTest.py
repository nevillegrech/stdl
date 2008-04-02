import unittest
import sys
sys.path=['..'] + sys.path
from Parser import Parser # code from module you're testing
from InitParams import *
from Exceptions import *

class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.parser = Parser()
        self.initParams=InitParams()
        
    def genericTest(self,test="",delimitedParams=None, requiredParams=None, possibleParams=None):
        if delimitedParams is not None:
            self.initParams.delimitedParams=delimitedParams
        if possibleParams is not None:
            self.initParams.possibleParams=possibleParams
        if requiredParams is not None:
            self.initParams.requiredParams=requiredParams
        self.initParams.tokens=self.parser.initSection.parseString(test)[0]
        self.initParams.populate()
        
    def testNormalParams(self):
        test="""\
        init:
        import: x,y,z #hello
        export: x1
        break: 899"""
        delimitedParams=["import","export"]
        requitedParams=["break"]
        self.genericTest(test,delimitedParams,requitedParams,delimitedParams+requitedParams)
        param=self.initParams.params["import"][1]
        assert param=="y",param
        param=self.initParams.params["export"][0]
        assert param=="x1",param
        
    def testMissingParam(self):
        test="""\
        init:
        import: x,y,z #hello
        export: x1
        """
        delimitedParams=["import","export"]
        requitedParams=["break"]
        self.assertRaises(SemanticInitException,self.genericTest,test,delimitedParams,requitedParams,delimitedParams+requitedParams)
        
    def testExtraParam(self):
        test="""\
        init:
        import: x,y,z #hello
        export: x1
        break: 899
        zingu: ghasafar
        """
        delimitedParams=["import","export"]
        requitedParams=["break"]
        self.assertRaises(SemanticInitException,self.genericTest,test,delimitedParams,requitedParams,delimitedParams+requitedParams)
        
if __name__ == "__main__":
    unittest.main() # run all tests

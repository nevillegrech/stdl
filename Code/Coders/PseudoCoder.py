from PartitionCheck import PartitionCheck
from PartitionCheckItem import PartitionCheckItem
from TestCaseValue import TestCaseValue
from ICoder import *

class PseudoCoder(ICoder):
    """A simple coder which produces a verbose pseudo-output """

    #----------------------------------------------------------------------
    extension='.txt'
    def __init__(self):
        """Constructor"""
        self.code=""
    
    def setInitparams(self,params):
        pass
    
    def addTest(self,suite,test,method,returns):
        code=['**********************************************************************\n']
        code.append('Test %s on method %s which returns %s\n'%(test,method,returns))
        for tc in suite:
            code.append('=======================================================================\n')
            for v in tc[1:]:
                assert isinstance(v,TestCaseValue)
                if not v.isJustExternalCode:
                    code.append('%s = '%v.variableName)
                code.append(str(v.value))
                code.append('\n----------------------\n')
            code.append('============================CHECKS=====================================\n')
            check=tc[0]
            assert isinstance(check,PartitionCheck)
            for checkItem in check.getCheckItems(tc[1:]):
                assert isinstance(checkItem,PartitionCheckItem)
                code.append('assert %s %s %s\n'%('returns' if checkItem.addReturns else '', checkItem.comparator, checkItem.value))
        code.append('\nTotal tests: %s test cases'%str(len(suite)))
        self.code="".join(code)

    def getCode(self):
        return self.code
    
    
    
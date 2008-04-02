import unittest
import sys
sys.path=['..'] + sys.path
from Parser import Parser # code from module you're testing
from DependsOn import *
from Exceptions import *

class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.parser = Parser()
        self.dependsOn = DependsOn()
    
    def testPopulate1(self):
        cut=self.dependsOn
        cut.tokens=[]
        cut.populate()
        assert len(cut)==0, len(cut)
        assert not cut
        
    def testPopulate2(self):
        cut=self.dependsOn
        test="""\
        dependsOn x1,x2,y1,y2:
            <%
            c1=new ArrayList();
            c1.add(new Point(%x1%,%y1%));
            c1.add(new Point(%x2%,%y2%));
            %>
            <% %>
        out:
            returns >= (x1+y1) - (x2-y2)
        error:
            throws > 3"""
        cut.tokens=self.parser.dependsOn.parseString(test)[0]
        cut.populate()
        assert len(cut.subPartitions)==2
        assert len(cut)==4,len(cut)
        assert len(cut.outPartitionCheck)==1
        assert len(cut.errorPartitionCheck)==1
    
    def testPopulateErr(self):
        cut=self.dependsOn
        test="""\
        dependsOn x1,x2,y1,y2:
            <%
            c1=new ArrayList();
            c1.add(new Point(%x1%,%y1%));
            c1.add(new Point(%x2%,%y2%));
            %>
        error:
            throws > 3
            returns < 2"""
        cut.tokens=self.parser.dependsOn.parseString(test)[0]
        self.assertRaises(SemanticException,cut.populate)
        
    def getTestSuite1(self):
        #Mock Objects
        out1=PartitionCheck()
        out1.notEmpty, out1.throws, out1.valid, out1.out=True, False, True, True
        check1=PartitionCheckItem()
        check1.addReturns, check1.code, check1.comparator = True, 3, '>'
        check2=PartitionCheckItem()
        check2.addReturns, check2.code, check2.comparator = True, 4, '>'
        out1.checkItems=[check1,check2]
        out2=PartitionCheck()
        out2.notEmpty, out2.throws, out2.valid, out2.out=True, False, True, True
        out2.checkItems=[check2]
        check1=PartitionCheckItem()
        check1.addReturns, check1.code, check1.comparator = True, 2, '<'
        check2=PartitionCheckItem()
        check2.addReturns, check2.code, check2.comparator = True, 4, '<'
        dic1=[out1,TestCaseValue(5,0,True,'a'),TestCaseValue(3,0,True,'b'),TestCaseValue(4,0,True,'c')]
        dic2=[out2,TestCaseValue(5,0,True,'a'),TestCaseValue(4,0,True,'b'),TestCaseValue(2,1,True,'c')]
        return [dic1,dic2]
        
    def testPutValues1(self):
        testSuite=self.getTestSuite1()
        #DependsOn object
        cut=self.dependsOn
        test='''\
        dependsOn a,b:
          d==34
          d<a + b
        out:
          returns > d
        '''
        cut.inputName='d'
        cut.tokens=self.parser.dependsOn.parseString(test)[0]
        cut.populate()
        cut.valueStart=2
        testSuite[0].append(TestCaseValue(index=3))
        testSuite[1].append(TestCaseValue(index=3))
        cut.putValues(testSuite[0],4)
        cut.putValues(testSuite[1],4)
        assert testSuite[0][4].value==7,testSuite[0][4]
        assert testSuite[1][4].value==8,testSuite[1][4]
        assert len(testSuite[0][0].checkItems)==3,len(testSuite[0][0].checkItems)
        assert len(testSuite[1][0].checkItems)==2,len(testSuite[1][0].checkItems)
        
    def testPutValues2(self):
        testSuite=self.getTestSuite1()
        #DependsOn object
        cut=self.dependsOn
        test='''\
        dependsOn a,b:
          d<a + b
          d==a+2
          d==b-2
        out:
          returns > d
        error:
          returns < 0
          returns < b - a
        '''
        cut.inputName='d'
        cut.tokens=self.parser.dependsOn.parseString(test)[0]
        cut.populate()
        cut.valueStart=2
        testSuite[0].append(TestCaseValue(index=3))
        testSuite[1].append(TestCaseValue(index=4))
        cut.putValues(testSuite[0],4)
        cut.putValues(testSuite[1],4)
        assert testSuite[0][4].value==7,testSuite[0][4]
        assert testSuite[1][4].value==2,testSuite[1][4]
        #Check out partition check here
        assert len(testSuite[0][0].checkItems)==3
        assert len(testSuite[1][0].checkItems)==2
   
if __name__ == "__main__":
    unittest.main() # run all tests
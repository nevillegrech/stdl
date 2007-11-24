import unittest
import sys
sys.path=['..'] + sys.path
from Exceptions import *
from Parser import Parser,ProgramParser # code from module you're testing


class SimpleTests(unittest.TestCase):

    def setUp(self):
        """Call before every test case."""
        self.parser = Parser()
        
    def testPartition(self):
        test="""be5<=7+5\r\n"""
        parseTree=self.parser.subPartition.parseString(test)
        assert 3 == len(parseTree[0]),parseTree
    
    def testPartition2(self):
        test="""be5<=7+5 #hello world\r\n#hi there\r\n"""
        parseTree=self.parser.subPartition.parseString(test)
        assert 3 == len(parseTree[0]),parseTree

    def testPartition3(self):
        test="""a<4 #jgjhg\r\n\r\nb>6\r\n"""
        parseTree=self.parser.partition.parseString(test)
        assert 2 == len(parseTree[0]),parseTree

    def testValidPartition(self):
        test="""valid 9 (a.b,g.h,u):
a<8 
b>7 
  as>23
"""
        parseTree=self.parser.validPartition.parseString(test)
        assert 2 == len(parseTree[0]),parseTree[0]
        assert parseTree[0][0][1]=='9', parseTree[0][0][1]
        assert parseTree[0][0][2][0][1]=='b',parseTree[0][0][2][0][1]
        assert parseTree[0][0][2][2][0]=='u',parseTree[0][0][2][2][0]
    
    def testOutstmt(self):
        test="""returns=="blablabla" #comment
"""
        parseTree=self.parser.builtInVerif.parseString(test)
        assert 3==len(parseTree), parseTree
        assert parseTree[1]=="==", parseTree[0][1]
        
    def testOutstmts(self):
        test="""returns<%.out()=="blablabla"%> #comment
throws==xi haga lemm
<%%>
"""
        parseTree=self.parser.outStmts.parseString(test)
        assert 3==len(parseTree[0][1]), parseTree
        
    def testPartitionOut(self):
        test="""out:
assert <%testme(455,233);%>
returns<%.out()=="blablabla"%> #comment
throws==xi haga lemm"""
        parseTree=self.parser.partitionOut.parseString(test)
        assert 2==len(parseTree[0]), parseTree[0]
        assert 3==len(parseTree[0][1]), parseTree[0][1]
        assert "testme(455,233);"==parseTree[0][1][0][1],parseTree[0][1][0][1]

    def testEqClasses(self):
        test="""valid 0:
                b>0
                d<9 #as
                out:
                assert <%true
                %>
                invalid 0:
                b==0
                out:
                throws <%.GetType().Name==NullReferenceException%>
                returns==5 #ddd
                """
        parseTree=self.parser.eqClasses.parseString(test)
        assert 2==len(parseTree[0]), parseTree[0]
        
    def testEqClasses(self):
        test="""valid 0:
                b>0
                d<9 #as
                out:
                assert <%true
                %>
                invalid 0:
                b==0
                out:
                throws <%.GetType().Name==NullReferenceException%>
                returns==5 #ddd
                """
        parseTree=self.parser.eqClasses.parseString(test)
        assert 2==len(parseTree[0]), parseTree[0]
        
    def testIDescriptor(self):
        test="""\
        var <%Collection<String>%> a:
        
        """
        parseTree=self.parser.iDescriptor.parseString(test)
        assert 4==len(parseTree[0]), parseTree[0]
        assert parseTree[0][2] == "a", parseTree[0][2]
        
    def testInput1(self):
        test="""\
        var <%Collection<String>%> a:
        valid 0:
          a<3
        out:
          <%true%>
        invalid 0:
          a<5
        out 0:
          throws(a).asdf==awf #hara
        """
        parseTree=self.parser.input.parseString(test)
        assert 3==len(parseTree[0]), parseTree[0]
        assert parseTree[0][1]==[]
        
    def testInput2(self):
        test="""\
        param <%Collection<String>%> a:
        dependsOn c,d,e: #new construct
          a<c
          <%a=new balasfa%d% %>
        valid 0:
          a<3
        out:
          <%true%>
        invalid 0:
          a<5
        out:
          throws(a).asdf==awf #hara
        """
        parseTree=self.parser.input.parseString(test)
        assert 3==len(parseTree[0]), parseTree[0]
        assert 4==len(parseTree[0][0]), parseTree[0][0]
        assert parseTree[0][0][2]=="a", parseTree[0][0][2]
        assert 3==len(parseTree[0][1][0]), parseTree[0][1][0]
        assert 2==len(parseTree[0][1][1]), parseTree[0][1][1]
        
    def testInput3(self):
        test="""param <%Collection<String>%> a(a,b,c,d):
        dependsOn c,d,e: #new construct
          a<c
          <%a=new balasfa%d% %>
        valid 0:
          a<3
        out:
          <%true%>
        error:
          throws<%%>
        invalid:
          a<5
        out:
          throws==awf #hara
        """
        parseTree=self.parser.input.parseString(test)
        assert 3==len(parseTree[0]), parseTree[0]
        assert 4==len(parseTree[0][0]), parseTree[0][0]
        assert parseTree[0][0][2]=="a", parseTree[0][0][2]
        assert 3==len(parseTree[0][1][0]), parseTree[0][1][0]
        assert 2==len(parseTree[0][1][1]), parseTree[0][1][1]
    
    def testInput4(self):
        test='''param a(a,b,c,d)
        '''
        parseTree=self.parser.input.parseString(test)
        assert 4==len(parseTree[0][0][2]), parseTree[0][0][2]
    def testTestDecl1(self):
        test="""test m_j45 method <%m3 (a,b,c)%> returns <%adf%>:"""
        parseTree=self.parser.testDecl.parseString(test)
        assert 6==len(parseTree[0]), parseTree[0]
    def testTestDecl2(self):
        test="""test _m_j45 method <%m3 (a,b,c)%>:"""
        parseTree=self.parser.testDecl.parseString(test)
        assert 4==len(parseTree[0]), parseTree[0]
        
    def testSquareErrorExample(self):
        f=open('prog.stdl', 'r')
        test=f.read()
        parseTree=self.parser.test.parseString(test)
        f.close()
        assert 6==len(parseTree[0][1]), parseTree[0][1]
        
    def testSquareErrorExample2(self):
        f=open('prog2.stdl', 'r')
        test=f.read()
        parseTree=self.parser.program.parseString(test)
        f.close()
        assert 3==len(parseTree[0]), parseTree[0]
        assert 2==len(parseTree[1]), parseTree[1]
        
    def testProperConsumption(self):
        parser=ProgramParser()
        test='''\
        init:
	language: Pseudo
	
	
        test dateChecker method <%dateCheck (%day%,%month%,%year%)%> returns <%bool%>:
                var febDay:
                        dependsOn year:
                                febDay==29 if not(year % 400) else 28 if not (year % 100) else 29 if not (year % 4) else 28
                param day:
                        dependsOn month,febDay:
                                day<=[31,febDay,31,30,31,30,31,31,30,31,30,31][month-1]
                                day>=1
                        out:
                                returns = <% true %>'''
        self.assertRaises(SyntaxException,parser.parseText,test)
    def tearDown(self):
        """Call after every test case."""
        pass
     




if __name__ == "__main__":
    unittest.main() # run all tests
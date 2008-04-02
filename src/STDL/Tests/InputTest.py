import unittest
import sys
sys.path=['..'] + sys.path
from Input import Input
from Parser import Parser
from SubPartition import SubPartition
from Exceptions import *
from InheritedPartition import InheritedPartition

class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.parser = Parser()
        self.input = None
        self.input = Input()
        
    def testNormal1(self):       
        test="""\
        param <%ArrayList<point>%> c1:
                 dependsOn x1,x2,y1,y2:
                         <%
                         c1=new ArrayList();
                         c1.add(new Point(%x1%,%y1%));
                         c1.add(new Point(%x2%,%y2%));
                         %>
                 out:
                         returns >= (x1+y1) - (x2-y2)	
                 invalid 0:
                         <%c1=null;%>
                 out:
                         throws <%.GetType().Name==NullReferenceException%>"""
        self.input.tokens=self.parser.input.parseString(test)[0]
        gen=self.input.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        name=self.input.name
        inherits=self.input.inherits
        dataType=self.input.dataType
        assert name=="c1",name
        assert len(inherits)==0,inherits
        assert dataType=="ArrayList<point>",returns
       
    def testNormal2(self):
        test="""\
        param c2(a,b)
        """
        self.input.tokens=self.parser.input.parseString(test)[0]
        gen=self.input.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        name=self.input.name
        inherits=self.input.inherits
        assert name=="c2",name
        assert inherits[0]=='a',inherits
        dataType=self.input.dataType
        assert dataType is None, dataType
        
    def testNormal3(self):
        test="""\
        param <%ArrayList<point>%> c1:
                
            valid 0:
                    <%c1=null;%>
            out:
                    returns <%.GetType().Name==NullReferenceException%>
            invalid 0:
                     <%c1=null;%>
             out:
                     returns <%.GetType().Name==NullReferenceException%>
        """
        self.input.tokens=self.parser.input.parseString(test)[0]
        gen=self.input.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        name=self.input.name
        assert name=="c1",name
        assert self.input.validPartitions
        assert self.input.invalidPartitions
 
    def testEraseBug(self):
        self.input=Input([["param","c3","x4"]])
        gen=self.input.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        assert self.input.name=="c3",self.input.name
    
    def testDefective1(self):
        test="""\
        param <%ArrayList<point>%> c1:
                
            valid 0:
                    <%c1=null;%>
            out:
                    returns <%.GetType().Name==NullReferenceException%>
            valid 0:
                     <%c1=null;%>
             out:
                     returns <%.GetType().Name==NullReferenceException%>
        """
        self.input.tokens=self.parser.input.parseString(test)[0]
        gen=self.input.populate()
        self.assertRaises(DuplicateDefinitionException,gen.next)
        
    def testValueCount1(self):
        cut=self.input
        test="""\
        param <%ArrayList<point>%> c1:
            valid 0:
                    <%c1=null;%>
            valid 1:
                     <%c1=null;%> 
        """
        self.input.tokens=self.parser.input.parseString(test)[0]
        try:
            cut.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        assert cut.valueCount==(2,0), cut.valueCount
        assert cut.valueCount==(2,0), cut.valueCount

    def testValueCount2(self):
        cut=self.input
        test="""\
        param <%ArrayList<point>%> c1:
            valid 0:
                    <% %c1%=null;%>
            valid 1:
                     <% %c1%=null;%>
            invalid 0:
               c1 < 5
               c1 > 3
        """
        cut.tokens=self.parser.input.parseString(test)[0]
        try:
            cut.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        assert 5-sum(cut.valueCount)<=1
        assert 5-sum(cut.valueCount)<=1
    def getC1(self):
        test1="""\
        param <%ArrayList<point>%> c1:
            valid 0:
                    <% %c1%=null;%>
            valid 1:
                     <% %c1%=null;%>
            invalid 0:
               c1 < 5
               c1 > 3
        """
        c1=Input(tokens=self.parser.input.parseString(test1)[0])
        try:
            c1.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        return c1
    def testInheritOnly1(self):
        cut=self.input
        test2='''\
        param c2(c1)
        '''
        cut.tokens=self.parser.input.parseString(test2)[0]
        gen=cut.populate()
        c=True
        try:
            typ,ini = gen.next()
            assert typ=='ini',typ
            assert ini=='c1',ini
            c=False
            gen.send(self.getC1())
        except StopIteration:
            if c: self.fail("I haven't been asked any values")
        else:
            self.fail('Why has execution stopped')
        assert 5-sum(cut.valueCount)<=1
        assert 5-sum(cut.valueCount)<=1
    
    def testTransform1(self):
        cut=self.input
        cut.name='x'
        inh=InheritedPartition()
        s=SubPartition()
        inh.subPartitions.append(s)
        s.containsExternalCode=True
        s.code='hello %w% %w%'
        s.inputName='w'
        s=cut._Input__transformPartition(inh)[0]
        assert isinstance(s,SubPartition)
        assert s.code=='hello %x% %x%'
        assert s.inputName=='x'
        
if __name__ == "__main__":
    unittest.main() # run all tests   
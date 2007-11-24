from __future__ import with_statement
import unittest
import sys
sys.path=['..'] + sys.path
from Parser import *
from Test import Test
from Input import *
from Exceptions import *

class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.parser = Parser()
        self.test = Test()
    
    def testNormal1(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%> returns <%double%>:
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
			throws <%.GetType().Name==NullReferenceException%>
        '''
        cut.tokens=self.parser.test.parseString(test)[0]
        try:
            cut.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        assert self.test.test=="squareError",self.test.test
        
    def testNormal2(self):
        cut = self.test
        test="""\
        test squareError method <%squareError (%c1%,%c2%)%>:
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
			throws <%.GetType().Name==NullReferenceException%>
        """
        self.test.tokens=self.parser.test.parseString(test)[0]
        try:
            cut.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        assert self.test.method=="squareError (%c1%,%c2%)",self.test.method
    
    def testDefective1(self):
        test="""\
        test squareError method <%squareError (%c1%,%c2%)%>:
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
			throws <%.GetType().Name==NullReferenceException%>
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
			throws <%.GetType().Name==NullReferenceException%>
        """
        self.test.tokens=self.parser.test.parseString(test)[0]
        gen=self.test.populate()
        self.assertRaises(DuplicateDefinitionException,gen.next)
     
    def testInheritance1(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x:
             valid 0:
               x==3
               x==5
             out:
               assert <% true %>
            param y(x)
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        try:
            cut.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        inp=cut.inputs['y']
        assert isinstance(inp,Input)
        assert not inp.dependsOn
        assert inp.inherits
        assert len(inp.validPartitions)==1,len(inp.validPartitions)

    def testInheritance2(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x:
             valid 0:
               x==3
               x==5
             out:
               assert <% true %>
            param z(x)
            param w(z):
              valid 0:
               w==3
               w==5
               w==1
             out:
               assert <% true %>
            param y(x,w)
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        try:
            cut.populate().next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        inp=cut.inputs['y']
        assert isinstance(inp,Input)
        assert not inp.dependsOn
        assert inp.inherits
        assert len(inp.validPartitions)==3,len(inp.validPartitions)

    def testInheritance3(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x(w):
             valid 0:
               x==3
               x==5
             out:
               assert <% true %>
            param z(x)
            param w(z):
              valid 0:
               w==3
               w==5
               w==1
             out:
               assert <% true %>
            param y(w)
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        self.assertRaises(CyclicReferenceException,cut.populate().next)
        
    def getExample(self):
        test='''\
        invalid y:
          y==4
          y<3
          y>2
        '''
        tokens=LibraryParser().invalidPartition.parseString(test)[0]
        p=InheritedPartition(tokens)
        for x in p.populate():
            pass
        return p
    
    def testInheritance4(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x:
             valid 0(email):
               x==3
               x==5
             out:
               assert <% true %>
            param z(x)
            param w(z):
              valid 0:
               w==3
               w==5
               w==1
             out:
               assert <% true %>
            param y(w)
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        f=False
        gen=cut.populate()
        try:
            typ,val=gen.next()
            assert typ=='inp',typ
            assert 'email' in val,val
            f=True
            gen.send(self.getExample())
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        assert f
        inp=cut.inputs['y']
        assert isinstance(inp,Input)
        assert not inp.dependsOn
        assert inp.inherits
        assert len(inp.validPartitions)==2,len(inp.validPartitions)
        
    def testInheritance5(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x(w)
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        self.assertRaises(SemanticException,cut.populate().next)
    def testInheritance6(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x(w)
           param w(f,r)
           param f:
             valid 0:
               f==4
           param r(x)
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        self.assertRaises(CyclicReferenceException,cut.populate().next)
    def testInheritance7(self):
        cut=self.test
        test='''\
        test squareError method <%squareError (%c1%,%c2%)%>:
           param x(w)
           param w(f,r)
           param f:
             valid 0:
               f==4
           param r():
             valid 0:
               w==5
        '''
        self.test.tokens=self.parser.test.parseString(test)[0]
        self.assertRaises(SemanticException,cut.populate().next)
    def checkIfDependant(self,order,inputDict):
        for i,name in enumerate(order):
            assert all((dep in order[:i]) for dep in inputDict[name].dependsOn)
            
    def testSortDependencies1(self):
        cut=self.test
        i1,i2,i3,i4,i5=Input(),Input(),Input(),Input(),Input()
        i1.name,i2.name,i3.name,i4.name,i5.name='i1','i2','i3','i4','i5'
        i1.dependsOn=['i2','i3','i4']
        i5.dependsOn=['i1']
        i4.dependsOn=['i2','i3']
        i2.dependsOn=['i3']
        cut.inputs={'i1':i1,'i2':i2,'i3':i3,'i4':i4,'i5':i5}
        order=cut.sortDependencies()
        assert len(order)==5,len(order)
        self.checkIfDependant(order,cut.inputs)
    def testSortDependencies2(self):
        cut=self.test
        i1,i2,i3,i4,i5=Input(),Input(),Input(),Input(),Input()
        i1.name,i2.name,i3.name,i4.name,i5.name='i1','i2','i3','i4','i5'
        cut.inputs={'i1':i1,'i2':i2,'i3':i3,'i4':i4,'i5':i5}
        order=cut.sortDependencies()
        assert len(order)==5,len(order)
        self.checkIfDependant(order,cut.inputs)
    def testSortDependencies3(self):
        cut=self.test
        i1,i2,i3,i4,i5=Input(),Input(),Input(),Input(),Input()
        i1.name,i2.name,i3.name,i4.name,i5.name='i1','i2','i3','i4','i5'
        i1.dependsOn=['i2','i4']
        i5.dependsOn=['i1']
        i4.dependsOn=['i2','i3']
        i2.dependsOn=['i3']
        i3.dependsOn=['i5']
        cut.inputs={'i1':i1,'i2':i2,'i3':i3,'i4':i4,'i5':i5}
        self.assertRaises(CyclicReferenceException,cut.sortDependencies)
    
    def testSortDependencies4(self):
        cut=self.test
        i1,i2,i3,i4,i5=Input(),Input(),Input(),Input(),Input()
        i1.name,i2.name,i3.name,i4.name,i5.name='i1','i2','i3','i4','i5'
        i1.dependsOn=['i2','i4']
        i5.dependsOn=['i1']
        i4.dependsOn=['i2','i3']
        i2.dependsOn=['i3']
        i3.dependsOn=['i7']
        cut.inputs={'i1':i1,'i2':i2,'i3':i3,'i4':i4,'i5':i5}
        self.assertRaises(SemanticException,cut.sortDependencies)
    
    def testCombine1(self):
        test=self.combineN([1,2,3])
        assert test==[[1],[2],[3]],test
    
    def testCombine2(self):
        test1=self.combineN([1,2,3],[4,5,6])
        test2=self.test.combine2([1,2,3],[4,5,6],True)
        assert all(t1==t2 for t1,t2 in zip(test1,test2))
        
    def testHorizontalGrowth1(self):
        cut=self.test
        suite=cut.combine2([TestCaseValue(index=i+1,variableName=0) for i in range(3)],
                           [TestCaseValue(index=j+1,variableName=1) for j in range(3)],True)
        pi=cut.horizontalGrowth(suite,2,[3,3,1])
        assert len(pi)==0,len(pi)
        assert all(TestCaseValue(index=1, variableName=2) in tc or TestCaseValue(index=None, variableName=2) in tc for tc in suite)
     
    def testHorizontalGrowth2(self):
        cut=self.test
        suite=cut.combine2([TestCaseValue(index=i+1,variableName=0) for i in range(3)],
                           [TestCaseValue(index=j+1,variableName=1) for j in range(3)],True)
        pi=cut.horizontalGrowth(suite,2,[3,3,3])
        assert len(pi)==2,len(pi)
        assert all(TestCaseValue(index=1, variableName=2) in tc or TestCaseValue(index=2, variableName=2) or TestCaseValue(index=3, variableName=2) in tc for tc in suite)    
        
    def testVerticalGrowth1(self):
        cut=self.test
        suite=[]
        suite.append([TestCaseValue(index=1,variableName=0),TestCaseValue(index=1,variableName=1)])
        suite.append([TestCaseValue(index=1,variableName=0),TestCaseValue(index=2,variableName=1)])
        suite.append([TestCaseValue(index=2,variableName=0),TestCaseValue(index=1,variableName=1)])
        suite.append([TestCaseValue(index=None,variableName=0),TestCaseValue(index=2,variableName=1)])
        pi=set([(TestCaseValue(index=2,variableName=0),TestCaseValue(index=2,variableName=1))])
        cut.verticalGrowth(suite,pi)
        assert len(suite)==4,len(suite)
        assert len(pi)==0,len(pi)
        assert suite[3][1]==TestCaseValue(index=2,variableName=1),str(suite[3][1])
        self.assertPairwiseCoverage(suite)
    
    def assertPairwiseCoverage(self,suite):
        vars=len(suite[0])
        column=[[] for i in range(vars)]
        for tc in suite:
            for i in range(vars):
                column[i].append(tc[i])
        #calculate whole pi
        pi=set()
        for i in range(vars):
            for c in range(i):
                pairs=self.test.combine2(set(column[c]),set(column[i]))
                intersections=set((p1,p2) for p1,p2 in pairs if p1.index!=None and p2.index!=None)
                pi.update(intersections)
        #start removing pairs from pi
        for i in range(vars):
            for c in range(i):
                pairs=set(pair for pair in zip(column[c],column[i]))
                pi.difference_update(pairs)
        assert len(pi)==0,len(pi)
        
    def combineN (self, *args):
        '''Combines the first list (as argument) with subsequent lists'''
        #This method is a bit too much memory hungry due to its recursive nature and can be optimised. Speed is ok.
        if len(args)==0:
            return
        for i,ls in enumerate(args[0]):
            if not isinstance(ls,list):
                args[0][i]=[ls]
        if len(args)==1:
            for ls in args[0]:
                ls[0]=copy.copy(ls[0])
            return args[0]
        res=[]
        for ls in args[0]:
            #combine with args[1]
            for c in args[1]:
                temp=copy.copy(ls)
                temp.append(copy.copy(c))
                res.append(temp)
        return self.combineN(res,*args[2:])
        
    def testAssertPairwiseCoverage1(self):
        cut=self.test
        suite=cut.combine2([TestCaseValue(index=i+1,variableName=0) for i in range(3)],
                           [TestCaseValue(index=j+1,variableName=1) for j in range(3)],True)
        self.assertPairwiseCoverage(suite)
        
    def testAssertPairwiseCoverage2(self):
        cut=self.test
        suite=self.combineN([TestCaseValue(index=i+1,variableName=0) for i in range(3)],
                           [TestCaseValue(index=j+1,variableName=1) for j in range(3)],
                       [TestCaseValue(index=j+1,variableName=2) for j in range(2)])
        self.assertPairwiseCoverage(suite)
                    
        
    def testGetPairwiseSuite1(self):
        suite=self.test.getPairwiseSuite([2,2,3])
        self.assertPairwiseCoverage(suite)
        
    def testGetPairwiseSuite2(self):
        '''testing with a large test suite'''
        suite=self.test.getPairwiseSuite([2,2,3,4,5,6,1])
        self.assertPairwiseCoverage(suite)
        
    def testGetPairwiseSuite3(self):
        '''testing with a shallow test suite'''
        suite=self.test.getPairwiseSuite([1,1,1,1,1,1,1,1,1,1])
        assert len(suite)==1,len(suite)
        self.assertPairwiseCoverage(suite)
        
    def testGetPairwiseSuite4(self):
        '''testing with a too short test suite'''
        suite=self.test.getPairwiseSuite([1])
        assert len(suite)==1,len(suite)
        self.assertPairwiseCoverage(suite)
        
    def testGetPairwiseSuite5(self):
        '''testing with a very large test suite'''
        suite=self.test.getPairwiseSuite([10,2,10,4,5,20,1])
        self.assertPairwiseCoverage(suite)
        
    def testGetPairwiseSuite6(self):
        '''testing with an incrementally larger test suite'''
        suite=self.test.getPairwiseSuite([1,1,5,10,60])
        self.assertPairwiseCoverage(suite)
    
    def testgetBCInvalidSuite(self):
        '''testing base choice combination strategy'''
        suite=self.test.getBCInvalidSuite([2,0,0,3,2])
        assert len(suite)==7,len(suite)
        #check there is only 1 negative no.
        assert all(len([None for v in tc if v.index<0])==1 for tc in suite)
        #check that all other nos are 0
        assert all(len([None for v in tc if v.index==0])==len(tc)-1 for tc in suite)
                                          
    #-----------------------------------------Integration tests-----------------------------------------#
    
    def testGetTestSuite1(self):
        '''Simple test suite generation'''
        cut=self.test
        test='''\
        test xihaga method <% boq (%a%)%> returns <% int %>:
            param c:
             valid 0:
              c==3
              c==4
            
            param b(c)
            
            param a:
              dependsOn b,c:
                a==b+c
              out:
                returns>3
              valid 0:
                a==1
        '''
        cut.tokens=self.parser.test.parseString(test)[0]
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        suite=cut.getTestSuite()
        values=[tc[3].value for tc in suite]
        assert values==[6,1,1,8],values
        
    def testGetTestSuite2(self):
        '''Saved test suite generation'''
        cut=self.test
        with open('prog.stdl') as f:
           cut.tokens=self.parser.test.parseString(f.read())[0]
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        suite=cut.getTestSuite()
        assert len(suite)==6,len(suite)
        
    def testGetInvalidTestSuite1(self):
        '''Testing an invalid test suite only'''
        cut=self.test
        test='''\
        test xihaga method <% boq (%a%)%> returns <% int %>:
            param c:
             valid 0:
              c>3
              c<7
             out:
              assert <%true%>
             error:
              assert <%false%>
            
            param b(c)
        '''
        cut.tokens=self.parser.test.parseString(test)[0]
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        suite=cut.getTestSuite(valid=0,invalid='bc')
        assert len(suite)==4,len(suite)
        for check in (tc[0] for tc in suite):
            assert isinstance(check,PartitionCheck)
            checkItems=check.getCheckItems({})
            for checkItem in checkItems:
                assert isinstance(checkItem,PartitionCheckItem)
                assert checkItem.value=='false',checkItems.value
if __name__ == "__main__":
    unittest.main() # run all tests   
import unittest
import sys
sys.path=['..'] + sys.path
from Partition import * # code from module you're testing
from Parser import *
from PartitionCheck import *


class SimpleTests(unittest.TestCase):
    #CUT is Class Under Test
    def setUp(self):
        """Call before every test case."""
        self.partition = Partition()
        self.parser = Parser()
        
    def testPopulateBasic1(self):
        cut=self.partition
        test='''\
        valid 0:
          x==3
        out:
          returns==3
        '''
        test=self.parser.eqClass.parseString(test)[0]
        cut.tokens=test
        cut.inputName='x'
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
        assert cut.name==0,cut.name
        assert cut.valid
        assert len(cut.subPartitions)==1, len(cut.subPartitions)
        l=len(cut.outPartitionCheck.checkItems)
        assert l==1,l
        assert not cut.errorPartitionCheck.checkItems
        
    def testPopulateBasic2(self):
        cut=self.partition
        test='''\
        invalid 0:
          x==3
          x==5
        out:
          returns==3
          assert<% %>
        '''
        test=self.parser.eqClass.parseString(test)[0]
        cut.tokens=test
        cut.inputName='x'
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
        assert cut.name==0,cut.name
        assert not cut.valid
        assert len(cut.subPartitions)==2, len(cut.subPartitions)
        l=len(cut.outPartitionCheck.checkItems)
        assert l==2,l
        assert cut.errorPartitionCheck is None
        
    def testPopulateErr1(self):
        cut=self.partition
        test='''\
        invalid 0:
          x==5
          y==4
        out:
          assert<% %>
        '''
        test=self.parser.eqClass.parseString(test)[0]
        cut.tokens=test
        cut.inputName='x'
        gen=cut.populate()
        self.assertRaises(SemanticException,gen.next)
    
    def testPopulateInherit1(self):
        cut=self.partition
        test='''\
        invalid 0 (email):
          x==5
        out:
          assert<% %>
        '''
        test=self.parser.eqClass.parseString(test)[0]
        cut.tokens=test
        cut.inputName='x'
        gen=cut.populate()
        req=gen.next()
        assert req==('inp',['email']), req
        
        try:
            gen.send([])
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
            
    def testPopulateInherit2(self):
        cut=self.partition
        test='''\
        invalid 0 (email,email.wide):
          x==5
        out:
          assert<% %>
        '''
        test=self.parser.eqClass.parseString(test)[0]
        cut.tokens=test
        cut.inputName='x'
        gen=cut.populate()
        req=gen.next()
        assert req==('inp',['email']), req
        req=gen.send([SubPartition()])
        assert req==('inp',['email','wide']), req
        try:
            gen.send([])
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
    
    def getExample(self):
        test='''\
        invalid 0:
          y==4
          y<3
          y>2
        '''
        p=Partition(self.parser.eqClass.parseString(test)[0],'y')
        for x in p.populate():
            pass
        dic={'email':p.subPartitions,'wide':{}}
        test='''\
        invalid 0:
          <% %z%=null %>
          z==<%null%>
          z<4
        '''
        p=Partition(self.parser.eqClass.parseString(test)[0],'z')
        p.inputName='z'
        for x in p.populate():
            pass
        dic['wide']['email']=p.subPartitions
        return dic
    
    def getFromDic(self,req,dic):
        '''given a list representing the path to a value, will return a value from the respective dictionary'''
        for r in req:
            dic=dic[r]
        return dic
        
    def testPutValue1(self):
        cut=self.partition
        test='''\
        invalid 0 (email,wide.email):
          x==5
        out:
          assert<% %>
        '''
        cut.tokens=self.parser.eqClass.parseString(test)[0]
        cut.inputName='x'
        dic=self.getExample()
        gen=cut.populate()
        typ,req=gen.next()
        typ,req=gen.send(self.getFromDic(req,dic))
        try:
            req=gen.send(self.getFromDic(req,dic))
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
        cut.valueStart=-1
        suite=[[PartitionCheck(),TestCaseValue(index=-i)] for i in range(1,cut.valueCount+1)]
        [cut.putValues(tc,1,variableName='v1') for tc in suite]
        assert 5 in (value[1].value for value in suite)
        assert 4 in (value[1].value for value in suite)
        assert 3 in (value[1].value for value in suite)
        assert 2 in (value[1].value for value in suite)
        assert all (value[1].variableName=='v1' for value in suite)
        assert 'null' in (value[1].value for value in suite)
        assert ' v1=null ' in (value[1].value for value in suite)
        
    def testInvert1(self):
        cut=self.partition
        test='''\
        valid 0:
          x<3
          x<4
        error:
          returns==3
          assert<% %>
        '''
        test=self.parser.eqClass.parseString(test)[0]
        cut.tokens=test
        cut.inputName='x'
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
        cut=~cut
        cut.valueStart=-1
        suite=[[PartitionCheck(),TestCaseValue(index=-i)] for i in range(1,cut.valueCount+1)]
        [cut.putValues(tc,1,variableName='x') for tc in suite]
        assert cut.name==0,cut.name
        assert not cut.valid
        assert len(cut.subPartitions)==2, len(cut.subPartitions)
        l=len(cut.outPartitionCheck.checkItems)
        assert l==2,l
        assert 4 in (v[1].value for v in suite)
        assert len(suite[0][0])==2,len(suite[0][0])
        assert cut.errorPartitionCheck is None
        
    def testSetValueStart1(self):
        cut=self.partition
        test='''\
        valid 0:
          x<3
          x<4
        '''
        cut.tokens=self.parser.eqClass.parseString(test)[0]
        cut.inputName='x'
        gen=cut.populate()
        try:
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
        cut.valueStart=3
        assert 3 in cut.putValueDict
        assert 4 in cut.putValueDict
        assert len (cut.putValueDict)==2,len (cut.putValueDict)
        
    def testSetValueStart2(self):
        cut=self.partition
        test='''\
        invalid 0(email):
          x<3
          x<4
        '''
        cut.tokens=self.parser.eqClass.parseString(test)[0]
        cut.inputName='x'
        gen=cut.populate()
        try:
            c=gen.next()
            gen.send(self.getExample()['email'])
        except StopIteration:
            pass
        else:
            self.fail("Why has execution paused?")
        cut.valueStart=-2
        assert -2 in cut.putValueDict
        assert -3 in cut.putValueDict
        assert -4 in cut.putValueDict
        assert -5 in cut.putValueDict
        assert -6 in cut.putValueDict
        assert len (cut.putValueDict)==5,len (cut.putValueDict)
if __name__ == "__main__":
    unittest.main() # run all tests
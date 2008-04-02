import unittest
import sys
sys.path=['..'] + sys.path
from PartitionCheck import * # code from module you're testing
from Parser import *


class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.check = PartitionCheck()
        self.parser = Parser()
        
    def testPopulateValid1(self):
        cut=self.check
        cut.valid=True
        test="""\
          out:
            returns<10
            returns><%aw aw%>
            returns< <%aw%>
            assert <% asdfa %>
            returns<%asdfa%>
        """
        test=self.parser.partitionOut.parseString(test)[0]
        cut.tokens=test
        cut.populate()
        assert cut.valid
        l=len(cut.checkItems)
        assert l==5,l
        assert not cut.throws
   
    def testPopulateValid2(self):
        cut=self.check
        cut.valid=True
        test="""\
          out:
            returns<10
            returns><%aw aw%>
            returns< <%aw%>
            throws <% asdfa %>
            returns<%asdfa%>
        """
        test=self.parser.partitionOut.parseString(test)[0]
        cut.tokens=test
        self.assertRaises(SemanticException,cut.populate)
        
        
    def testPopulateInvalid1(self):
        cut=self.check
        cut.valid=True
        test="""\
          error:
            throws<10
            throws <% asdfa %>
            throws<%asdfa%>
        """
        test=self.parser.partitionError.parseString(test)[0]
        cut.tokens=test
        cut.populate()
        assert cut.throws
        assert not cut.valid
        l=len(cut.checkItems)
        assert l==3,l
        
    def testPopulateInvalid2(self):
        cut=self.check
        cut.valid=False
        test="""\
          error:
            throws<10
        """
        test=self.parser.partitionError.parseString(test)[0]
        cut.tokens=test
        self.assertRaises(SemanticException,cut.populate)
        
    def testPopulateInvalid3(self):
        cut=self.check
        cut.valid=True
        test="""\
          out:
            throws<10
        """
        test=self.parser.partitionOut.parseString(test)[0]
        cut.tokens=test
        self.assertRaises(SemanticException,cut.populate)
        
    def testAdd1(self):
        cut=self.check
        cut.valid=True
        test="""\
          out:
            returns<10
        """
        cut.tokens=self.parser.partitionOut.parseString(test)[0]
        test="""\
          out:
            assert <%c<10%>
        """
        other=PartitionCheck(self.parser.partitionOut.parseString(test)[0],True)
        cut.populate()
        other.populate()
        new=other + cut
        assert isinstance(new,PartitionCheck)
        assert new.notEmpty
        assert new.checkItems[0].addReturns ^ new.checkItems[1].addReturns, 'Only one should be with a returns'
        assert new.checkItems[0].isJustExternalCode ^ new.checkItems[1].isJustExternalCode, 'Only one should be just external code'
        assert not new.throws
        assert new.valid
        
    def testAdd2(self):
        cut=self.check
        cut.valid=True
        test="""\
          out:
            returns<10
        """
        cut.tokens=self.parser.partitionOut.parseString(test)[0]
        test="""\
          out:
            throws <%c<10%>
        """
        other=PartitionCheck(self.parser.partitionOut.parseString(test)[0],False)
        cut.populate()
        other.populate()
        assert other+cut==other,'Not equal'
        
    def testAdd3(self):
        cut=self.check
        cut.valid=True
        test="""\
          error:
            returns<10
        """
        cut.tokens=self.parser.partitionError.parseString(test)[0]
        test="""\
          out:
            returns <%c<10%>
        """
        other=PartitionCheck(self.parser.partitionOut.parseString(test)[0],True)
        cut.populate()
        other.populate()
        assert other+cut==cut,'Not equal'
        
    def testAdd4(self):
        '''testing with more than 1 invalid partition'''
        cut=self.check
        cut.valid=True
        test="""\
          error:
            returns<10
        """
        cut.tokens=self.parser.partitionError.parseString(test)[0]
        test="""\
          out:
            returns <%c<10%>
        """
        other=PartitionCheck(self.parser.partitionOut.parseString(test)[0],False)
        test="""\
          out:
             assert <%c<10%>
        """
        other2=PartitionCheck(self.parser.partitionOut.parseString(test)[0],False)
        cut.populate()
        other.populate()
        other2.populate()
        new=cut+other+other2
        self.assertNotEqual(new,cut,'Should not be referencing the same object')
        assert not cut.otherCheck or other.otherCheck or other2.otherCheck
        assert len(new.otherCheck)==2,len(new.otherCheck)
        assert new.otherCheck[0]==other,other
        assert new.otherCheck[1]==other2,other2

    def testGetCheckItems1(self):
        cut=self.check
        cut.valid=True
        test="""\
          out:
            assert <% %returns%<10%>
        """
        test=self.parser.partitionOut.parseString(test)[0]
        cut.tokens=test
        cut.populate()
        assert cut.valid
        items=cut.getCheckItems([])
        l=len(items)
        assert l==1,l        
        assert items[0].value.find('returns<10')!=-1
if __name__ == "__main__":
    unittest.main() # run all tests
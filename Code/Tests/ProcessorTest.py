import unittest
import sys
sys.path=['..'] + sys.path
from Processor import Processor
from Parser import LibraryParser


class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.processor = Processor()
        
    def testPopulate1(self):
        cut=self.processor
        test='''\
        init:
          language: CS2
	
        valid email:
          email=="duca@waldonet.net"
          email=="s@de.com"
          email=="m@m.gov"
         
        valid monkey:
          monkey==4
          monkey==6
          '''
        parser=LibraryParser()
        parser.parseText(test)
        cut._Processor__populateLibrary(parser.tokens,'testlib')
        assert 'testlib' in cut.inheritedPartitions
        inh=cut.inheritedPartitions['testlib']
        assert 'email' in inh
        assert 'monkey' in inh
        
    def testPopulate2(self):
        cut=self.processor
        test='''\
        init:
          language: CS2
	
        valid email:
          email=="duca@waldonet.net"
          email=="s@de.com"
          email=="m@m.gov"
          
               
        valid monkey():
          monkey==4
          monkey==6
          '''
        parser=LibraryParser()
        parser.parseText(test)
        cut._Processor__populateLibrary(parser.tokens,'testlib')
        assert 'testlib' in cut.inheritedPartitions
        inh=cut.inheritedPartitions['testlib']
        assert 'email' in inh
        assert 'monkey' in inh
        assert '"m@m.gov"' in (sp.code for sp in inh['email'].subPartitions)
    #--------------------------------------------- Integration TESTS ----------------------------------
    def testLoadFromFile1(self):
        cut=self.processor
        cut.loadFromFile('testimport.stdl')
        
        
if __name__ == "__main__":
    unittest.main() # run all tests   
import unittest
import sys
sys.path=['..'] + sys.path
from Parser import ProgramParser # code from module you're testing
from Program import *

class SimpleTests(unittest.TestCase):
    def setUp(self):
        """Call before every test case."""
        self.parser = ProgramParser()
        self.program = Program()
        self.program.name="TestProgram"
        
    def testNormalProg(self):
        self.parser.loadFromFile("normal.stdl")
        self.program.tokens=self.parser.tokens
        gen=self.program.populate()
        try:
            typ,imp=gen.next()
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        assert typ=='imp',typ
        assert imp==['imports.stdl'],imp
        imports=self.program.initParams.params["imports"][0]
        assert imports=="imports.stdl",imports
        
    def testDefectiveProg1(self):
        self.parser.loadFromFile("defective1.stdl")
        self.program.tokens=self.parser.tokens
        self.assertRaises(SemanticInitException,self.program.populate().next)
        
    def testDuplicates(self):
        test1=Test()
        test2=Test()
        test3=Test()
        test4=Test()
        test1.test="a"
        test2.test="b"
        test3.test="b"
        test4.test="a"
        self.program.children=[test1,test2,test3,test4]
        duplicates=self.program.getDuplicates()
        assert ' a ' in duplicates
        assert ' b ' in duplicates
    
    #-------------------------- Integration tests -------------------------------------------------
    def testGetCode1(self):
        self.parser.loadFromFile('normal.stdl')
        self.program.tokens=self.parser.tokens
        gen=self.program.populate()
        try:
            typ,imp=gen.next()
            gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        c,code=self.program.getCode()
        assert 'returns >= 2' in code
        assert 'c2.add(new Point(-1,-1));' in code
        assert 'c1.add(new Point(-1,1));' in code
        
    def testGetCode2(self):
        self.parser.loadFromFile('..\\examples\\dateCheck.stdl')
        self.program.tokens=self.parser.tokens
        gen=self.program.populate()
        try:
            typ,imp=gen.next()
        except StopIteration:
            pass
        else:
            self.fail('Why has execution stopped')
        c,code=self.program.getCode()
        assert 'day = 28' in code
        assert 'assert returns ==  true' in code
        assert 'month = 6' in code
        
        
if __name__ == "__main__":
    unittest.main() # run all tests   
    
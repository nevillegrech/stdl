from Exceptions import *
from BaseClasses import *
from pyparsing import QuotedString,ParseException

class PartitionCheckItem(ParsedElement):
    
    def __init__(self,tokens=None):
        self.containsExternalCode=None
        self.isJustExternalCode=None
        self.throws=False
        self.addReturns=False
        self.code=None
        self.value=None
        self.comparator=None
        ParsedElement.__init__(self,tokens)
   
    def calcValue(self,testCaseValues=None):
        if not self.containsExternalCode:
            #evaluate python code
            try:
                compiledExpression=compile(self.code,'<output-check>','eval')
                value=eval(compiledExpression,testCaseValues)
            except Exception:
                raise SyntaxSemanticException("Invalid Syntax in %s"%(self.code))
            self.value=str(value)
        else:
            def repl(x):
                return "%" if x[0]=="" else str(testCaseValues[x[0]]) 
            var=QuotedString("%").setParseAction(repl)
            self.value=var.transformString(self.code)
        
    def populate(self):
        tokens=self.tokens
        if len(tokens)==2:
            self.containsExternalCode=True
            self.isJustExternalCode=True
            if tokens[0]=='assert':
                self.addReturns=False
                self.throws=False
            elif tokens[0]=='throws':
                self.throws=True
                self.addReturns=False
            elif tokens[0]=='returns':
                self.addReturns=True
                self.throws=False
            else: raise SemanticException('Invalid Partition Check Item')
            self.code=tokens[1]
        elif len(tokens)==3:
            self.addReturns=tokens[0]=='returns'
            self.throws=not self.addReturns
            tok=self.tokens[2]
            self.comparator=self.tokens[1]
            parse=QuotedString ("<%", "\\", None, False, unquoteResults=True, endQuoteChar="%>")
            self.isJustExternalCode=False
            try:
                self.code=parse.parseString(tok)[0]
                self.containsExternalCode=True
            except ParseException:
                self.containsExternalCode=False
                self.code=tok
        else:
            raise SemanticException("Check is invalid")
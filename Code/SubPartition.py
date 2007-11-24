from BaseClasses import *
from Exceptions import *
from pyparsing import QuotedString, ParseBaseException
from TestCaseValue import *


class SubPartition(ParsedElement):
    opposites={"<":">=","==":"!=",">=":"<",">":"<=","!=":"==","<=":">"}
    def __init__(self,tokens=None, inputName="",valid=None):
        self.containsExternalCode=None
        self.isJustExternalCode=None
        self.inputName=inputName
        self.comparator=None
        self.code=None
        self.valid=valid
        super (SubPartition,self).__init__(tokens)
    
    def __getValueCount(self):
        return 1
    valueCount=property(fget=__getValueCount, doc='Returns the number of interesting values')
    def evaluate(self,comparator,expression,dependsDict={}):
        #TODO: REFACTOR, USE PARTIAL FUNCTIONS HERE
        values={"<":([-1],[-2]),"<=":([0],[-1]),"==":([0],[0]),">=":([0],[+1]),">":([1],[2]),"!=":([1,-1],[0])}
        try:
            compiledExpression=compile(expression,'sub-partition','eval')
            #convert the dependsDict values
            value=eval(compiledExpression,dependsDict)
            if isinstance(value,str):
                if comparator!='==':
                    raise SemanticException('Cannot use comparator %s with %s'%(comparator,expression))
                else:
                    value='"%s"'%value
            else:
                value+=values[comparator][0][0]
        except Exception:
            raise SyntaxSemanticException("Invalid Syntax in %s"%(expression))
        return [value]
            
  
    def populate(self):
        if len(self.tokens)==3:
            self.isJustExternalCode=False
            if self.tokens[0]!=self.inputName:
                raise SemanticException("Cannot set input %s in a subpartition of %s"%(self.tokens[0],self.inputName))
            tok=self.tokens[2]
            self.comparator=self.tokens[1]
            parse=QuotedString ("<%", "\\", None, False, unquoteResults=True, endQuoteChar="%>")
            try:
                self.code=parse.parseString(tok)[0]
                self.containsExternalCode=True
                if self.comparator!="==":
                    raise SemanticException("Only == operator is supported when using external code in sub-partition")
            except ParseBaseException:
                self.containsExternalCode=False
                self.code=tok
        elif len(self.tokens)==1:
            self.containsExternalCode, self.isJustExternalCode=True,True
            self.code=self.tokens[0]
        else: raise SemanticException("Invalid Input in sub partition")
 
    def getValue(self,index=0,dependsDict=None,variableName=None):
        if not dependsDict: dependsDict={}
        if self.containsExternalCode:
            def repl(x):
                return "%" if x[0]=="" else variableName if self.inputName == x[0] else str(dependsDict[x[0]])
            var=QuotedString("%").setParseAction(repl)
            code=[var.transformString(self.code)]
        else:
            code=self.evaluate(self.comparator,self.code,dependsDict)
        return TestCaseValue(value=code[index],isJustExternalCode=self.isJustExternalCode,variableName=variableName)
    
    def __invert__(self):
        if self.containsExternalCode or self.isJustExternalCode or self.comparator is None:
            return None
        else:
            new=SubPartition()
            new.containsExternalCode, new.isJustExternalCode, new.inputName = self.containsExternalCode, self.isJustExternalCode, self.inputName
            new.comparator = self.opposites[self.comparator]
            new.valid = self.valid
            new.code = self.code
        return new
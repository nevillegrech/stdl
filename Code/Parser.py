from __future__ import with_statement
from pyparsing import *
from Exceptions import *

class Parser(object):
    #The following is the grammar of the language:
    
    #White space chars of the language
    DEFAULT_WHITE_CHARS = " \t\r"
    ParserElement.setDefaultWhitespaceChars(DEFAULT_WHITE_CHARS)
    
    #Primitives
    codeLineEnd=OneOrMore(pythonStyleComment | LineEnd() | Literal('\r')).suppress()
    statementEnd=":" + codeLineEnd
    extStmt=QuotedString ("<%", "\\", None, True, unquoteResults=True, endQuoteChar="%>")
    cmp1=oneOf("== <= >= > !=")
    cmp2=Literal("<")
    
    lBracket=Literal("(").suppress()
    rBracket=Literal(")").suppress()  
    
    
    #names
    allowedChars="-_"
    identifier=Word(alphas+allowedChars,alphanums+allowedChars)
    variable=identifier
    commaSeperatedVars=delimitedList(variable)
    
    #------Structure of the language----#
    
    #Partition Definition
    partitionIdentifier=Word(nums)
    otherStmt=extStmt + codeLineEnd
    sp1=Group(variable + cmp1 + SkipTo(codeLineEnd,True))
    sp2=Group(variable + cmp2 + Combine(~Literal("%") + SkipTo(codeLineEnd,True)))
    sp3=Group(otherStmt)
    subPartition=sp1 | sp2 | sp3
    partition=Group(ZeroOrMore(subPartition)) #Changed this line at the last minute.. check!
    inheritPartition=Group(lBracket+Optional(delimitedList(Group(variable+Optional(Literal(".").suppress()+variable))),[])+rBracket)
    commonPartition=partitionIdentifier + Optional(inheritPartition,[]) + statementEnd.suppress()
    validPartition=Group(Group("valid" + commonPartition) + partition)
    invalidPartition=Group(Group("invalid" + commonPartition) + partition)
    
    #Partition output checks
    outputTokens="returns throws"
    extVerif=oneOf(outputTokens+" assert")+otherStmt
    biv1=oneOf(outputTokens) + cmp1 + SkipTo(codeLineEnd,True)
    biv2=oneOf(outputTokens) + cmp2 + Combine(~Literal("%") + SkipTo(codeLineEnd,True))
    builtInVerif=biv1 | biv2
    
    outStmts=Group(OneOrMore(Group(extVerif | builtInVerif)))
    partitionOut=Group ("out"+statementEnd.suppress()+outStmts)
    partitionError=Group ("error"+statementEnd.suppress()+outStmts)
    
    #Full partition definition
    eqClass=Group (validPartition + Optional(partitionOut,[]) + Optional(partitionError,[])) | Group (invalidPartition + Optional(partitionOut,[]))
    eqClasses=Group(OneOrMore(eqClass))
    
    #Input descriptors
    iDescriptorTokens="attrib param var"
    inheritance=lBracket+commaSeperatedVars+rBracket
    iDescriptor=Group(oneOf(iDescriptorTokens) + Optional(extStmt,"") + identifier + Group(Optional(inheritance))+statementEnd.suppress())
    iDescriptorInherit=Group(oneOf(iDescriptorTokens) + identifier + Group(inheritance)+codeLineEnd)
    
    #relation between inputs/vars
    dependsOnDecl=Group (Literal("dependsOn ").suppress()+commaSeperatedVars + statementEnd.suppress())
    dependsOn=Group(dependsOnDecl + Group(OneOrMore(subPartition))+ Optional(partitionOut,[]) + Optional(partitionError,[]))
    
    #Full input
    input=Group(iDescriptor + Optional(dependsOn,[]) + Optional(eqClasses,[])) | Group(iDescriptorInherit)
    
    #Test Definition
    testDecl=Group("test" + identifier + "method" + extStmt + Optional("returns" + extStmt) + statementEnd.suppress())
    test=Group(testDecl+Group(OneOrMore(input)))
    
    #Initialisation
    colonSeparatedNameValue=Group(identifier+Literal(":").suppress()+SkipTo(codeLineEnd,True))
    initSection=Literal("init").suppress()+statementEnd.suppress()+Group(OneOrMore(colonSeparatedNameValue))
    
    #Whole Program
    program=initSection+Group(OneOrMore(test))
   
    #End of grammar
    def __init__(self,filename=None):
        """Constructor with no args"""
        if filename is None:
            self.tokens=[]
        else:
            self.loadFromFile(filename)
        
        
    def loadFromFile(self,filename):
        """Loads a file with the program, parses it and stores tokens in tokens attribute"""
        with open(filename) as f:
           self.parseText(f.read())
        
    def parseText(self,text):
        """Parses the string supplied as parameter text, parses it and stores tokens in tokens attribute"""
        gen=self.program.scanString(text,1)
        try:
            tokens,start,end=gen.next()
        except StopIteration:
            try:
                self.program.parseString(text)
            except ParseBaseException, pe:
                raise SyntaxException('Syntax Error, not a valid source file\n%s'%str(pe))
            else:
                raise SyntaxException('Syntax Error, not a valid source file')
        else:
            text=text.expandtabs()
            if end<len(text)-1:
                raise SyntaxException('Not a valid source file\r\nSyntax error after line %d, column %d'%(lineno(end,text),col(end,text)))
        self.tokens=tokens
    
    
    
class ProgramParser(Parser):
    def __init__(self,filename=None):
        Parser.__init__(self,filename)    
        
            
        
class LibraryParser(Parser):
    def __init__(self,filename=None):
        Parser.__init__(self,filename)
    
    #Updated Partition definition
    partitionIdentifier=Parser.identifier
    commonPartition=partitionIdentifier + Optional(Parser.inheritPartition,[]) + Parser.statementEnd.suppress()
    validPartition=Group(Group("valid" + commonPartition) + Parser.partition)
    invalidPartition=Group(Group("invalid" + commonPartition) + Parser.partition)
    
    #Whole Program
    program=Parser.initSection+Group(OneOrMore(validPartition|invalidPartition))

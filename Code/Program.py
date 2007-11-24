from __future__ import absolute_import
import sys, types
#sys.path=['Coders'] + sys.path
from BaseClasses import *
from InitParams import *
from Test import *
from Coders.ICoder import *

# The following 3 functions are taken from the python cookbook
def _get_mod(modulePath):
    try:
        aMod = sys.modules[modulePath]
        if not isinstance(aMod, types.ModuleType):
            raise KeyError
    except KeyError:
        # The last [''] is very important!
        aMod = __import__(modulePath, globals(), locals(), [''])
        sys.modules[modulePath] = aMod
    return aMod

def _get_func(fullFuncName):
    """Retrieve a function object from a full dotted-package name."""
    
    # Parse out the path, module, and function
    lastDot = fullFuncName.rfind(u".")
    funcName = fullFuncName[lastDot + 1:]
    modPath = fullFuncName[:lastDot]
    
    aMod = _get_mod(modPath)
    aFunc = getattr(aMod, funcName)
    
    # Assert that the function is a *callable* attribute.
    assert callable(aFunc), u"%s is not callable." % fullFuncName
    
    # Return a reference to the function itself,
    # not the results of the function.
    return aFunc

def _get_class(fullClassName, parentClass=None):
    """Load a module and retrieve a class (NOT an instance).
    
    If the parentClass is supplied, className must be of parentClass
    or a subclass of parentClass (or None is returned).
    """
    aClass = _get_func(fullClassName)
    
    # Assert that the class is a subclass of parentClass.
    if parentClass is not None:
        if not issubclass(aClass, parentClass):
            raise TypeError(u"%s is not a subclass of %s" %
                            (fullClassName, parentClass))
    
    # Return a reference to the class itself, not an instantiated object.
    return aClass



class Program(ParsedElement, HasChildren):
 
    def __init__(self,tokens=None, name=None, initParams=None):
        self.name=name
        self.inheritedSubPartitions={}
        self.tests=[]
        self.initParams=initParams
        ParsedElement.__init__(self,tokens)
        
    def getCode(self):
        if not self.isPopulated:
            return None
        params=self.initParams.params
        coder=params['language']
        try:      
            coderObject=_get_class('Coders.%sCoder.%sCoder'%(coder,coder),ICoder)()
        except Exception:
            raise SemanticException("Error loading %s Coder object/language not supported"%coder)
        valid=params['valid_cs'] if 'valid_cs' in params else 2
        invalid=params['invalid_cs'] if 'valid_cs' in params else 'bc'
        suites=[]
        coderObject.setInitparams(params)
        try:
            for test in self.tests:
                assert isinstance(test,Test)                
                coderObject.addTest(test.getTestSuite(valid,invalid),test.test,test.method,test.returns)
        except SemanticException, se:
            se.msg+='\nIn %s'%(str(self))
            raise
        else:
            return coderObject.extension, coderObject.getCode()
           
        
    def populate(self):
        try:
            #Get Init Part
            init=self.tokens[0]
            tests=self.tokens[1]
            self.initParams=InitParams(init)
            if 'imports' in self.initParams.params:
                yield 'imp',self.initParams.params['imports']
            self.tests=[Test(test) for test in tests]
            #Populate children
            for test in self.tests:
                gen=test.populate()
                try:
                    typ,val=gen.next()
                    while True:
                        try:
                            c=(yield (typ,val))
                        except Exception, ex:
                            gen.throw(ex)
                        else:
                            typ,val=gen.send(c)
                except StopIteration: pass                
            #-----------Semantic Checks Start here-----------#
            #Check that all names are unique
            self.children=tests
            duplicates=self.getDuplicates()
            if duplicates:
                raise DuplicateDefinitionException("Duplicate Test definitions %s"%(duplicates))
        except SemanticException, error:
            error.msg+="\nIn %s."%(str(self))
            raise
        except Exception:
            raise SemanticException("Could not process %s tokens"%(str(self)))
        else:
            self.isPopulated=True
        
    def __str__(self):
        return 'STDL source file %s'%str(self.name)
                
        
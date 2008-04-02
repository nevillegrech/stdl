from BaseClasses import *
from Exceptions import *

class InitParams(ParsedElement):
    requiredParams=['language']
    delimitedParams=['imports','language_imports']
    possibleParams=set(requiredParams+delimitedParams+['valid_cs','invalid_cs','namespace','classname','runInSTA'])
    def __init__(self,tokens=None):
        ParsedElement.__init__(self,tokens)
        self.params={}
        if tokens is not None:
            self.populate()
    
    def checkAndStoreParams(self,params,exceptionClass):
        extraParams=[param for param in params if not param in self.possibleParams]
        if extraParams:
            raise exceptionClass("%s are not valid initialisation parameters"%(str(extraParams)))
        lackingParams=[param for param in self.requiredParams if not param in params]
        if lackingParams:
            raise exceptionClass("%s required but not found"%(str(lackingParams)))
        for dp in self.delimitedParams:
            if dp in params:
                params[dp]=params[dp].split(",") #Split and format delimited parameter
        for k,v in params.iteritems():
            if isinstance(v, basestring):
                params[k]=v.strip() 
            elif isinstance(v,list):
                params[k]=[i.strip() for i in v]
            else:
                raise ValueError('parameter has to be string or list')
                
        self.params=params
    
    def getInitParams(self):
        return dict((tuple(t) for t in self.tokens))
    
    def populate(self):
        try:
            self.params=self.getInitParams()
            self.checkAndStoreParams(self.params,SemanticInitException)
        except SemanticException, se:
            se.msg+='\nIn %s'%str(self)
            raise
        except Exception, ex:
            raise SemanticException("Error in initialisation Parameters")            
            
    def __str__(self):
        return 'Initialisation Paramters'

            
            
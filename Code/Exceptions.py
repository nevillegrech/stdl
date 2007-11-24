class SemanticException(Exception):
    def __init__(self, msg=None):
        self.msg=msg
        
    def __str__(self):
        return self.msg
        
class DuplicateDefinitionException(SemanticException):
    def __init__(self, msg=None):
        SemanticException.__init__(self,msg)
        
class SemanticInitException(SemanticException):
    def __init__(self,msg):
        SemanticException.__init__(self,msg)
        
class SyntaxSemanticException(SemanticException):
    def __init__(self,msg):
        SemanticException.__init__(self,msg)
        
class CyclicReferenceException(SemanticException):
    def __init__(self,msg):
        SemanticException.__init__(self,msg)

class SyntaxException(SemanticException):
    def __init__(self,msg):
        SemanticException.__init__(self,msg)
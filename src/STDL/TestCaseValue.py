class TestCaseValue:
    
    def __init__(self,value=None,index=None,isJustExternalCode=None,variableName=None,type=None,dataType=None):
        self.value=value
        self.index=index
        self.isJustExternalCode=isJustExternalCode
        self.variableName=variableName
        self.type=type
        self.dataType=dataType
        
       
    def __str__(self):
        return str(self.value) if self.value is not None else ''
        
    def __eq__(s,o):
        return all((s.value==o.value,s.index==o.index, s.variableName==o.variableName,s.type==o.type))\
               if isinstance(o,TestCaseValue) else False       
    def __hash__(self):
        return hash(self.value) ^ hash(self.index) ^ hash(self.variableName) ^ hash(self.type)

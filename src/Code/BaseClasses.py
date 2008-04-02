#Represents ParsedElement class and some exceptions

class ParsedElement(object):
    def __init__(self, tokens=None):
        self.tokens=tokens
        self.isPopulated=False
        
    def populate(self):
        ''' This is an abstract method that has to be overridden.
            Otherwise an exception will be thrown the first time
            the method is called.
            This method is called whenever '''
        raise NotImplementedError('Method not implemented')
    
    def __str__(self):        
        raise NotImplementedError('Method not implemented')
 
class HasChildren(object):
    children=[]
    
    def getDuplicates(self):
        """Returns duplicate child names"""
        names=[test for test in self.children]
        setNames=set(names)
        duplicates=[]
        if len(names)-len(setNames):
            for v in names:
                if v in setNames:
                    setNames.remove(v)
                else:
                    duplicates.append(v)
        return ', '.join((str(d) for d in duplicates))
    
class AbstractPartition(ParsedElement):
    def __init__(self,tokens=None,inputName=None):
        self.subPartitions=[]
        self.inputName=inputName
        self.outPartitionCheck=None
        self.errorPartitionCheck=None
        self.valid=None
        self.__valueCount=None
        self.__valueStart=None
        self.putValueDict={}
        super(AbstractPartition,self).__init__(tokens)
        
    
    def __getValueCount(self):
        if not self.__valueCount:
            self.__valueCount=sum(sp.valueCount for sp in self.subPartitions)
        return self.__valueCount
    valueCount=property(fget=__getValueCount, doc='Returns the number of interesting values')
    
    def __setValueStart(self,valueStart):
        multiplier = 1 if self.valid else -1
        self.__valueStart=valueStart
        i=valueStart #continue please
        for sp in self.subPartitions:
            for x in xrange(sp.valueCount):
                self.putValueDict[i]=sp,x
                i+=multiplier
            
    def __getValueStart(self):
        return self.__valueStart
    valueStart=property(fget=__getValueStart, fset=__setValueStart, doc='Returns the number of interesting values')
    
    def putValues(self,testCase, columnNo,variableName=None,type=None,dataType=None):
        if variableName is None: variableName=self.inputName
        subPartition, valueNo = self.putValueDict[testCase[columnNo].index]
        #Transform depends dictionary
        if 'dependsOn' in dir(self):
            dic=dict((value.variableName, value.value) for value in testCase[1:] if value.variableName in self.dependsOn)
        else: dic={}
        newValue=subPartition.getValue(valueNo,dic,variableName)
        newValue.index=testCase[columnNo].index
        newValue.type=type
        newValue.dataType=dataType
        testCase[columnNo]=newValue
        #Update the out partition check
        testCase[0]+=self.outPartitionCheck
       
    def __invert__(self):
        if self.errorPartitionCheck is None or not self.valid or len(self.errorPartitionCheck)==0:
            return None
        new = self.__class__(inputName=self.inputName)
        for sp in self.subPartitions:
            invert=~sp
            if invert is not None: new.subPartitions.append(invert)
        new.outPartitionCheck, new.valid=self.errorPartitionCheck, not self.valid
        if not new.outPartitionCheck or not new.subPartitions:
            return None
        else:
            return new
    
    



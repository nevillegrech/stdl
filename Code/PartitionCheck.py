from BaseClasses import *
from Exceptions import *
from PartitionCheckItem import *

class PartitionCheck(ParsedElement):
    #Using add operator overload to add partition checks with each other
    def __init__(self,tokens=None, valid=None):
        self.notEmpty=None
        self.valid=valid
        self.checkItems=[]
        self.throws=None
        self.otherCheck=None
        self.out=None
        ParsedElement.__init__(self,tokens)
        
    def getCheckItems(self,testCaseValues):
        res=[]
        for item in self.checkItems:
            assert isinstance (item,PartitionCheckItem)
            d=dict((v.variableName,v.value) for v in testCaseValues)
            d['returns']='returns'
            d['class']='%class%'
            item.calcValue(d)
            res.append(item)
        return res
    
    def populate(self):
        tokens=self.tokens
        if tokens:
            self.out=tokens[0]=='out'
            if ((not self.out) and tokens[0]!='error'):
                raise SemanticException('%s is invalid: %s'%(str(self),tokens[0]))
            if ((not self.valid) and tokens[0]=='error'):
                raise SemanticException("Cannot have an invalid partition with 'error' title in %s"%(str(self)))
            self.valid=self.out and self.valid
            try:
                for items in tokens[1]:
                    item=PartitionCheckItem(items)
                    item.populate()
                    self.checkItems.append(item)
            except SemanticException, se:
                se.msg+="\nIn %s "%(str(self))
                raise
            self.notEmpty=True
            self.throws=any(i.throws for i in self.checkItems)
            if self.throws and self.valid:
                raise SemanticException("There cannot be a valid partition with a 'throws' clause. In %s"%(str(self)))
            #If there is throws, there cannot be throws + anything else
            if self.throws and any(not i.throws for i in self.checkItems):
                raise SemanticException("If there is a throws clause, the other clauses may only be 'throws' in %s"%(str(self)))
        else: self.notEmpty=True
    
    def __add__(self,other):
        #In the case that the check is a valid one
        if not isinstance(other,PartitionCheck):
            return self
        if self.valid is None:
            return other
        if other.valid is None:
            return self
        if self.valid:
            new=PartitionCheck(valid=self.valid and other.valid)
            if new.valid:
                new.throws=False
                new.notEmpty=self.notEmpty or other.notEmpty
                new.checkItems=[]
                new.checkItems.extend(self.checkItems)
                new.checkItems.extend(other.checkItems)
            else:
                new=other
        else:
            #In the case that this check is an invalid one
            if other.valid:
                new=self
            else:
                #This is what happens if there is more than one invalid check
                if not self.notEmpty:
                    new=other
                else:
                    new=PartitionCheck(valid=self.valid and other.valid)
                    new.otherCheck=[]
                    if self.otherCheck:
                        new.otherCheck.extend(self.otherCheck)
                    new.otherCheck.append(other)
                    new.throws=self.throws
                    new.notEmpty=self.notEmpty
                    new.checkItems=self.checkItems
        return new     
        
    def __len__(self):
        return len(self.checkItems) if self.checkItems else 0
    def __nonzero__(self):
        return bool(self.notEmpty)
    def __str__(self):
        return '%s %s partition check'%({True:'Out', False:'Error', None:'Unknown'}[self.out],{True:'valid', False:'invalid', None:'Unknown'}[self.valid])
    
        
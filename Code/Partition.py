from BaseClasses import *
from SubPartition import *
from Exceptions import *
from PartitionCheck import *

class Partition(AbstractPartition):
    def __init__(self,tokens=None, inputName=None):        
        self.name=None
        super(Partition,self).__init__(tokens,inputName)
        
    def populate(self):
        try:     
            title=self.tokens[0][0]
            self.name=int(title[1])
            self.valid=title[0]=="valid"
            #title[2] is a list of inherited partitions
            for temp in title[2]:
                inheritedPartition = [t for t in temp]
                self.subPartitions+=yield ("inp",inheritedPartition)
            #Initialise the individual sub partitions    
            for subPartitionTokens in self.tokens[0][1]:
                sp=SubPartition(tokens=subPartitionTokens,inputName=self.inputName)
                #populate the individual sub partitions here
                sp.populate()
                self.subPartitions.append(sp)
            #populate the out partition checks
            self.outPartitionCheck=PartitionCheck(self.tokens[1],self.valid)
            self.outPartitionCheck.populate()
            #populate the error partition checks
            if len(self.tokens)>2:
                self.errorPartitionCheck=PartitionCheck(self.tokens[2],self.valid)
                self.errorPartitionCheck.populate()
            
        except SemanticException, se:
            se.msg+="\nIn %s"%(str(self))
            raise
        except GeneratorExit:
            pass
        except Exception, e:
            raise SemanticException("Error in Parameters of %s"%(str(self)))
        
        
    def __eq__(self,other):
        return isinstance(other,Partition) and self.valid == other.valid and self.name == other.name
    def __hash__(self):
        return hash(self.name)^hash(self.valid)
    def __str__(self):
        return '%s partition %s'%({True:'valid',False:'invalid',None:'unknown'}[self.valid], str(self.name))
    def __invert__(self):
        new=super(Partition,self).__invert__()
        if new is not None:
            new.name=self.name
        return new
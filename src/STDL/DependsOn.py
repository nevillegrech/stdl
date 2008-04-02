from BaseClasses import *
from Exceptions import *
from TestCaseValue import *
from PartitionCheck import *
from SubPartition import *


class DependsOn(AbstractPartition):
    def __init__(self,tokens=None,inputName=None):
        self.dependsOn=None
        AbstractPartition.__init__(self,tokens,inputName)
        
    def populate(self):
        if self.tokens:
            try:
                #get dependencies
                self.dependsOn=self.tokens[0]._ParseResults__toklist
                #populate subpartitions
                self.subPartitions=[]
                for subPartitionTokens in self.tokens[1]:
                    sp=SubPartition(subPartitionTokens,self.inputName)
                    sp.populate()
                    self.subPartitions.append(sp)
                #populate outPartitionCheck
                self.outPartitionCheck=PartitionCheck(self.tokens[2],True)
                self.outPartitionCheck.populate()
                #populate errorPartitionCheck
                self.errorPartitionCheck=PartitionCheck(self.tokens[3],True)
                self.errorPartitionCheck.populate()
                self.valid=True
            except SemanticException, se:
                se.msg+='\nIn %s'%(str(self))
                raise
            except Exception, e:
                raise SemanticException("Error in Parameters of %s"%(str(self)))
    
              
    def __str__(self):
        return 'DependsOn section'
    
    def __len__(self):
        return len(self.dependsOn) if self.dependsOn else 0
    
    def __invert__(self):
        new=super(DependsOn,self).__invert__()
        if new is not None:
            new.dependsOn=self.dependsOn
        return new
                
            
            
from BaseClasses import ParsedElement
from SubPartition import SubPartition
from Exceptions import *
import copy

class InheritedPartition(ParsedElement):
    def __init__(self,tokens=None):
        self.subPartitions=[]
        self.name=None
        self.valid=None
        super(InheritedPartition,self).__init__(tokens)
    
    def populate (self):
        try:     
            title=self.tokens[0]
            self.name=title[1]
            self.valid=title[0]=="valid"
            #title[2] is a list of inherited partitions
            for temp in title[2]:
                inheritedPartition = [t for t in temp]
                if inheritedPartition: self.subPartitions+=self.__transformPartition((yield ("inp",inheritedPartition)))
            #Initialise the individual sub partitions    
            for subPartitionTokens in self.tokens[1]:
                sp=SubPartition(tokens=subPartitionTokens,inputName=self.name)
                #populate the individual sub partitions here
                sp.populate()
                self.subPartitions.append(sp)
        except SemanticException, se:
            se.msg+="\nIn %s"%(str(self))
            raise
        except Exception, e:
            raise SemanticException("Error in Parameters of %s"%(str(self)))
    
    def __transformPartition(self,inheritedPartition):
        assert isinstance(inheritedPartition,InheritedPartition)
        subPartitions=[]
        for subPartition in inheritedPartition.subPartitions:
            s=copy.copy(subPartition)
            assert isinstance(s,SubPartition)
            if s.containsExternalCode:
                s.code=s.code.replace('%%%s%%'%s.inputName,'%%%s%%'%self.name)
            s.inputName=self.name
            subPartitions.append(s)
        return subPartitions
    
    def __str__(self):
        return '%s Inherited Partition %s'%({True:'valid',False:'invalid',None:'unknown'}[self.valid], str(self.name))
from BaseClasses import *
from Exceptions import *
from DependsOn import *
from Partition import *
from InheritedPartition import InheritedPartition
import copy, random

class Input(ParsedElement, HasChildren):
   
    def __init__(self,tokens=None):
        self.validPartitions=[]
        self.invalidPartitions=[]
        self.dependsOn=set()
        #if I can get the name of this input here, then I'll do it:
        self.name=(tokens[0][2] if len(tokens[0])>3 else tokens[0][1]) if tokens else None
        self.dataType=None
        self.inheritOnly=None
        self.inherits=None
        self.__valueCount=None
        ParsedElement.__init__(self,tokens)
    
    def __getValueCount(self):
        if self.__valueCount is None:
            vps,ips=0,0
            for p in self.validPartitions:
                p.valueStart=vps+1
                vps+=p.valueCount
            for p in self.invalidPartitions:
                p.valueStart=ips-1
                ips-=p.valueCount
            self.__valueCount=vps,-ips
        return self.__valueCount
    valueCount=property(fget=__getValueCount, doc='Returns a tuple containing the number of valid interesting and invalid interesting values')
    
    def populate(self):
        try:
            title=self.tokens[0]
            self.type=title[0]
            if len(title)>3:
                self.dataType=title[1]
                self.name=title[2]
                self.inherits=title[3]
                self.inheritOnly=False
            else:
                self.name=title[1]
                self.inherits=title[2]
                self.inheritOnly=True
        except Exception:
            raise SemanticException("Error in initialisation Parameters of %s"%(str(self)))
        try:
            partitions=[]
            #populate dependsOn clause
            if not self.inheritOnly and self.tokens[1]:
                dependsOn=DependsOn(self.tokens[1],self.name)
                dependsOn.populate()
                partitions.append(dependsOn)
                self.dependsOn=self.dependsOn.union(dependsOn.dependsOn)
            if not self.inheritOnly:
                for partitionTokens in self.tokens[2]:
                    #populating partitions involves sending them any additional data
                    partition=Partition(partitionTokens,self.name)
                    gen=partition.populate()
                    try:
                        typ,val=gen.next()
                        while True:
                            try:
                                c=(yield (typ,val))
                            except Exception, ex:
                                gen.throw(ex)
                            else:
                                if typ=='inp':
                                    #Transform variables
                                    c=self.__transformPartition(c)
                                typ,val=gen.send(c)
                    except StopIteration:
                        pass
                    partitions.append(partition)
            #Check that all names are unique
            self.children=partitions
            duplicates=self.getDuplicates()
            if duplicates:
                raise DuplicateDefinitionException("Duplicate partition numbers %s"%(duplicates))
            if self.inherits:
                #This input inherits from other inputs
                inheritedInputs=[(yield('ini',ini)) for ini in self.inherits] #Exception may be raised from calling code
                for i in inheritedInputs:
                    assert isinstance(i,Input)
                    if self.dependsOn and i.dependsOn:
                        raise SemanticException ('There can only be 1 logical dependsOn clause in all the inheritance tree')
                    self.dependsOn=self.dependsOn.union(i.dependsOn)
                    self.validPartitions+=[copy.copy(p) for p in i.validPartitions]
                    self.invalidPartitions+=[copy.copy(p) for p in i.invalidPartitions]
                    #Inherited partitions inherit also the data type
                    if self.dataType is None:
                        self.dataType=i.dataType
            #separate valid and invalid partitions
            self.validPartitions+=[partition for partition in partitions if partition.valid]
            self.invalidPartitions+=[partition for partition in partitions if not partition.valid]
            #create additional invalid partitions
            for partition in partitions:
                inv=~partition
                if inv is not None:
                    self.invalidPartitions.append(inv)
        except SemanticException, inst:
            inst.msg+="\nIn %s"%(str(self))
            raise
        except GeneratorExit:
            pass
        except Exception, ex:
            raise SemanticException('Error while processing tokens \nIn %s'%(str(self)))
        else:
            self.isPopulated=True
    
    def putValues(self,testSuite,columnNo,variableName=None):
        if variableName is None: variableName=self.name
        for testCase in testSuite:
            index = testCase[columnNo].index
            # if index is 0, populate with a random index - This should/might change in the future
            if index==0:
                index=random.randint(1,self.valueCount[0])
                testCase[columnNo].index=index
            for p in self.validPartitions + self.invalidPartitions:
                assert isinstance(p,AbstractPartition)
                if index in p.putValueDict:
                    p.putValues(testCase,columnNo,variableName,self.type,self.dataType)
                    break
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
            
    def __eq__(self,other):
        return self.name==other.name
    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return '%s %s input'%(self.name,self.dataType)
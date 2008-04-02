from BaseClasses import *
from Exceptions import *
from Input import *
import random

class Test(ParsedElement,HasChildren):

    def __init__(self,tokens=None):
        self.test=None
        self.method=None
        self.returns=None
        self.inputs={}
        self.traversedInputs=set()
        super(Test,self).__init__(tokens)
            
    def getInputs(self,inp):
        f=False
        if inp in self.traversedInputs:
            raise CyclicReferenceException('Cyclic reference: %s cannot inherit from %s'%(str(inp),str(inp)))
        try:
            self.traversedInputs.add(inp)
            if not inp in self.inputs:
                raise SemanticException('%s not found'%(inp))
            input=self.inputs[inp]
            if input.isPopulated: return
            #If the input exists but is yet unpopulated:
            gen=input.populate()
            f=True
            try:
                typ,val=gen.next()
                while True:
                    if typ=='ini':
                        gen2=self.getInputs(val)
                        try:
                            typ2,val2=gen2.next()
                            while True:
                                try:
                                    c=(yield (typ2,val2))
                                except Exception, ex:
                                    gen2.throw(ex)
                                else:
                                    typ2,val2=gen2.send(c)
                        except StopIteration:
                            pass
                        typ,val=gen.send(self.inputs[val])
                    else:
                        try:
                            c=(yield (typ,val))
                        except Exception, ex:
                            gen.throw(ex)
                        else:
                            typ,val=gen.send(c)
            except StopIteration:
                pass   
        finally:
            self.traversedInputs.remove(inp)
    
    def populate(self):
        try:
            title=self.tokens[0]
            params={}
            for n,v in enumerate(title):
                if n%2:
                    params[key]=v
                else:
                    key=v
            self.test=params["test"]
            self.method=params["method"]
        except Exception:
            raise SemanticException("Error in initialisation Parameters of %s"%(str(self)))
        if "returns" in params: self.returns=params["returns"]
        #Create input instances
        for inputTokens in self.tokens[1]:
            input=Input(inputTokens)
            name=input.name
            if name in self.inputs:
                raise DuplicateDefinitionException("Duplicate Input definition %s"%(name))
            self.inputs[input.name]=input
        #-----------Semantic Checks Start here-----------#
        for input in self.inputs:
            try:
                gen=self.getInputs(input)
                typ,val=gen.next()
                while True:
                    assert typ=='inp'
                    try:
                        c=(yield (typ,val))
                    except Exception, ex:
                        gen.throw(ex)
                    else:
                        typ,val=gen.send(c)
            except StopIteration:
                pass
        self.isPopulated=True
        
    def sortDependencies(self):
        inputOrder=[]
        inputs=copy.copy(self.inputs)
        assert isinstance (inputs,dict)
        for i in xrange(len(inputs)):
            satisfied=False
            for name,inp in inputs.iteritems():
                assert isinstance (inp, Input)
                if all((d in inputOrder) for d in inp.dependsOn):
                    inputOrder.append(name)
                    satisfied=True
                    break
                elif not all((d in self.inputs) for d in inp.dependsOn):
                    raise SemanticException('Input %s depends on non-existing input(s)\n In dependsOn clause\n In %s\n In %s'%(name,str(inp),str(self)))
            if not satisfied:
                raise CyclicReferenceException('Cyclic dependsOn referencing in input %s'%(name))
            else: inputs.pop(name)
        return inputOrder
 
    def combine2(self,list1,list2,asList=False):
        '''Combines list1 with list2. This version of the algorithm is much optimised than combineN.
           It is important that lists and not generators/iterators are used as arguments otherwise
           they would get consumed pre-maturely'''
        res=((copy.copy(l1),copy.copy(l2)) for l1 in list1 for l2 in list2)
        return [list(r) for r in res] if asList else res
            
    def horizontalGrowth(self,suite,columnNo,valueCountOrder):
        #Horizontal growth
        c2=columnNo
        pi=set()
        v=valueCountOrder[columnNo] #The number of new values in the new column
        for c1,c in enumerate(valueCountOrder[:columnNo]):
            pi.update(set(self.combine2([TestCaseValue(index=j,variableName=c1) for j in xrange(1,c+1)],
                                    [TestCaseValue(index=j,variableName=c2) for j in xrange(1,v+1)])))
        # pi set calculated, now let's extend the test suite horizontally
        column=[]
        j=0
        for j in xrange(v):
            j+=1
            if j>len(suite):
                break
            new=TestCaseValue(index=j,variableName=columnNo)
            column.append(new)
            #calculate the covered pairs and remove from original set
            covered=set((other,new) for other in suite[j-1])
            pi.difference_update(covered)
        # The following loop only executes if the number of values to the new column
        # is less than the number of test cases
        for j in xrange(j,len(suite)):
            #extend the jth test in T by adding one value such that the result
            #test covers the most number of pairs in pi
            if len(pi)==0:
                #put DC values
                column.append(TestCaseValue(index=None, variableName=c2))
            else:
                #Get the intersections of this variable value to other vars
                max=0,TestCaseValue(index=None, variableName=c2),set()
                intersections=set()
                for b in (TestCaseValue(index=x+1, variableName=c2) for x in range(v)):
                    intersections=set((a,b) for a in suite[j]) #j is not incremented in this loop
                    length=len(intersections.intersection(pi))
                    if length==len(suite[j]):
                        max=length,b,intersections
                        break
                    else:
                        if length>max[0]:
                            max=length,b,intersections
                column.append(max[1])
                pi.difference_update(max[2])
        for tc in suite:
            tc.append(column.pop(0))
        return pi
    
    def verticalGrowth(self,suite,pi):
        assert isinstance(pi,set)
        while pi:
            p_k,p_i=pi.pop()
            k=p_k.variableName
            i=p_i.variableName
            addNew=True
            for tc in suite:
                if tc[k].index==None and (tc[i]==p_i or tc[i].index==None):
                    tc[k]=copy.copy(p_k)
                    tc[i]=copy.copy(p_i)
                    addNew=False
                    break
            if addNew:
                tc=[TestCaseValue(variableName=j,index=None) for j in xrange(len(suite[0]))]
                tc[k]=copy.copy(p_k)
                tc[i]=copy.copy(p_i)
                suite.append(tc)
    
        
    def getPairwiseSuite(self,valueCountOrder):
        #combine the first 2 inputs
        column0=[TestCaseValue(index=i+1,variableName=0) for i in xrange(valueCountOrder[0])]
        if len(valueCountOrder)==1:
            suite=[[c] for c in column0]
        else:
            column1=[TestCaseValue(index=i+1,variableName=1) for i in xrange(valueCountOrder[1])]
            suite=self.combine2(column0,column1,True)
            for i,v in enumerate(valueCountOrder[2:]):
                #horizontal growth
                pi=self.horizontalGrowth(suite,i+2,valueCountOrder)
                #vertical growth
                self.verticalGrowth(suite,pi)
                assert len(pi)==0,len(pi)
        return suite
    
    def getBCInvalidSuite(self,valueCountOrder):
        suite=[]
        noOfVals=len(valueCountOrder)
        for x,v in enumerate(valueCountOrder):
            for i in range(v):
                tc=list(range(noOfVals))
                tc[x]=TestCaseValue(index=-i-1,variableName=x)
                rng=range(noOfVals)
                rng.remove(x)
                for c in rng:
                    tc[c]=TestCaseValue(index=0,variableName=c)
                suite.append(tc)
        return suite
    
    def getECSuite(self,valueCountOrder):
        pass
    
    def getTestSuite(self,valid=2,invalid=None):
        if not self.isPopulated:
            return None
        #sort the inputs according to dependancies
        depOrder=self.sortDependencies()
        #get the number of interesting values for every input
        valueCountOrder=[self.inputs[inp].valueCount for inp in depOrder]
        suite=[]
        if valid==0:
            pass #No valid test cases
        elif valid==2:
            suite+=self.getPairwiseSuite([v1 for v1,v2 in valueCountOrder])
        else:
            raise ValueError('Valid can only be in the range 0,1 or 2')
        if suite:
            # Fill up the don't care values to have a complete test suite
            vars=len(suite[0])
            columns=[[] for i in range(vars)]
            for tc in suite:
                for i in range(vars):
                    if tc[i].index is not None:
                        columns[i].append(tc[i])
            for tc in suite:
                for i,v in enumerate(tc):
                    if v.index is None:
                        tc[i]=copy.copy(random.choice(columns[i]))
        # Insert invalid test cases here
        if invalid=='bc':
            suite+=self.getBCInvalidSuite([v2 for v1,v2 in valueCountOrder])
        # Insert the partition check item to every test case
        for tc in suite:
            assert isinstance (tc,list)
            tc.insert(0,PartitionCheck())
        # Fill up the values of the test cases column by column
        for i,name in enumerate(depOrder):
            input=self.inputs[name]
            assert isinstance(input,Input)
            input.putValues(suite,i+1)
        return suite
 
    def __eq__(self,other):
        return self.test==other.test and self.method==other.method
    
    def __hash__(self):
        return hash(self.method) ^ hash(self.test)
    
    def __str__(self):
        return 'test %s on method %s'%(self.test,self.method)
        
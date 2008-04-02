from BaseClasses import ParsedElement,HasChildren
from InheritedPartition import InheritedPartition
from InitParams import InitParams
from Exceptions import *

class Library(ParsedElement,HasChildren):
    def __init__(self,tokens=None,name=None):
        self.inheritedPartitions={}
        self.initParams=None
        self.name=name
        super(Library,self).__init__(tokens)

    def populate(self):
        try:
            #Get Init Part
            init=self.tokens[0]
            partitionTokens=self.tokens[1]
            self.initParams=InitParams(init)
            if 'imports' in self.initParams.params:
                yield 'imp',self.initParams.params['imports']
            inp=[InheritedPartition(p) for p in partitionTokens]
            #Populate children
            self.inheritedPartitions[self.name]={}
            for p in inp:
                gen=p.populate()
                try:
                    typ,val=gen.next()
                    while True:
                        try:
                            c=(yield (typ,val))
                        except Exception, ex:
                            gen.throw(ex)
                        else:
                            typ,val=gen.send(c)
                except StopIteration: pass
                self.inheritedPartitions[self.name][p.name]=p
            #-----------Semantic Checks Start here-----------#
            #Check that all names are unique
            self.children=self.inheritedPartitions[self.name]
            duplicates=self.getDuplicates()
            if duplicates:
                raise DuplicateDefinitionException("Duplicate Partition definitions %s"%(duplicates))
        except SemanticException, error:
            error.msg+="\nIn %s."%(str(self))
            raise
        except Exception:
            raise SemanticException("Could not process %s tokens"%(str(self)))
        else:
            self.isPopulated=True
        
    def __str__(self):
        return 'STDL library file %s'%str(self.name)
        
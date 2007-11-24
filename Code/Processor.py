from __future__ import with_statement
from Program import Program
from Parser import ProgramParser, LibraryParser
from Exceptions import *
from Library import Library

class Processor(object):
    def __init__(self, filename=None):
        self.parser=None
        self.program=None
        self.filename=filename
        self.inheritedPartitions={}
        if filename is not None:
            self.loadFromFile(filename)
        
    def loadFromFile(self,filename):
        self.parser=ProgramParser(filename)
        #Strip any path information
        name=filename[filename.rfind("\\")+1:] if "\\" in filename else filename
        self.program=Program(self.parser.tokens,name)
        path=filename[:filename.rfind("\\")+1]
        gen=self.program.populate()
        try:
            typ,val=gen.next()
            while True:
                try:
                    if typ=='imp':
                        self.__import([path+v for v in val])
                        typ,val=gen.next()
                    elif typ=='inp':
                        gen.send(self.__getPartition(val))
                    else:
                        raise SemanticException('Unknown request %s'%typ)
                except SemanticException, ex:
                    gen.throw(ex)
        except StopIteration: pass
        
    def __import(self,imp):
        for impItem in imp:
            filename=impItem+'.stdll'
            parser=LibraryParser(filename)
            self.__populateLibrary(parser.tokens,impItem)
        
    def __populateLibrary(self,tokens,name):
        assert isinstance (name,str)
        library=Library(tokens,name[name.rfind("\\")+1:])
        path=name[:name.rfind("\\")+1]
        gen=library.populate()
        try:
            typ,val=gen.next()
            while True:
                try:
                    if typ=='imp':
                        self.__import([path+v for v in val])
                        typ,val=gen.next()
                    elif typ=='inp':
                        typ,val=gen.send(self.__getPartition(val))
                        
                    else:
                        raise SemanticException('Unknown request %s\n'%typ)
                except SemanticException, ex:
                    gen.throw(ex)
        except StopIteration: pass
        self.inheritedPartitions.update(library.inheritedPartitions)
            
            
    def __getPartition(self,partition):
        dic=self.inheritedPartitions
        for r in partition:
            if r in dic:
                dic=dic[r]
            else:
                raise SemanticException('Partition %s not found\n'%'.'.join(partition))
        return dic
            
    
    def getCode(self,out):
        try:
            if not out:
                if self.filename.endswith('.stdl'):
                    out=self.filename[:-5]
                else: out=self.filename
            ext,code=self.program.getCode()
            out+=ext
            with open(out,'w') as f:
                f.write(code)
            return ('Produced file: %s\nOK.\n'%out)
        except IOError, ioe:
            return str(ioe)
        
            
            
        
                
            
            
                

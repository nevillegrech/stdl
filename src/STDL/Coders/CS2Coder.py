from PartitionCheck import PartitionCheck
from PartitionCheckItem import PartitionCheckItem
from TestCaseValue import TestCaseValue
from ICoder import ICoder
from Exceptions import *
import itertools
from pyparsing import QuotedString

class CS2Coder(ICoder):
    """C#.NET 2.0 NUnit coder"""

    #----------------------------------------------------------------------
    extension='.cs'
    def __init__(self):
        """Constructor"""
        self.code=""
        self.items=[]
        self.__namespace=None
        self.__runInSTA=False
    
    def __insertImports(self,imp):
        code=[]
        code+=['using %s;\n'%imp for imp in set(imp)]
        code.append('\n')
        self.items.append(''.join(code))
        
    def setInitparams(self,params):
        assert isinstance(params,dict)
        code=[]
        # check if unit tests should run in STA
        self.__runInSTA=bool(params.get('runInSTA',False))
        staImports=['System.Threading','System.Security.Permissions','System.Reflection'] if self.__runInSTA else []
        # write imports to code
        imports=(['System','NUnit.Framework','NUnit.Framework.SyntaxHelpers']
            + params.get('language_imports',[])
            + staImports)
        self.__insertImports(imports)
        if 'namespace' in params:
            self.__namespace=params['namespace']
            code.append('namespace %s\n{\n'%self.__namespace)
        if not 'classname' in params:
            raise SemanticInitException('Missing classname initialisation parameter.\nIn init section.')
        self.classname=params['classname']
        #generate a meaningful name for the mock object
        self.mockObjectName=self.classname.lower().replace('.','')
        if self.mockObjectName==self.classname:
            self.mockObjectName=self.mockObjectName.upper()
        self.items.append(''.join(code))
        
    def __convert(self,string,dic):
        if not string:
            return string
        def repl(x):
            return "%" if x[0]=="" else dic[x[0]]
        var=QuotedString("%").setParseAction(repl)
        return (var.transformString(string))
        
    def addTest(self,suite,test,method,returns):
        code=['  [TestFixture]\n  public class %s\n  {\n'%test]
        code.append('    public %s %s;\n'%(self.classname,self.mockObjectName))
        code.append('    [SetUp()]\n    public void Init()\n    {\n')
        code.append('      this.%s = new %s();\n'%(self.mockObjectName,self.classname))
        code.append('    }\n\n')
        #find input names        
        for i,tc in enumerate(suite):
            #Test declaration
            code.append('    [Test]\n')
            testCode,attributes=self.__getTestCase(tc,method,returns)
            code+=['    %s\n'%at for at in attributes]
            code.append('    public void %s%d()\n'%(test,i))
            if self.__runInSTA:
                code.append('    {\n')
                code.append('      Exception lastThrownException = null;\n')
                code.append('      Thread staThread = new Thread\n')
                code.append('      (\n')
                code.append('        delegate()\n')
                code.append('        {\n')
                code.append('          try\n')
            code+=(testCode)
            if self.__runInSTA:
                code.append('          catch (Exception ex)\n')
                code.append('          {\n')
                code.append('            lastThrownException = ex;\n')
                code.append('          }\n      });\n')
                code.append('      staThread.SetApartmentState(ApartmentState.STA);\n')
                code.append('      staThread.Start();\n')
                code.append('      staThread.Join();\n')
                code.append('      ThrowException(lastThrownException);\n')
                code.append('    }\n')
        if self.__runInSTA:
            code.append('''
    [ReflectionPermission(SecurityAction.Demand)]
    private static void ThrowException(Exception ex)
    {
      if (ex!=null)
      {
        FieldInfo trace = typeof(Exception).GetField(
          "_remoteStackTraceString",
          BindingFlags.Instance | BindingFlags.NonPublic);
        trace.SetValue(ex, ex.StackTrace + Environment.NewLine);
        throw ex;
      }
    }\n''')
        code.append('  }\n\n')
        self.items.append(''.join(code))
    
    def __getTestCase(self,tc,method,returns):
        code,attributes=['    {\n'],[]        
        names=[v.variableName for v in tc[1:]]
        for v in tc[1:]:
            assert isinstance(v,TestCaseValue)
            #set values
            if v.isJustExternalCode:
                code.append('      %s %s;\n'%(v.dataType, v.variableName))
                code.append('      %s\n'%v.value)
            else:
                code.append('      %s %s = %s;\n'%(v.dataType, v.variableName,v.value))
            if v.type=='attrib':
                code.append('      %s.%s = %s;\n'%(self.mockObjectName,v.variableName,v.variableName))
        #convert method parameters
        try:
            method=self.__convert(method,dict(zip(names,names)))
        except KeyError, ke:
            raise SemanticException('Missing input %s\nIn test header declaration of method %s'%(str(ke),method))            
        #launch method here
        if returns is not None and returns.strip()!='void':
            code.append('      %s returns=this.%s.%s;\n'%(returns,self.mockObjectName,method))
        else:
            code.append('      this.%s.%s;\n'%(self.mockObjectName,method))
        check=tc[0]
        assert isinstance(check,PartitionCheck)
        for checkItem in check.getCheckItems(tc[1:]):
            assert isinstance(checkItem,PartitionCheckItem)
            if not checkItem.throws:
                if checkItem.isJustExternalCode:
                    #convert class variable to actual mock object reference
                    assType=self.__convert(checkItem.value,{'class':'this.%s'%self.mockObjectName})
                else:
                    cmpdict={"<":'LessThan',"<=":'LessThanOrEqualTo',"==":'EqualTo',">=":'GreaterThanOrEqualTo',">":'GreaterThan',"!=":'Not.EqualTo'}
                    assType=', Is.%s(%s)'%(cmpdict[checkItem.comparator],str(checkItem.value))
                code.append('      Assert.That(%s%s);\n'%('returns' if checkItem.addReturns else '',assType))
            else:
                    #The method will fire an exception and therefore it has to be handled
                    attributes.append ('[ExpectedException(typeof(%s))]\n'%checkItem.value)
                
        code.append('    }\n\n')
        return code,attributes
    
    def getCode(self):
        if self.__namespace is not None:
            self.items.append('\n}')
        return ''.join(self.items)
    
    
    

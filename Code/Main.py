from Processor import Processor
from optparse import *
from Exceptions import *
from sys import stderr, stdout
import time

def produceCode(filename,out):
    try:
        processor=Processor(filename)
        msg=processor.getCode(out)
        return True, msg
    except SemanticException, se:
        return False, se.msg
def main():
    argParser = OptionParser(usage="usage: %prog [options] inputfile")
    argParser.add_option("-o", "--out", dest="outfile",
                      help="produce file with a specified output filename", default=None)
    argParser.add_option("-s", "--sourceonly", action="store_true", dest="sourceOnly", default=False,
                      help="do not compile the produced test script")
    argParser.add_option("-q", "--quiet",
                      action="store_false", dest=" ", default=True,
                      help="don't print status messages to stdout")
    (options, args) = argParser.parse_args()
    if len(args)!=1:
        print >> stderr,"Error, no input file specified/too many arguments. Use the '-h' option for help"
        return
    t1=time.clock()
    success,msg=produceCode(args[0],options.outfile)
    
    t2 = time.clock()
    if msg:
        print >> stdout if success else stderr, msg
    if success:
        print >> stdout,'Total execution time: %s Seconds'%str(round(t2-t1, 3))
        
if __name__ == "__main__":
    main()
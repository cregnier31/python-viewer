import os,sys
import ConfigParser
##############################################################
## C.REGNIER Juin 2014
## Class Loader to load different type of file with a pattern factory
##############################################################

class Loader(object):
    # Create based on class name:
    @staticmethod
    def factory(type):
        #return eval(type + "()")
        if type == "ASCII": return AsciiLoader()
        if type == "NML": return NmlLoader()
        if type == "DAT": return ColocLoader()
        assert 0, "Format not known: " + type


class NmlLoader(Loader): 
    def load(self,filename):
        db = ConfigParser.ConfigParser()
        db.read(os.path.expanduser(filename))
        if not db.sections():
            print "Error : Configuration file not found %s ! " %(filename)
            sys.exit(1)
        return db

class AsciiLoader(Loader):
    def read_pos(self,filename):
        data=np.genfromtxt(filename,usecols = (1,2),skip_header=1)
        position=np.array(data)
        return position
class ColocLoader(Loader):
    def read_pos(self,filename):
       #print 'read ASCII file : %s ' %(filename)
       #data=np.genfromtxt(filename,usecols = (5,6))
        data=np.genfromtxt(filename,usecols = (15,16))
        position=np.array(data)
        return position


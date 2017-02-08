#IHM for CMES Viewer
## Main window to explore the catalog and plot the result of your demand
## C.REGNIER January 2017
#

import os,sys,fileinput,shutil,re
import subprocess,shlex
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import pyqtSignal
import fileinput
import resource

from ui_user_interface_dialogs_plot import CmemsProductDialog

## Set stack size and virtual memory to unlimited
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

# 
def startmain():
    app = QtGui.QApplication(sys.argv)
    install_dir=os.getcwd()
    myWindow = CmemsProductDialog(install_dir)
    myWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    import sys
    startmain()


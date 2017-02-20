#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL
from PyQt4.QtGui import QMessageBox,QStatusBar
import sys,os,cPickle
from THREDDS_Explorer_mix_dockwidget_base import Ui_THREDDSViewer
#from libvisor import VisorController
import resource

## Set stack size and virtual memory to unlimited
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

class THREDDSViewer(QtGui.QDockWidget,Ui_THREDDSViewer):
    def __init__(self,parent=None):
        super(THREDDSViewer, self).__init__(parent)
        self.setupUi(self)
        filename=str(parent)+"/../statics/cmems_dic_tot_pit.p"
        self.tmp=str(parent)+"/../tmp/"
        self.mainobj=parent
        self.dict_var={}
        f = file(filename, 'r')
        self.dict_prod=cPickle.load(f)
        print "Read pit  ok"


        ##self.tabWidget.currentChanged.connect(self.runWhenTabChange)
        ##self.connect(self.combo_wcs_coverage, SIGNAL("currentIndexChanged(const QString&)"),
        ##        self._onCoverageSelectorItemChanged)
        ##self.connect(self.combo_wms_layer, SIGNAL("currentIndexChanged(const QString&)"),
        ##        self._onWMSLayerSelectorItemChanged)
        ##self.connect(self.combo_wms_style_type, SIGNAL("currentIndexChanged(const QString&)"),
        ##        self._onWMSStyleTypeSelectorItemChanged)
        ##self.connect(self.combo_wms_time, SIGNAL("currentIndexChanged(int)"), self._onWMSFirstTimeChanged)
        ##self.connect(self.combo_wcs_time, SIGNAL("currentIndexChanged(int)"), self._onWCSFirstTimeChanged)

        ##self.button_req_map.clicked.connect(self._onbuttonReqMapClicked)
        ###self.actionToggleAlwaysOnTop.toggled.connect(self._onAlwaysOnTopPrefsChanged)
        ##self.buttonManageServers.clicked.connect(self._onManageServersRequested)
        ##self.button_req_animation.clicked.connect(self.toggleAnimationMenu)
        ### We add a status bar to this QDockWidget:
        ##self.statusbar = QStatusBar()
        ##self.gridLayout.addWidget(self.statusbar)

        ##self.datasetInUse = None
        ##self.uiAnimation = None
        ##self.currentMap = None
        ##self.wcsAvailableTimes = []
        ##self.wmsAvailableTimes = []

        ##self.firstRunThisSession = True


##    def toggleAnimationMenu(self):
##        """Shows (or hides) the animation menu elements,
##        and instantiate a controller.
##
##        It seems I can not directly hide elements,
##        but I can make another Widget in QDesigner and
##        create/add it to a layout here so... oh well..."""
##
##        if self.uiAnimation is None:
##            self.uiAnimation = AnimationFrame(parent = self)
##            self.uiAnimation.errorSignal.connect(self.postCriticalErrorToUser)
##
##            self.controller.mapInfoRetrieved.connect(self.uiAnimation.setAnimationInformation)
##            if None is not self.currentMap :
##                self.uiAnimation.setAnimationInformation(self.currentMap)
##
##            self.uiAnimation.show()
##            self.button_req_animation.setText("Hide animation menu <<")
##        else:
##            self.uiAnimation.hide()
##            self.uiAnimation = None
##            self.button_req_animation.setText("Show animation menu >>")
##
##    def clearData(self):
##        self.WMSBoundingBoxInfo.setText("No Bounding Box or CRS information available.")
##        self.WMS_northBound.setText("East: No info")
##        self.WMS_southBound.setText("West: No info")
##        self.WMS_eastBound.setText("North: No info")
##        self.WMS_westBound.setText("South: No info")
##        self.combo_wms_layer.clear()
##        self.combo_wms_style_type.clear()
##        self.combo_wms_style_palette.clear()
##        self.combo_wms_time.clear()
##        self.combo_wms_time_last.clear()
##        self.combo_wcs_coverage.clear()
##        self.combo_wcs_time.clear()
##        self.combo_wcs_time_last.clear()
##        self.WCSBoundingBoxInfo.setText("No Bounding Box or CRS information available." )
##        self.WCS_northBound.setText("East: No info")
##        self.WCS_southBound.setText("West: No info")
##        self.WCS_eastBound.setText("North: No info")
##        self.WCS_westBound.setText("South: No info")


##    @pyqtSlot()
##    def _onManageServersRequested(self):
##        """Delegates the action of showing the server manager window to the controller."""
##
##        self.controller.showServerManager()
## 
    def main(self):
        self.show()
 
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    install_dir=os.getcwd()
    imageViewer = THREDDSViewer(install_dir)
    imageViewer.main()
    app.exec_()

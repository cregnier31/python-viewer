#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL
from PyQt4.QtGui import QMessageBox,QStatusBar
import sys
from Main_widget import Ui_THREDDSViewer
from libvisor import VisorController
import resource

## Set stack size and virtual memory to unlimited
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

class THREDDSViewer(QtGui.QDockWidget,Ui_THREDDSViewer):
    def __init__(self,parent=None):
        super(THREDDSViewer, self).__init__(parent)
        self.setupUi(self)
##      Add the controller
        self.controller = VisorController.VisorController()
        self.controller.threddsServerMapObjectRetrieved.connect(self.onNewDatasetsAvailable)
        self.controller.threddsDataSetUpdated.connect(self.onDataSetUpdated)
        self.controller.mapImageRetrieved.connect(self.showNewImage)
        self.controller.standardMessage.connect(self.postInformationMessageToUser)
        self.controller.errorMessage.connect(self.postCriticalErrorToUser)
        self.controller.mapInfoRetrieved.connect(self._onMapInfoReceivedFromController)
        self.controller.batchDownloadFinished.connect(self.createLayerGroup)

#        self.showEmptyDatasetNodes = showEmptyDatasetNodes # TODO: self-explanatory...
        self.combo_dataset_list.currentIndexChanged.connect(self._onDataSetItemChanged)
        self.tree_widget.itemClicked.connect(self._onMapTreeWidgetItemClicked)
        self.tree_widget.itemExpanded.connect(self._onMapTreeWidgetItemExpanded)

        self.tabWidget.currentChanged.connect(self.runWhenTabChange)

        self.connect(self.combo_wcs_coverage, SIGNAL("currentIndexChanged(const QString&)"),
                self._onCoverageSelectorItemChanged)
        self.connect(self.combo_wms_layer, SIGNAL("currentIndexChanged(const QString&)"),
                self._onWMSLayerSelectorItemChanged)
        self.connect(self.combo_wms_style_type, SIGNAL("currentIndexChanged(const QString&)"),
                self._onWMSStyleTypeSelectorItemChanged)
        self.connect(self.combo_wms_time, SIGNAL("currentIndexChanged(int)"), self._onWMSFirstTimeChanged)
        self.connect(self.combo_wcs_time, SIGNAL("currentIndexChanged(int)"), self._onWCSFirstTimeChanged)

        self.button_req_map.clicked.connect(self._onbuttonReqMapClicked)
        #self.actionToggleAlwaysOnTop.toggled.connect(self._onAlwaysOnTopPrefsChanged)
        self.buttonManageServers.clicked.connect(self._onManageServersRequested)
        self.button_req_animation.clicked.connect(self.toggleAnimationMenu)
        # We add a status bar to this QDockWidget:
        self.statusbar = QStatusBar()
        self.gridLayout.addWidget(self.statusbar)

        self.datasetInUse = None
        self.uiAnimation = None
        self.currentMap = None
        self.wcsAvailableTimes = []
        self.wmsAvailableTimes = []

        self.firstRunThisSession = True

###    def show(self):
###        if iface and not iface.mainWindow().restoreDockWidget(self):
###            iface.mainWindow().addDockWidget(Qt.LeftDockWidgetArea, self)
###
###        super(Visor, self).show()
###
###        if self.firstRunThisSession:
###            self.firstRunChecks()
###            self.firstRunThisSession = False
###
###        # If no dataset is selected yet, we will assume the first
###        # thing the user will want to do is actually doing something
###        # related to the servers (pick one from a list, or add a new
###        # one) as there is little else that can be done at this point.
###        # So we present them the screen to do so...
###        if self.datasetInUse is None:
###            self._onManageServersRequested()
###
    def firstRunChecks(self):
        """Convenience method to add any checks which should be performed
        when the user opens the plug-in for first time (be advised this
        is not the same as the first time the plug-in object is created,
        which is on QGIS load)."""
        pass

    def runWhenTabChange(self):
        """Convenience method to add any actions to be performed at tab change."""

        # Show warning for GDAL version, if needed.
        self.checkGdalWindowWarning()

    def toggleAnimationMenu(self):
        """Shows (or hides) the animation menu elements,
        and instantiate a controller.

        It seems I can not directly hide elements,
        but I can make another Widget in QDesigner and
        create/add it to a layout here so... oh well..."""

        if self.uiAnimation is None:
            self.uiAnimation = AnimationFrame(parent = self)
            self.uiAnimation.errorSignal.connect(self.postCriticalErrorToUser)

            self.controller.mapInfoRetrieved.connect(self.uiAnimation.setAnimationInformation)
            if None is not self.currentMap :
                self.uiAnimation.setAnimationInformation(self.currentMap)

            self.uiAnimation.show()
            self.button_req_animation.setText("Hide animation menu <<")
        else:
            self.uiAnimation.hide()
            self.uiAnimation = None
            self.button_req_animation.setText("Show animation menu >>")

    def clearData(self):
        self.WMSBoundingBoxInfo.setText("No Bounding Box or CRS information available.")
        self.WMS_northBound.setText("East: No info")
        self.WMS_southBound.setText("West: No info")
        self.WMS_eastBound.setText("North: No info")
        self.WMS_westBound.setText("South: No info")
        self.combo_wms_layer.clear()
        self.combo_wms_style_type.clear()
        self.combo_wms_style_palette.clear()
        self.combo_wms_time.clear()
        self.combo_wms_time_last.clear()
        self.combo_wcs_coverage.clear()
        self.combo_wcs_time.clear()
        self.combo_wcs_time_last.clear()
        self.WCSBoundingBoxInfo.setText("No Bounding Box or CRS information available." )
        self.WCS_northBound.setText("East: No info")
        self.WCS_southBound.setText("West: No info")
        self.WCS_eastBound.setText("North: No info")
        self.WCS_westBound.setText("South: No info")

    # TODO: Unused (for now)
    @pyqtSlot(bool)
    def _onAlwaysOnTopPrefsChanged(self, newSettingBool):
        """Will change the alwaysontop window modifier to suit the user selection."""

        self.setWindowFlags(self.windowFlags() ^ Qt.WindowStaysOnTopHint)
        QtGui.QMainWindow.show(self)

    @pyqtSlot(list, str)
    def onNewDatasetsAvailable(self, inDataSets, serverName):
        """
        A callback for when the dataSet displayed
        needs to be updated.

        :param inDataSets:  list of DataSet objects which will be
                            available to the user.
        :type inDataSets: list of threddsFetcherRecursos.DataSet objects.

        :param serverName:  An user-friendly representation of this server name.
        :type serverName: str
        """
        StringList = []
        for dataSet in inDataSets:
            StringList.append(dataSet.getName())

        self.setWindowTitle("THREDDS Explorer - Connected: "+serverName)
        self.combo_dataset_list.clear()
        self.combo_dataset_list.addItems(StringList)
        self.combo_dataset_list.setCurrentIndex(0)
        self.postInformationMessageToUser("Dataset list updated: "+str(len(StringList))+ " elements.")
        self.clearData()

    @pyqtSlot(str)
    def postInformationMessageToUser(self, message):
        """
        Will post information messages to the user through
        the status bar.
        :param message: String to use as message to
                            the user.
        :type message: str
        """

        self.statusbar.showMessage(message)

    @pyqtSlot(str)
    def postCriticalErrorToUser(self, errorString):
        """
        To be used with non-recoverable error situations. Shows
        a message box with the error message.

        :param errorString: String to use as message to
                            the user.
        :type  errorString: str
        """

        box = QMessageBox()
        box.setText(errorString)
        box.setIcon(QMessageBox.Critical)
        box.exec_()

    @pyqtSlot(str)
    def _onDataSetItemChanged(self, stringItem):
        """Will receive notifications about this window dataSet
        chosen combobox when the item selected changes."""

        self.tree_widget.clear()
        self.datasetInUse = self.controller.getSingleDataset(self.combo_dataset_list.currentText())
        if self.datasetInUse is None:
            return #If no dataset is available to be shown, we will create no tree.

        rootItem = self.tree_widget.invisibleRootItem();
        newItem = QtGui.QTreeWidgetItem(rootItem, [self.datasetInUse.getName()])
        rootItem.addChild(self._createHierarchy(self.datasetInUse, newItem))

    def _createHierarchy(self, dataSet, treeItemParent):
        """Recursively creates a hierarchy of elements to populate
        a treeWidgetItem from a given dataSet.

        :param dataSet: DataSet object to create an hierarchy from.
        :type dataset: threddsFetcherRecursos.DataSet

        :param treeItemParent: Item which will be this
                                branch parent.
        :type treeItemParent: QTreeWidgetItem"""

        i = 0
        itemsAlreadyAddedToElement = []
        while i < treeItemParent.childCount():
            child = treeItemParent.child(i)
            if child.text(0) == "Loading..." or child.text(0) == "No subsets found":
                treeItemParent.removeChild(child)
            else:
                itemsAlreadyAddedToElement.append(child)
            i = i+1
        elementsAlreadyInTreeItemParent = [x.text(0) for x in itemsAlreadyAddedToElement]
        if dataSet != None:
            for mapElement in dataSet.getAvailableMapList():
                if mapElement.getName() in elementsAlreadyInTreeItemParent:
                    continue
                else:
                    newItem = QtGui.QTreeWidgetItem(treeItemParent, [mapElement.getName()])
                    treeItemParent.addChild(newItem)

            subSets = dataSet.getSubSets()
            if len(subSets) == 0:
                #We add a dummy element so the element open icon is created..
                newItem = QtGui.QTreeWidgetItem(treeItemParent)
                newItem.setText(0,"No subsets found")
                treeItemParent.addChild(newItem)
            else:
                for dataset in subSets:
                    #If an item with the same name as this dataset is found as a subchild
                    #of the parent item, we will use it to build our tree. Otherwise, we
                    #create a new one and append it.
                    itemList = ([x for x in itemsAlreadyAddedToElement if x.text(0) == dataset.getName()])
                    if itemList is None or len(itemList) == 0:
                        item = QtGui.QTreeWidgetItem(treeItemParent, [dataset.getName()])
                        treeItemParent.addChild(self._createHierarchy(dataset, item))
                    else:
                        item = itemList[0]
                        self._createHierarchy(dataset, item)
        else:
            self.postCriticalErrorToUser("WARNING: Attempted to add a null dataset to view.")

    def _onMapTreeWidgetItemClicked(self, mQTreeWidgetItem, column):
        """
        Will receive notifications about the MapTreeWidget
        elements being clicked, so we can update the first
        combobox of WMS/WCS tabs with the layer list.
        """

        self.clearData()
        self.postInformationMessageToUser("")
        if None is mQTreeWidgetItem or None is mQTreeWidgetItem.parent():
            return

        self.controller.getMapObject(str(mQTreeWidgetItem.text(0)), str(mQTreeWidgetItem.parent().text(0)), self.datasetInUse)

    @pyqtSlot(object)
    def _onMapInfoReceivedFromController(self, mapInfoObject):
        #print("_onMapInfoReceivedFromController 1"+str(mapInfoObject))
        self.currentMap = mapInfoObject
        #print("_onMapInfoReceivedFromController 2"+str(self.currentMap))
        if self.currentMap is not None:
            #WCS Data update
            self.currentCoverages = self.controller.getWCSCoverages(self.currentMap)
            if self.currentCoverages is not None:
                for c in self.currentCoverages:
                    self.combo_wcs_coverage.addItem(c.getName())
            else:
                self.combo_wcs_coverage.addItem("No data available.")
            #WMS Data update
            self.currentWMSMapInfo = self.controller.getWMSMapInfo(self.currentMap)
            if self.currentWMSMapInfo is not None:
                for l in self.currentWMSMapInfo.getLayers():
                    self.combo_wms_layer.addItem(l.getName())
            else:
                self.combo_wms_layer.addItem("No data available.")

    def _onMapTreeWidgetItemExpanded(self, mQTreeWidgetItem):
        """
        Once a set is expanded in the tree view we will attempt to
        recover it's data and present it to the user.
        """
        setToUpdate = self.datasetInUse.searchSubsetsByName(
                          str(mQTreeWidgetItem.text(0)), exactMatch=True)
        if setToUpdate is not None and len(setToUpdate) > 0:
            self.controller.mapDataSet(setToUpdate[0], depth=1)

    def onDataSetUpdated(self, dataSetObject):
        """
        Will update the QTreeWidget to include the updated
        dataset object and it's new data.
        """
        if dataSetObject.getParent() is not None:
            parent = self.tree_widget.findItems(dataSetObject.getName(), Qt.MatchRecursive)
        self._createHierarchy(dataSetObject, parent[0])

    @pyqtSlot(str)
    def _onCoverageSelectorItemChanged(self, QStringItem):
        """
        Will triger when the user selects a coverage name in
        the combobox (or that list is updated) so the available
        times to request to server are updated in the other
        combobox for the WCS service.
        """

        self.combo_wcs_time.clear()
        if self.currentCoverages is not None:
            coverageElement = [ x for x in self.currentCoverages if x.getName() == str(QStringItem) ]
            if None is not coverageElement or len(coverageElement) > 0:
                try:
                    self.wcsAvailableTimes = coverageElement[0].getTiempos()
                    self.combo_wcs_time.addItems(self.wcsAvailableTimes)
                    BBinfo = coverageElement[0].getBoundingBoxInfo()
                    self.WCSBoundingBoxInfo.setText("CRS = "+BBinfo.getCRS()
                                                +"\n\n Bounding Box information (decimal degrees):" )
                    self.WCS_eastBound.setText(BBinfo.getEast())
                    self.WCS_westBound.setText(BBinfo.getWest())
                    self.WCS_northBound.setText(BBinfo.getNorth())
                    self.WCS_southBound.setText(BBinfo.getSouth())
                except IndexError:
                    pass

    @pyqtSlot(str)
    def _onWMSLayerSelectorItemChanged(self, QStringItem):
        self.combo_wms_style_type.clear()
        self.combo_wms_style_palette.clear()
        self.combo_wms_time.clear()

        # Only one should be returned here.
        if self.currentWMSMapInfo is not None:
            layerSelectedObject =  [ x for x in self.currentWMSMapInfo.getLayers()
                                    if x.getName() == str(QStringItem) ]

            if layerSelectedObject is not None and len(layerSelectedObject) == 1:
                self.wmsAvailableTimes = layerSelectedObject[0].getTimes()
                self.combo_wms_time.addItems(self.wmsAvailableTimes)
                self.wmsAvailableStyles = layerSelectedObject[0].getStyles()
                self.combo_wms_style_type.addItems(list({(x.getName().split(r"/"))[0]
                                                    for x in self.wmsAvailableStyles}))

                BBinfo = layerSelectedObject[0].getBoundingBoxInfo()
                self.WMSBoundingBoxInfo.setText("CRS = "+BBinfo.getCRS()
                                                +"\n\n Bounding Box information (decimal degrees):" )
                self.WMS_eastBound.setText(BBinfo.getEast())
                self.WMS_westBound.setText(BBinfo.getWest())
                self.WMS_northBound.setText(BBinfo.getNorth())
                self.WMS_southBound.setText(BBinfo.getSouth())

    @pyqtSlot(str)
    def _onWMSStyleTypeSelectorItemChanged(self, qstringitem):
        self.combo_wms_style_palette.clear()
        self.combo_wms_style_palette.addItems(list({(x.getName().split(r"/"))[1]
                                                    for x in self.wmsAvailableStyles
                                                    if str(qstringitem) in x.getName()}))

    @pyqtSlot(int)
    def _onWCSFirstTimeChanged(self, position):
        #print("self.wcsAvailableTimes"+str((sorted(self.wcsAvailableTimes))))
        #print("WCS INDEX: "+str(position))
        self.combo_wcs_time_last.clear()
        #print self.wcsAvailableTimes[position:]
        self.combo_wcs_time_last.addItems(
          (sorted(self.wcsAvailableTimes))[position:])

    @pyqtSlot(int)
    def _onWMSFirstTimeChanged(self, position):
        #print("self.wmsAvailableTimes"+str((sorted(self.wmsAvailableTimes))))
        #print("WMS INDEX: "+str(position))
        self.combo_wms_time_last.clear()
        #print self.wmsAvailableTimes[position:]
        self.combo_wms_time_last.addItems(
          self.wmsAvailableTimes[position:])

    def _onbuttonReqMapClicked(self):
        """
        Action to be performed when the user clicks the
        button to request a new map to be displayed,
        after selecting proper values in the rest of fields.
        """
        self.postInformationMessageToUser("") # reset error display.
        print "Request Map"
        if self.tabWidget.currentIndex() == self.tabWidget.indexOf(self.tab_WCS):
            try:
                selectedBeginTimeIndex = self.wcsAvailableTimes.index(self.combo_wcs_time.currentText())
                selectedFinishTimeIndex = self.wcsAvailableTimes.index(self.combo_wcs_time_last.currentText())+1

                # We retrieve some information about the current selected map, useful
                # to grab the actual CRS used by the map service. Should be changed if
                # CRS is to be user-selectable later via dropdown menu or anything like
                # that.
                if self.currentCoverages is not None:
                    coverageElement = [ x for x in self.currentCoverages if
                            x.getName() == str(self.combo_wcs_coverage.currentText()) ]
                if None is not coverageElement or len(coverageElement) > 0:
                    try:
                        try:
                            north = float(self.WCS_northBound.text())
                            south = float(self.WCS_southBound.text())
                            east = float(self.WCS_eastBound.text())
                            west = float(self.WCS_westBound.text())
                        except ValueError:
                            self.postCriticalErrorToUser("Bounding box values were not valid."
                            +"\nCheck only decimal numbers are used\n(example: 12.44)")
                            return
                        # We retrieve the bounding box CRS information from the
                        # requested coverage, and get the actual box values
                        # from the UI.
                        BBinfo = coverageElement[0].getBoundingBoxInfo()
                        boundingBoxToDownload = BoundingBox()
                        boundingBoxToDownload.setCRS(BBinfo.getCRS())
                        boundingBoxToDownload.setEast(east)
                        boundingBoxToDownload.setWest(west)
                        boundingBoxToDownload.setNorth(north)
                        boundingBoxToDownload.setSouth(south)
                        self.controller.asyncFetchWCSImageFile(
                                    self.currentMap,
                                    self.combo_wcs_coverage.currentText(),
                                    self.wcsAvailableTimes[selectedBeginTimeIndex:selectedFinishTimeIndex],
                                    boundingBox=boundingBoxToDownload)
                    except IndexError:
                        pass
            except Exception as exc:
                self.postInformationMessageToUser("There was an error retrieving the WCS data.")
                QgsMessageLog.logMessage(traceback.format_exc(), "THREDDS Explorer", QgsMessageLog.CRITICAL )
        elif self.tabWidget.currentIndex() == self.tabWidget.indexOf(self.tab_WMS):
            try:
                selectedBeginTimeIndex = self.wmsAvailableTimes.index(self.combo_wms_time.currentText())
                selectedFinishTimeIndex = self.wmsAvailableTimes.index(self.combo_wms_time_last.currentText())+1
                style = self.combo_wms_style_type.currentText()+r"/"+self.combo_wms_style_palette.currentText()

                #We retrieve some information about the current selected map, useful
                #to grab the actual CRS used by the map service. Should be changed if
                #CRS is to be user-selectable later via dropdown menu or anything like
                #that.
                #Only one should be returned here.
                if self.currentWMSMapInfo is not None:
                    layerSelectedObject =  [ x for x in self.currentWMSMapInfo.getLayers()
                                            if x.getName() == str(self.combo_wms_layer.currentText())]

                #We retrieve the bounding box CRS information from the
                #requested coverage, and get the actual box values
                #from the UI.
                if None is not layerSelectedObject or len(layerSelectedObject) > 0:
                    try:
                        north = float(self.WMS_northBound.text())
                        south = float(self.WMS_southBound.text())
                        east = float(self.WMS_eastBound.text())
                        west = float(self.WMS_westBound.text())
                    except ValueError:
                        self.postCriticalErrorToUser("Bounding box values were not valid."
                        +"\nCheck only decimal numbers are used\n(example: 12.44)")
                        return

                    BBinfo = layerSelectedObject[0].getBoundingBoxInfo()
                    boundingBoxToDownload = BoundingBox()
                    boundingBoxToDownload.setCRS(BBinfo.getCRS())
                    boundingBoxToDownload.setEast(east)
                    boundingBoxToDownload.setWest(west)
                    boundingBoxToDownload.setNorth(north)
                    boundingBoxToDownload.setSouth(south)
                    self.controller.asyncFetchWMSImageFile(self.currentMap,
                                                            self.combo_wms_layer.currentText(),
                                                            style,
                                                            self.wmsAvailableTimes[selectedBeginTimeIndex
                                                                                   :selectedFinishTimeIndex],
                                                            boundingBox = boundingBoxToDownload)
            except Exception as exc:
                print(exc)
                self.postInformationMessageToUser("There was an error retrieving the WMS data.")
                QgsMessageLog.logMessage(traceback.format_exc(), "THREDDS Explorer", QgsMessageLog.CRITICAL )

    @pyqtSlot(list, str)
    def createLayerGroup(self, layerList, groupName):
        if layerList:
            groupifier = LayerGroupifier(layerList, groupName)
            groupifier.setSingleLayerSelectionModeInGroup(False)
            groupifier.statusSignal.connect(self.postInformationMessageToUser, Qt.DirectConnection)
            groupifier.groupifyComplete.connect(self._onNewLayerGroupGenerated)
            groupifier.groupify()
        else:
            self.postInformationMessageToUser("There was a problem showing the time series.")

##    @pyqtSlot(QgsLayerTreeGroup, list)
##    def _onNewLayerGroupGenerated(self, groupObject, layerList):
##        """
##        Currently only used to show the first image of a newly created group
##        so the user knows when the operation finishes.
##
##        :param groupObject: The legend group object which was created.
##        :type  groupObject: QgsLayerTreeGrupo
##
##        :param layerList: The layers which are held in the group object.
##        :type  layerList: [QgsLayer]
##        """
##        if (layerList[0]).isValid():
##            iface.legendInterface().setLayerVisible(layerList[0], True)
##        else:
##            self.postInformationMessageToUser("There was a problem showing a layer.")
##
    @pyqtSlot(tuple)
    def showNewImage(self, image):
        """
        Will order this UI to post a new image to the user
        through the qgis window.

        :param image: a tuple consisting of (imageOrLayerObject, Name, Service)
        :type image: (QgsRasterLayer, String, String)

        """

        self.postInformationMessageToUser("Layer '"+image[1]+"' ["+image[2]+"]retrieved")
        layer = image[0]
        if layer and layer.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(layer)
            iface.zoomToActiveLayer()
            iface.legendInterface().refreshLayerSymbology(layer)
        else:
            self.postInformationMessageToUser("There was a problem loading the layer.")

    @pyqtSlot()
    def _onManageServersRequested(self):
        """Delegates the action of showing the server manager window to the controller."""

        self.controller.showServerManager()
 
    def main(self):
        self.show()
 
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    imageViewer = THREDDSViewer()
    imageViewer.main()
    app.exec_()

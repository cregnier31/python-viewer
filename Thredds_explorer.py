
#!/usr/bin/python
# -*- coding: utf-8 -*-
# C.REGNIER February 2017

from PyQt4 import QtGui, QtCore
from PyQt4 import uic
from PyQt4.QtCore import pyqtSlot, SIGNAL, Qt
from PyQt4.QtGui import QMessageBox, QStatusBar
import sys,os,cPickle,io,urllib2
import numpy as np
import xml.etree.ElementTree as ET
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import pyproj
import matplotlib.pyplot as plt
from matplotlib.image import imread
import numpy as np 
import matplotlib as mpl
import matplotlib.cm as cm
from tools import *
from motuclient import *
import owslib
#from THREDDS_Explorer_extract_WMS_dockwidget_base import Ui_THREDDSViewer
from THREDDS_Explorer_extract_Multi_WMS_dockwidget_base import Ui_THREDDSViewer
#from libvisor import VisorController
import resource
from Loader import *
from XmlParser import *
import time
import logging
from libvisor import VisorController
## Set stack size and virtual memory to unlimited
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

class THREDDSViewer(QtGui.QDockWidget,Ui_THREDDSViewer):

    """ Main Class for thredds viewing"""

    def __init__(self,parent=None):
        super(THREDDSViewer, self).__init__(parent)
        self.setupUi(self)
        self.logger= logging.getLogger('THREDDSViewer')
        self.logger.setLevel(20)
        self.initUX(parent)
        self.initProxy(parent)
        self.installEventFilter(self)
        logging.basicConfig()
##      Add the controller
        self.controller = VisorController.VisorController()
        self.controller.threddsServerMapObjectRetrieved.connect(self.onNewDatasetsAvailable)
        self.controller.threddsDataSetUpdated.connect(self.onDataSetUpdated)
        #self.controller.mapImageRetrieved.connect(self.showNewImage)
        self.controller.standardMessage.connect(self.postInformationMessageToUser)
        self.controller.errorMessage.connect(self.postCriticalErrorToUser)
        self.controller.mapInfoRetrieved.connect(self._onMapInfoReceivedFromController)
        self.controller.batchDownloadFinished.connect(self.createLayerGroup)
##      Actions for  Cmems page
        self.connect(self.combo_area_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.openproducts)
        self.connect(self.combo_product_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.opendatasets)
        self.connect(self.combo_dataset_cmems_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.openvariables)
        self.connect(self.combo_variable_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.opentimeanddepth)
        self.connect(self.combo_proj, QtCore.SIGNAL("currentIndexChanged(int)"),self.changesrs)
        self.button_req_map_plot.clicked.connect(self._onbuttonReqMapPlotClicked)
        self.button_req_motu.clicked.connect(self._onbuttonMotuRequest)
##      Action for other page
        self.combo_dataset_list.currentIndexChanged.connect(self._onDataSetItemChanged)
        self.tree_widget.itemClicked.connect(self._onMapTreeWidgetItemClicked)
        self.tree_widget.itemExpanded.connect(self._onMapTreeWidgetItemExpanded)
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
        self.buttonManageServers.clicked.connect(self._onManageServersRequested)
        self.button_req_animation_plot.clicked.connect(self.toggleAnimationMenu)
        self.datasetInUse = None
        self.uiAnimation = None
        self.currentMap = None
        self.wcsAvailableTimes = []
        self.wmsAvailableTimes = []
        self.firstRunThisSession = True

    def initUX(self,parent):

        """ Init UX with a list of area """

        list_area=['ARCTIC','BAL','GLOBAL','IBI','MED','NWS']
        for area in list_area : 
            self.combo_area_list.addItem(str(area))
            self.combo_area_list.setEnabled(True)
            self.combo_product_list.setEnabled(False)
            self.combo_dataset_cmems_list.setEnabled(False)
        filename=str(parent)+"/statics/cmems_dic_tot_pit.p"
        self.tmp=str(parent)+"/tmp/"
        self.mainobj=parent
        self.dict_var={}
        f = file(filename, 'r')
        self.dict_prod=cPickle.load(f)
        self.logger.info("Load catalaog for UX ok")

    def initProxy(self,parent):

        """ Set proxy params if exist """

        params_file=str(parent)+"/statics/params.cfg"
        param_dict=Loader.factory('NML').load(params_file)
        self.proxyserver=str(param_dict.get('proxy','proxy_adress'))
        self.proxyuser=str(param_dict.get('proxy','proxy_user'))
        self.proxypass=str(param_dict.get('proxy','proxy_pass'))
        self.cmemsuser=str(param_dict.get('cmems_server','user_cmems'))
        self.cmemspass=str(param_dict.get('cmems_server','pass_cmems'))

    def changesrs(self) :
        input_srs=str(self.combo_proj.currentText())
        if input_srs == "EPSG:3408" : 
            self.checkBox_arc.setChecked(True)
            self.checkBox_ant.setChecked(False)
        elif input_srs == "EPSG:3409" :
            self.checkBox_arc.setChecked(False)
            self.checkBox_ant.setChecked(True)

    def load_options(self,default_values):

        """ Load options for motu client """

        class cmemsval(dict):
            pass
        values=cmemsval()
        for k,v in default_values.items():
            #print k,v
            setattr(values, k, v)
        return values

    def eventFilter(self, source, event):
            if (event.type() == QtCore.QEvent.Close and isinstance(source, QtGui.QDockWidget)):
                #print source.windowTitle()
                self.logger.error("exit ")
                sys.exit(1)
               # return super(Example, self).eventFilter(source, event)

    def cleardata(self):
        self.combo_product_list.clear()
        self.combo_dataset_cmems_list.clear()
        self.combo_variable_list.clear()
        self.combo_wms_time_first_d.clear()
        self.combo_wms_time_first_h.clear()
        self.combo_wms_time_last_d.clear()
        self.combo_wms_time_last_h.clear()
        self.combo_wms_time_first_d_2.clear()
        self.combo_wms_time_first_h_2.clear()
        self.combo_wms_time_last_d_2.clear()
        self.combo_wms_time_last_h_2.clear()
        self.combo_wms_layer_depth.clear()
        self.combo_wms_layer_depth_2.clear()
        self.combo_wms_layer_depth_max_2.clear()
        self.combo_colorbar.clear()
        self.combo_proj.clear()
        self.logger.info("Clear data")

    def openproducts(self):

        """Populate combobox with products """

        self.logger.info("Open products")
        self.combo_product_list.setEnabled(True)
        frame=self.combo_area_list.currentText()
        self.cleardata()
        list_glo=[]
        if str(frame) == "GLOBAL":
            for key in self.dict_prod.keys():
                if str(frame) in key :
                    list_glo.append(str(key))
        ind=0
        #print "Frame %s " %(frame)
        for key in self.dict_prod.keys():
            if str(frame) == "BAL":
                frame1="_BAL_"
                frame2="-BAL-"
                if frame1 in key or frame2 in key :
                    self.combo_product_list.addItem(str(key))
            elif str(frame) == "NWS":
                frame1="NORTHWESTSHELF_"
                frame2="NWS"
                if frame1 in key or frame2 in key :
                    self.combo_product_list.addItem(str(key))
            elif str(frame) == "GLOBAL":
                if str(frame) in key :
                    if ind ==  0 :
                        self.combo_product_list.addItem(list_glo[5])
                    elif ind ==  5 : 
                        self.combo_product_list.addItem(list_glo[0])
                    else : 
                        self.combo_product_list.addItem(list_glo[ind])
                    ind+=1
            else :
                if str(frame) in key :
                    self.combo_product_list.addItem(str(key))
        self.combo_dataset_cmems_list.setEnabled(True)

    def opendatasets(self): 

        """Populate combobox with datasets """

        self.logger.info("Open Datasets")
        print 'clear'
        self.combo_dataset_cmems_list.clear()
        print 'clear 1'
        self.combo_variable_list.clear()
        print 'clear 2'
        self.combo_wms_time_first_d.clear()
        self.combo_wms_time_first_h.clear()
        print 'clear 3'
        self.combo_wms_time_last_d.clear()
        self.combo_wms_time_last_h.clear()
        print 'clear 4'
        self.combo_wms_time_first_d_2.clear()
        self.combo_wms_time_first_h_2.clear()
        print 'clear 5'
        self.combo_wms_time_last_d_2.clear()
        self.combo_wms_time_last_h_2.clear()
        print 'clear 6'
        self.combo_wms_layer_depth.clear()
        print 'clear 7'
        self.combo_colorbar.clear()
        self.combo_proj.clear()
        print 'clear ok'
        product=str(self.combo_product_list.currentText())
        self.logger.info("Product %s "%(product))
        for key in self.dict_prod[product].keys():
            self.logger.info("Datasets %s "%(key))
            self.combo_dataset_cmems_list.addItem(str(key))
        self.combo_variable_list.setEnabled(True)

    def openvariables(self): 

        """Populate combobox with variables """

        self.logger.info("Open Variable")
        self.combo_wms_time_first_d.clear()
        self.combo_wms_time_first_h.clear()
        self.combo_wms_time_last_d.clear()
        self.combo_wms_time_last_h.clear()
        self.combo_wms_time_first_d_2.clear()
        self.combo_wms_time_first_h_2.clear()
        self.combo_wms_time_last_d_2.clear()
        self.combo_wms_time_last_h_2.clear()
        self.combo_colorbar.clear()
        self.combo_proj.clear()
        # 0 list_variables
        # 1 list_time
        # 2 list_server
        # 3 list_DGF
        # 4 list_MFTP
        # 5 list_WMS
        # 6 list_depth
        # 7 list_resol
        # print "Open variables"
        product=str(self.combo_product_list.currentText())
        dataset=str(self.combo_dataset_cmems_list.currentText())
        self.combo_variable_list.clear()
        url_base=self.dict_prod[product][dataset][5]
        self.logger.info("url %s" %(url_base))
        self.dict_var=ParseXML(url_base)
        self.logger.info("Parse XML OK")
        for key in self.dict_var.keys():
            if not str(key).startswith('Automatically'):
                self.combo_variable_list.addItem(str(key))
        ## Add current in the list if u, v exist

        variable=str(self.combo_variable_list.currentText()) 
        list_area=self.dict_var[str(variable)][2]
        self.lon_WMS_westBound.setText(list_area[0]) 
        self.lon_WMS_eastBound.setText(list_area[1])
        self.lat_WMS_southBound.setText(list_area[2])
        self.lat_WMS_northBound.setText(list_area[3])
        self.lon_WMS_westBound_2.setText(list_area[0]) 
        self.lon_WMS_eastBound_2.setText(list_area[1])
        self.lat_WMS_southBound_2.setText(list_area[2])
        self.lat_WMS_northBound_2.setText(list_area[3])
        self.combo_wms_time_first_d.setEnabled(True)
        self.combo_wms_time_first_h.setEnabled(True)
        self.combo_wms_time_last_d.setEnabled(True)
        self.combo_wms_time_last_h.setEnabled(True)
        self.combo_wms_time_first_d_2.setEnabled(True)
        self.combo_wms_time_first_h_2.setEnabled(True)
        self.combo_wms_time_last_d_2.setEnabled(True)
        self.combo_wms_time_last_h_2.setEnabled(True)
        self.combo_colorbar.setEnabled(True)
        self.combo_proj.setEnabled(True)
        self.lon_WMS_westBound.setEnabled(True)
        self.lon_WMS_eastBound.setEnabled(True)
        self.lat_WMS_northBound.setEnabled(True)
        self.lat_WMS_southBound.setEnabled(True)
        self.lon_WMS_westBound_2.setEnabled(True)
        self.lon_WMS_eastBound_2.setEnabled(True)
        self.lat_WMS_northBound_2.setEnabled(True)
        self.lat_WMS_southBound_2.setEnabled(True)
        ## Open wms server
        ## Find complementary informations from WMS with OWSlib
        try:
            from owslib.wms import WebMapService
        except ImportError:
            raise ImportError('OWSLib required to use wmsimage method')
        self.wms = WebMapService(url_base[0])
        projections=self.wms[variable].crsOptions
        styles=self.wms[variable].styles
        for colorbar in styles.keys():
            self.combo_colorbar.addItem(str(colorbar.split('/')[1]))
        self.minscale_value.setText('-50')
        self.maxscale_value.setText('50')
        self.nbcolors_value.setText('20')
        self.Xpixels_value.setText('800')
        self.Xparallels_value.setText('20')
        self.Ymedians_value.setText('20')
        formats=self.wms.getOperationByName('GetMap').formatOptions
        ind=0
        for proj in projections :
            if str(proj) == "EPSG:4326" or str(proj) == "EPSG:3408" or str(proj) == "EPSG:3409" : 
               self.combo_proj.addItem(str(proj))

    def opentimeanddepth(self) :

        """Populate combobox with time and depth variables """

        self.logger.info("Open time and depth")
        self.combo_wms_time_first_d.clear()
        self.combo_wms_time_first_h.clear()
        self.combo_wms_time_last_d.clear()
        self.combo_wms_time_last_h.clear()
        self.combo_wms_time_first_d_2.clear()
        self.combo_wms_time_first_h_2.clear()
        self.combo_wms_time_last_d_2.clear()
        self.combo_wms_time_last_h_2.clear()
        self.combo_wms_layer_depth.clear()
        self.combo_wms_layer_depth_2.clear()
        self.combo_wms_layer_depth_max_2.clear()
        # Current combobox values
        product=str(self.combo_product_list.currentText())
        dataset=str(self.combo_dataset_cmems_list.currentText())
        variable=str(self.combo_variable_list.currentText())
        print "---------------"
        print product
        print dataset
        print "--------------------"
        print self.dict_prod[product][dataset]

        resol=self.dict_prod[product][dataset][7][0]

        list_time=self.dict_var[str(variable)][1]
        if "daily" in str(resol) :
            self.logger.info("Daily variable")
            for value in list_time:
                day=str(value).split()[0][:-13]
                hour=str(value).split()[0][11:]
                self.combo_wms_time_first_d.addItem(str(day))
                self.combo_wms_time_first_d_2.addItem(str(day))
                self.combo_wms_time_last_d.addItem(str(day))
                self.combo_wms_time_last_d_2.addItem(str(day))
            self.combo_wms_time_first_h.addItem(str(hour))  
            self.combo_wms_time_first_h_2.addItem(str(hour))  
            self.combo_wms_time_last_h.addItem(str(hour))  
            self.combo_wms_time_last_h_2.addItem(str(hour))  
        self.combo_wms_time_first_h.setEnabled(True)
        self.combo_wms_time_first_h_2.setEnabled(True)
        self.combo_wms_time_last_h.setEnabled(True)
        self.combo_wms_time_last_h_2.setEnabled(True)
        if "hourly" in str(resol) :
            self.logger.info("Hourly variable")
            i=0
            day_tmp=''
            for value in list_time :
                day=str(value).split()[0][:-13]
                if day_tmp != day :
                    self.combo_wms_time_first_d.addItem(str(day))
                    self.combo_wms_time_first_d_2.addItem(str(day))
                    self.combo_wms_time_last_d.addItem(str(day))
                    self.combo_wms_time_last_d_2.addItem(str(day))
                    i=i+1
                day_tmp=day
                if i == 1:
                    hour=str(value).split()[0][11:]
                    self.combo_wms_time_first_h.addItem(str(hour))
                    self.combo_wms_time_first_h_2.addItem(str(hour))
                    self.combo_wms_time_last_h.addItem(str(hour))
        list_prof=self.dict_var[variable][0]
        for value in list_prof : 
            prof=str(value).split()[0]
            self.combo_wms_layer_depth.addItem(str(prof))
            self.combo_wms_layer_depth_2.addItem(str(prof))
            self.combo_wms_layer_depth_max_2.addItem(str(prof))
       # if variable == "sea_water_velocity" :
       #    self.checkBox.setEnabled(True)

    def _onbuttonReqMapPlotClicked(self):

        """ Request wms map and plot with matplotlib"""

        self.logger.info("Request WMS image in matplotlib")
        day1=str(self.combo_wms_time_first_d.currentText())
        hour1=str(self.combo_wms_time_first_h.currentText())
        date_val=day1+hour1
        depth=str(self.combo_wms_layer_depth.currentText())
        variable=str(self.combo_variable_list.currentText())
        product=str(self.combo_product_list.currentText())
        dataset=str(self.combo_dataset_cmems_list.currentText())
        xmin=int(float(self.lon_WMS_westBound.text()))
        xmax=int(float(self.lon_WMS_eastBound.text()))
        ymin=int(float(self.lat_WMS_southBound.text()))
        ymax=int(float(self.lat_WMS_northBound.text()))
        dir_out=self.tmp
        rastermin=self.minscale_value.text()
        rastermax=self.maxscale_value.text()
        nb_colors=self.nbcolors_value.text()
        xpixels=float(self.Xpixels_value.text())
        xparallels=int(self.Xparallels_value.text())
        ymeridians=int(self.Ymedians_value.text())
        dpi=300
        colorbar=str(self.combo_colorbar.currentText())
        input_srs=str(self.combo_proj.currentText())
        epsg_val=input_srs.split(':')[1]
        ll_polar=False
	if self.checkBox_arc.isChecked() == True :
            m = Basemap(projection='npstere',boundinglat=ymin,lon_0=0,round=True,resolution='l')   
            #Proj4js.defs["EPSG:3408"] = "+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +a=6371228 +b=6371228 +units=m +no_defs";
            ll_polar=True
            self.logger.info("Projection arctic")
	elif self.checkBox_ant.isChecked() == True :
            m = Basemap(projection='spstere',boundinglat=ymax,lon_0=180,round=True,resolution='l')   
            ll_polar=True
            self.logger.info("Projection antarctic")
	else : 
            m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
                        urcrnrlon=xmax, llcrnrlat=ymin,resolution='i',epsg=epsg_val)   
            self.logger.info("cylindric projection")

        # ypixels not given, find by scaling xpixels by the map aspect ratio.
        ypixels = int(m.aspect*xpixels)
        style='boxfill/'+colorbar
        p = pyproj.Proj(init="epsg:%s" % epsg_val, preserve_units=True)
        xmin,ymin = p(m.llcrnrlon,m.llcrnrlat)
        xmax,ymax = p(m.urcrnrlon,m.urcrnrlat)
        if epsg_val == '4326' :
            xmin = (180./np.pi)*xmin; xmax = (180./np.pi)*xmax
            ymin = (180./np.pi)*ymin; ymax = (180./np.pi)*ymax
        self.logger.info("Bounding Box %i %i %i %i " %(xmin,xmax,ymin,ymax))
        img = self.wms.getmap(layers=[variable],service='wms',bbox=(xmin,ymin,xmax,ymax),
                                  size=(int(xpixels),ypixels),
                                  format='image/png',
                                  elevation=depth,
                                  srs=input_srs,
                                  time=date_val,
                                  colorscalerange=rastermin+','+rastermax,numcolorbands=nb_colors,logscale=False,
                                  styles=[style])
        image=imread(io.BytesIO(img.read()),format='png')
        if variable == "sea_water_velocity" :
            ylabel="magnitude"
        else :
            ylabel=self.wms[variable].abstract

        long_name=self.wms[variable].title
        title=product+" - "+long_name+" "+" - "+date_val
        file_pal='./palettes/thredds/'+colorbar+'.pal'
        my_cmap=compute_cmap(file_pal,colorbar)
        cm.register_cmap(name=colorbar, cmap=my_cmap)
        font=10
        norm = mpl.colors.Normalize(vmin=float(rastermin), vmax=float(rastermax), clip=False) 
        parallels=np.round(np.arange(ymin,ymax+xparallels/2,xparallels))
        meridians = np.round(np.arange(xmin,xmax+ymeridians/2,ymeridians))
        # Plot figure 
        plt.figure(figsize=(20,12))
        if epsg_val == '4326' :
            m.drawcoastlines(color='lightgrey',linewidth=0.25)
            m.fillcontinents(color='lightgrey')
            m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,linewidth=0.2,dashes=[1, 5])
            m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,linewidth=0.2)

        elif ll_polar == True : 
            #m.drawcoastlines(linewidth=0.5)
            m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,linewidth=0.2)
            m.drawmeridians(meridians[:-1],labels=[1,1,1,1],fontsize=10,linewidth=0.2,dashes=[1, 5])
        ## Plot the image
        cs=m.imshow(image,origin='upper',alpha=1,cmap=(cm.get_cmap(colorbar,int(nb_colors))),norm=norm)
        ## Add colorbar
        cb=plt.colorbar(cs,orientation='vertical',format='%4.2f',shrink=0.7)
        cb.ax.set_ylabel(ylabel, fontsize=int(font)+4)
        cl=plt.getp(cb.ax, 'ymajorticklabels')
        plt.setp(cl, fontsize=font)

        plt.title(title,fontsize=font+4,y=1.05)
        plt.savefig('images/'+product+"_"+long_name+"_"+date_val+"_basemap.png",dpi=300,bbox_inches='tight')
        plt.show()

    def _onbuttonMotuRequest(self): 

        """ Motu request with input params """

        self.logger.info("launch motuclient request")
        day1=str(self.combo_wms_time_first_d_2.currentText())
        hour1=str(self.combo_wms_time_first_h_2.currentText())
        day2=str(self.combo_wms_time_last_d_2.currentText())
        hour2=str(self.combo_wms_time_last_h_2.currentText())
        date_min=day1.split('T')[0]+' '+hour1.split('0Z')[0]
        date_max=day2.split('T')[0]+' '+hour2.split('0Z')[0]
        depth_min=str(self.combo_wms_layer_depth_2.currentText()).split('-')[1]
        depth_max=str(self.combo_wms_layer_depth_max_2.currentText()).split('-')[1]
        proxy_server=str(self.proxyserver)
        proxy_user=str(self.proxyuser)
        proxy_pass=str(self.proxypass)
        cmems_user=str(self.cmemsuser)
        cmems_pass=str(self.cmemspass)
        variable=str(self.combo_variable_list.currentText())
        product=str(self.combo_product_list.currentText())
        dataset=str(self.combo_dataset_cmems_list.currentText())
        lon_min=float(self.lon_WMS_westBound_2.text())
        lon_max=float(self.lon_WMS_eastBound_2.text())
        lat_min=float(self.lat_WMS_southBound_2.text())
        lat_max=float(self.lat_WMS_northBound_2.text())
        id_product=dataset
        id_service=str(self.dict_prod[product][dataset][8][0])
        dir_out=self.tmp
        #dir_out="/homelocal-px/px-137/sauvegarde/cregnier/tmp/"
        motu=str(self.dict_prod[product][dataset][2][0])
        date1=date_min.replace('-','')
        date1=date1.replace(':','')
        date1=date1.replace(' ','_')
        date2=date_max.replace('-','')
        date2=date2.replace(':','')
        date2=date2.replace(' ','_')
        outputname='ext-'+dataset+'_'+variable+'_zmin'+str(depth_min)+'zmax_'+str(depth_max)+'_'+str(date1)+'_'+str(date2)+'.nc'
        default_values = {'date_min': str(date_min),'date_max': str(date_max),'depth_min': depth_min, 'depth_max': depth_max,\
                          'longitude_max': lon_max,'longitude_min': lon_min,'latitude_min': lat_min,'latitude_max': lat_max,\
                          'describe': None, 'auth_mode': 'cas', 'motu': motu,'block_size': 65536, 'log_level': 30, 'out_dir': dir_out,\
                          'socket_timeout': None,'sync': None,  'proxy_server': proxy_server,\
                          'proxy_user': proxy_user,'proxy_pwd': proxy_pass, 'user': cmems_user, 'pwd': cmems_pass,\
                          'variable':[variable],'product_id': id_product,'service_id': id_service,'user_agent': None,'out_name': outputname}
        self.logger.info("=======================================")
        self.logger.info("Options")
        self.logger.info(default_values)
        self.logger.info("=======================================")
        _opts = self.load_options(default_values)
        try :
            tic = time.time()
            motu_api.execute_request(_opts)
            toc = time.time()
            self.logger.info("| Motu request Ok %6d sec Elapsed for Motu request %f | " %(toc-tic))
        except Exception, e:
            self.logger.error("Execution failed: %s", e)
            if hasattr(e, 'reason'):
                self.logger.error("reason: %s", e.reason)
            if hasattr(e, 'code'):
                self.logger.error(" . code  %s: ", e.code)
            if hasattr(e, 'read'):
                self.logger.error(" . detail:\n%s", e.read())
        self.logger.info("Launch ncview")
        os.system("/home/modules/versions/64/centos7/ncview/ncview-2.1.1_gnu4.8.2/bin/ncview "+dir_out+outputname)

    ## Function from ThreddViewer pluggin
    def toggleAnimationMenu(self):
        """Shows (or hides) the animation menu elements,
        and instantiate a controller.

        It seems I can not directly hide elements,
        but I can make another Widget in QDesigner and
        create/add it to a layout here so... oh well..."""

        if self.uiAnimation is None:
            self.logger.info("Add animation frame")
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

    def clearData(self):
        self.WMSBoundingBoxInfo.setText("No Bounding Box or CRS information available.")
        self.lat_WMS_northBound.setText("East: No info")
        self.lat_WMS_southBound.setText("West: No info")
        self.lon_WMS_eastBound.setText("North: No info")
        self.lon_WMS_westBound.setText("South: No info")
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
                self.logger.info("Inside WMS")
                selectedBeginTimeIndex = self.wmsAvailableTimes.index(self.combo_wms_time.currentText())
                selectedFinishTimeIndex = self.wmsAvailableTimes.index(self.combo_wms_time_last.currentText())+1
                style = self.combo_wms_style_type.currentText()+r"/"+self.combo_wms_style_palette.currentText()
                self.logger.info("Style %s " %(style))
                #We retrieve some information about the current selected map, useful
                #to grab the actual CRS used by the map service. Should be changed if
                #CRS is to be user-selectable later via dropdown menu or anything like
                #that.
                #Only one should be returned here.
                if self.currentWMSMapInfo is not None:
                    self.logger.info("Get Layer info")
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
                #QgsMessageLog.logMessage(traceback.format_exc(), "THREDDS Explorer", QgsMessageLog.CRITICAL )

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
    @pyqtSlot()
    def _onManageServersRequested(self):
        """Delegates the action of showing the server manager window to the controller."""
        self.controller.showServerManager()
 

    def main(self):
        self.show()
 
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    install_dir=os.getcwd()
    imageViewer = THREDDSViewer(install_dir)
    imageViewer.main()
    app.exec_()

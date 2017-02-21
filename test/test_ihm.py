
#!/usr/bin/python
# -*- coding: utf-8 -*-
# C.REGNIER February 2017

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot,SIGNAL
from PyQt4.QtGui import QMessageBox,QStatusBar
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
from THREDDS_Explorer_extract_WMS_dockwidget_base import Ui_THREDDSViewer
#from libvisor import VisorController
import resource
from Loader import *
import time
import logging
## Set stack size and virtual memory to unlimited
resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

class THREDDSViewer(QtGui.QDockWidget,Ui_THREDDSViewer):

    """ Main Class for thredds viewing"""

    def __init__(self,parent=None):
        super(THREDDSViewer, self).__init__(parent)
        self.setupUi(self)
        self.initUX(parent)
        self.initProxy(parent)
        self.installEventFilter(self)
        logging.basicConfig()
        self.connect(self.combo_area_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.openproducts)
        self.connect(self.combo_product_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.opendatasets)
        self.connect(self.combo_dataset_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.openvariables)
        self.connect(self.combo_variable_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.opentimeanddepth)
        self.button_req_map.clicked.connect(self._onbuttonReqMapClicked)
        self.button_req_motu.clicked.connect(self._onbuttonMotuRequest)
        ##self.tabWidget.currentChanged.connect(self.runWhenTabChange)
        ##self.connect(self.combo_wcs_coverage, SIGNAL("currentIndexChanged(const QString&)"),
        ##        self._onCoverageSelectorItemChanged)
        ##self.connect(self.combo_wms_time, SIGNAL("currentIndexChanged(int)"), self._onWMSFirstTimeChanged)
        ##self.connect(self.combo_wcs_time, SIGNAL("currentIndexChanged(int)"), self._onWCSFirstTimeChanged)

        ###self.actionToggleAlwaysOnTop.toggled.connect(self._onAlwaysOnTopPrefsChanged)
        ##self.buttonManageServers.clicked.connect(self._onManageServersRequested)
        self.button_req_animation.clicked.connect(self.toggleAnimationMenu)
        self.datasetInUse = None
        self.uiAnimation = None
        self.currentMap = None
        ##self.wcsAvailableTimes = []
        ##self.wmsAvailableTimes = []

        ##self.firstRunThisSession = True

    def openproducts(self):

        """Populate combobox with products """

        print "Open products"
        self.combo_product_list.setEnabled(True)
        frame=self.combo_area_list.currentText()
        self.combo_product_list.clear()
        self.combo_dataset_list.clear()
        self.combo_variable_list.clear()
        print str(frame)
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
        self.combo_dataset_list.setEnabled(True)

    def opendatasets(self): 

        """Populate combobox with datasets """

        print "Open datasets"
        self.combo_dataset_list.clear()
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
        product=str(self.combo_product_list.currentText())
        for key in self.dict_prod[product].keys():
            print "Variable"
            self.combo_dataset_list.addItem(str(key))
        self.combo_variable_list.setEnabled(True)

    def openvariables(self): 

        """Populate combobox with variables """

        print "Open Variable"
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
        dataset=str(self.combo_dataset_list.currentText())
        self.combo_variable_list.clear()
        url_base=self.dict_prod[product][dataset][5]
        print 'url'
        print url_base
        self.dict_var=self.getXML(url_base)
        print 'Get XML'
        for key in self.dict_var.keys():
            if not str(key).startswith('Automatically'):
                self.combo_variable_list.addItem(str(key))
        ## Add current in the list if u, v exist

        variable=str(self.combo_variable_list.currentText()) 
        list_area=self.dict_var[str(variable)][2]
        self.WMS_westBound.setText(list_area[0]) 
        self.WMS_eastBound.setText(list_area[1])
        self.WMS_southBound.setText(list_area[2])
        self.WMS_northBound.setText(list_area[3])
        self.WMS_westBound_2.setText(list_area[0]) 
        self.WMS_eastBound_2.setText(list_area[1])
        self.WMS_southBound_2.setText(list_area[2])
        self.WMS_northBound_2.setText(list_area[3])
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
        self.WMS_westBound.setEnabled(True)
        self.WMS_eastBound.setEnabled(True)
        self.WMS_northBound.setEnabled(True)
        self.WMS_southBound.setEnabled(True)
        self.WMS_westBound_2.setEnabled(True)
        self.WMS_eastBound_2.setEnabled(True)
        self.WMS_northBound_2.setEnabled(True)
        self.WMS_southBound_2.setEnabled(True)
        print "Get XML Ok"
        ## Open wms server
        ## Find complementary informations from WMS with OWSlib
        try:
            from owslib.wms import WebMapService
        except ImportError:
            raise ImportError('OWSLib required to use wmsimage method')
        #print 'projection options:'
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

    def getXML(self,url_base):

        """ Get XML from WMS adress """

        version="1.1.1"
        print "Adress %s " %(url_base[0])
        try :
            ## Read xml with urllib2
            url=url_base[0]+'?service=WMS&version='+version+'&request=GetCapabilities'
            request = urllib2.Request(url, headers={"Accept" : "application/xml"})
            u = urllib2.urlopen(request)
            u=urllib2.urlopen(url)
            value=u.read()
            tree= ET.fromstring( value )
            #print ET.dump(tree)
            dict_var={}
            cap = tree.findall('Capability')[0]
            layer1 = cap.findall('Layer')[0]
            layer2 = layer1.findall('Layer')[0]
            layers = layer2.findall('Layer')
            for l in layers:
                ## Find Variable name
                variable_name=l.find('Name').text
                print 'variable %s ' %(variable_name)
                ## Find are of product
                list_area=[]
                box=l.find('BoundingBox')
                lonmin=box.attrib['minx']
                list_area.append(lonmin)
                lonmax=box.attrib['maxx']
                list_area.append(lonmax)
                latmin=box.attrib['miny']
                list_area.append(latmin)
                latmax=box.attrib['maxy']
                list_area.append(latmax)
                ## Find time and prof
                dims=l.findall('Extent')
                list_prof=[]
                list_time=[]
                list_tot=[]
                for dim in dims : 
                    if dim.attrib['name'] == 'elevation' :
                        list_prof=str(dim.text).split(',')
                    if dim.attrib['name'] == 'time' :
                        list_time=str(dim.text).split(',')
                if  list_prof == [] : 
                    list_prof.append('0')
                list_tot.append(list_prof)
                list_tot.append(list_time)
                list_tot.append(list_area)
                dict_var[str(variable_name)]=list_tot
        except:
            raise
            print "Error in WMS procedure"
            sys.exit(1)
        return dict_var

    def opentimeanddepth(self) :

        """Populate combobox with time and depth variables """

        print "Open time and depth"
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
        dataset=str(self.combo_dataset_list.currentText())
        variable=str(self.combo_variable_list.currentText())
        resol=self.dict_prod[product][dataset][7][0]
        list_time=self.dict_var[str(variable)][1]
        if "daily" in str(resol) :
            print "Daily variable"
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
            print "Hourly variable"
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

    def load_options(self,default_values):
        class cmemsval(dict):
            pass
        values=cmemsval()
        for k,v in default_values.items():
            print k,v
            setattr(values, k, v)
        return values

    def initUX(self,parent):

        """ Init UX with a list of area """

        list_area=['ARCTIC','BAL','GLOBAL','IBI','MED','NWS']
        for area in list_area : 
            self.combo_area_list.addItem(str(area))
            self.combo_area_list.setEnabled(True)
            self.combo_product_list.setEnabled(False)
            self.combo_dataset_list.setEnabled(False)
        filename=str(parent)+"/../statics/cmems_dic_tot_pit.p"
        self.tmp=str(parent)+"/../tmp/"
        self.mainobj=parent
        self.dict_var={}
        f = file(filename, 'r')
        self.dict_prod=cPickle.load(f)
        print "Load UX ok"

    def initProxy(self,parent):

        """ Set proxy params if exist """

        params_file=str(parent)+"/../statics/params.cfg"
        print params_file
        param_dict=Loader.factory('NML').load(params_file)
        self.proxyserver=str(param_dict.get('proxy','proxy_adress'))
        self.proxyuser=str(param_dict.get('proxy','proxy_user'))
        self.proxypass=str(param_dict.get('proxy','proxy_pass'))
        self.cmemsuser=str(param_dict.get('cmems_server','user_cmems'))
        self.cmemspass=str(param_dict.get('cmems_server','pass_cmems'))

    def _onbuttonReqMapClicked(self):

        """ Request wms map and plot with matplotlib"""

        day1=str(self.combo_wms_time_first_d.currentText())
        hour1=str(self.combo_wms_time_first_h.currentText())
        date_val=day1+hour1
        depth=str(self.combo_wms_layer_depth.currentText())
        variable=str(self.combo_variable_list.currentText())
        product=str(self.combo_product_list.currentText())
        dataset=str(self.combo_dataset_list.currentText())
        xmin=int(float(self.WMS_westBound.text()))
        xmax=int(float(self.WMS_eastBound.text()))
        ymin=int(float(self.WMS_southBound.text()))
        ymax=int(float(self.WMS_northBound.text()))
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
##	if self.checkBox_2.isChecked() == True :
##	   print "Projection arctic"
##           #m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
##           #            urcrnrlon=xmax, llcrnrlat=ymin,resolution='l',epsg=epsg_val)   
##           ##m = Basemap(projection='npstere',boundinglat=ymin,lon_0=0,round=True,resolution='l')   
##           m = Basemap(projection='npstere',boundinglat=ymin,lon_0=0,round=True,resolution='l')   
##            #Proj4js.defs["EPSG:3408"] = "+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +a=6371228 +b=6371228 +units=m +no_defs";
##            #
##           ll_polar=True
##	elif self.checkBox_3.isChecked() == True :
##	   print "Projection antarctic"
##           m = Basemap(projection='spstere',boundinglat=ymax,lon_0=180,round=True,resolution='l')   
##           ll_polar=True
##	else : 
        m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
                    urcrnrlon=xmax, llcrnrlat=ymin,resolution='l',epsg=epsg_val)   
        print "cylindric projection"

        # ypixels not given, find by scaling xpixels by the map aspect ratio.
        ypixels = int(m.aspect*xpixels)
        style='boxfill/'+colorbar
        print input_srs
        print epsg_val
        p = pyproj.Proj(init="epsg:%s" % epsg_val, preserve_units=True)
        xmin,ymin = p(m.llcrnrlon,m.llcrnrlat)
        xmax,ymax = p(m.urcrnrlon,m.urcrnrlat)
        if epsg_val == '4326' :
            xmin = (180./np.pi)*xmin; xmax = (180./np.pi)*xmax
            ymin = (180./np.pi)*ymin; ymax = (180./np.pi)*ymax
            print "Cylindric projection"
        print xmin,xmax,ymin,ymax
        print style
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

        print "OK launch motuclient command"
        day1=str(self.combo_wms_time_first_d_2.currentText())
        hour1=str(self.combo_wms_time_first_h_2.currentText())
        day2=str(self.combo_wms_time_last_d_2.currentText())
        hour2=str(self.combo_wms_time_last_h_2.currentText())
        date_min=day1.split('T')[0]+' '+hour1.split('0Z')[0]
        date_max=day2.split('T')[0]+' '+hour2.split('0Z')[0]
        depth_min=str(self.combo_wms_layer_depth_2.currentText()).split('-')[1]
        depth_max=str(self.combo_wms_layer_depth_max_2.currentText()).split('-')[1]
        print depth_min,depth_max
        #print depth_min,depth_max
        print "proxy"
        proxy_server=str(self.proxyserver)
        proxy_user=str(self.proxyuser)
        proxy_pass=str(self.proxypass)
        cmems_user=str(self.cmemsuser)
        cmems_pass=str(self.cmemspass)
        variable=str(self.combo_variable_list.currentText())
        product=str(self.combo_product_list.currentText())
        dataset=str(self.combo_dataset_list.currentText())
        lon_min=float(self.WMS_westBound_2.text())
        lon_max=float(self.WMS_eastBound_2.text())
        lat_min=float(self.WMS_southBound_2.text())
        lat_max=float(self.WMS_northBound_2.text())
        id_product=dataset
        id_service=str(self.dict_prod[product][dataset][8][0])
        print "id service %s " %(id_service)
        dir_out=self.tmp
        #dir_out="/homelocal-px/px-137/sauvegarde/cregnier/tmp/"
        print "OK %s " %(dir_out) 
        motu=str(self.dict_prod[product][dataset][2][0])
        date1=date_min.replace('-','')
        date1=date1.replace(':','')
        date1=date1.replace(' ','_')
        date2=date_max.replace('-','')
        date2=date2.replace(':','')
        date2=date2.replace(' ','_')
        print proxy_server,proxy_user,proxy_pass
        outputname='ext-'+dataset+'_'+variable+'_zmin'+str(depth_min)+'zmax_'+str(depth_max)+'_'+str(date1)+'_'+str(date2)+'.nc'
        default_values = {'date_min': str(date_min),'date_max': str(date_max),'depth_min': depth_min, 'depth_max': depth_max,\
                          'longitude_max': lon_max,'longitude_min': lon_min,'latitude_min': lat_min,'latitude_max': lat_max,\
                          'describe': None, 'auth_mode': 'cas', 'motu': motu,'block_size': 65536, 'log_level': 30, 'out_dir': dir_out,\
                          'socket_timeout': None,'sync': None,  'proxy_server': proxy_server,\
                          'proxy_user': proxy_user,'proxy_pwd': proxy_pass, 'user': cmems_user, 'pwd': cmems_pass,\
                          'variable':[variable],'product_id': id_product,'service_id': id_service,'user_agent': None,'out_name': outputname}
        print "======================================="
        print "Options"
        print default_values

        _opts = self.load_options(default_values)
        print "======================================="
        try :
            tic = time.time()
            print "Execute motu"
            motu_api.execute_request(_opts)
            toc = time.time()
            print '| %6d sec Elapsed for Motu request |' %(toc-tic)
            print "Motu OK"
        except :
        ##except Exception, e:
            print "error"
            sys.exit(1)
        ##    print "Execution failed: %s", e
        ##    if hasattr(e, 'reason'):
        ##        print "reason: %s", e.reason
        ##    if hasattr(e, 'code'):
        ##        print ' . code  %s: ', e.code
        ##    if hasattr(e, 'read'):
        ##        print ' . detail:\n%s', e.read()
        print "Open File in Mercator interface"
        print "======================================="
        print "Open OK launch ncview"
        os.system("/home/modules/versions/64/centos7/ncview/ncview-2.1.1_gnu4.8.2/bin/ncview "+dir_out+outputname)

    def toggleAnimationMenu(self):
        """Shows (or hides) the animation menu elements,
        and instantiate a controller.

        It seems I can not directly hide elements,
        but I can make another Widget in QDesigner and
        create/add it to a layout here so... oh well..."""

        if self.uiAnimation is None:
            print "Add animation frame"
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
    def eventFilter(self, source, event):
            if (event.type() == QtCore.QEvent.Close and isinstance(source, QtGui.QDockWidget)):
                #print source.windowTitle()
                print "exit "
                sys.exit(1)
               # return super(Example, self).eventFilter(source, event)
    def main(self):
        self.show()
 
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    install_dir=os.getcwd()
    imageViewer = THREDDSViewer(install_dir)
    imageViewer.main()
    app.exec_()

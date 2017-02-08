# coding: utf8
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
## C.REGNIER January 2017
## Creation of the interface for CMEMS WMS server
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
import cPickle
import os,io,urllib2
import time,sys
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
import owslib

#class CmemsProductDialog(QtGui.QMainWindow):
class CmemsProductDialog(QDialog):
    """ Dialog for searching cmems product and launch a request to the selected product """
    def __init__(self,parent):
        print "Read pit"
        ## Open cmems pit
        filename=str(parent)+"/statics/cmems_dic_tot_pit.p"
        self.tmp=str(parent)+"/tmp/"
        self.mainobj=parent
        self.dict_var={}
        f = file(filename, 'r')
        self.dict_prod=cPickle.load(f)
        print "Read pit  ok"
        QDialog.__init__(self)
       # self.2htab=["1",]
        self.setWindowTitle("Access CMEMS viewer")
        self.resize(579, 881)
        layout=QFormLayout(self)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(230, 820, 341, 41))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(60, 20, 491, 71))
        self.groupBox.setTitle((""))
        self.groupBox.setObjectName(("groupBox"))
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(220, 20, 241, 31))
        self.comboBox.setObjectName(("comboBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(0, 20, 101, 31))
        self.label.setObjectName(("label"))
        self.groupBox_2 = QtGui.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(50, 90, 491, 71))
        self.groupBox_2.setTitle((""))
        self.groupBox_2.setObjectName(("groupBox_2"))
        self.comboBox_2 = QtGui.QComboBox(self.groupBox_2)
        self.comboBox_2.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_2.setObjectName(("comboBox_2"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(0, 20, 111, 31))
        self.label_2.setObjectName(("label_2"))
        self.groupBox_3 = QtGui.QGroupBox(self)
        self.groupBox_3.setGeometry(QtCore.QRect(50, 160, 491, 71))
        self.groupBox_3.setTitle((""))
        self.groupBox_3.setObjectName(("groupBox_3"))
        self.comboBox_3 = QtGui.QComboBox(self.groupBox_3)
        self.comboBox_3.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_3.setObjectName(("comboBox_3"))
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(0, 20, 111, 31))
        self.label_3.setObjectName(("label_3"))
        self.groupBox_4 = QtGui.QGroupBox(self)
        self.groupBox_4.setGeometry(QtCore.QRect(50, 230, 491, 71))
        self.groupBox_4.setTitle((""))
        self.groupBox_4.setObjectName(("groupBox_4"))
        self.comboBox_4 = QtGui.QComboBox(self.groupBox_4)
        self.comboBox_4.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_4.setObjectName(("comboBox_4"))
        self.label_4 = QtGui.QLabel(self.groupBox_4)
        self.label_4.setGeometry(QtCore.QRect(0, 20, 121, 31))
        self.label_4.setObjectName(("label_4"))
        self.groupBox_5 = QtGui.QGroupBox(self)
        self.groupBox_5.setGeometry(QtCore.QRect(40, 300, 521, 161))
        self.groupBox_5.setTitle((""))
        self.groupBox_5.setObjectName(("groupBox_5"))
        self.label_5 = QtGui.QLabel(self.groupBox_5)
        self.label_5.setGeometry(QtCore.QRect(0, 60, 101, 31))
        self.label_5.setObjectName(("label_5"))
        self.lineEdit = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit.setGeometry(QtCore.QRect(125, 59, 121, 41))
        self.lineEdit.setObjectName(("lineEdit"))
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_2.setGeometry(QtCore.QRect(365, 55, 121, 41))
        self.lineEdit_2.setObjectName(("lineEdit_2"))
        self.lineEdit_3 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_3.setGeometry(QtCore.QRect(242, 100, 121, 41))
        self.lineEdit_3.setObjectName(("lineEdit_3"))
        self.lineEdit_4 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_4.setGeometry(QtCore.QRect(247, 19, 113, 41))
        self.lineEdit_4.setObjectName(("lineEdit_4"))
        self.label_6 = QtGui.QLabel(self.groupBox_5)
        self.label_6.setGeometry(QtCore.QRect(165, 38, 71, 21))
        self.label_6.setObjectName(("label_6"))
        self.label_7 = QtGui.QLabel(self.groupBox_5)
        self.label_7.setGeometry(QtCore.QRect(395, 28, 66, 21))
        self.label_7.setObjectName(("label_7"))
        self.label_8 = QtGui.QLabel(self.groupBox_5)
        self.label_8.setGeometry(QtCore.QRect(275, 78, 66, 21))
        self.label_8.setObjectName(("label_8"))
        self.label_9 = QtGui.QLabel(self.groupBox_5)
        self.label_9.setGeometry(QtCore.QRect(270, -1, 66, 21))
        self.label_9.setObjectName(("label_9"))
        self.groupBox_6 = QtGui.QGroupBox(self)
        self.groupBox_6.setGeometry(QtCore.QRect(50, 450, 491, 71))
        self.groupBox_6.setTitle((""))
        self.groupBox_6.setObjectName(("groupBox_6"))
        self.comboBox_5 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_5.setGeometry(QtCore.QRect(110, 20, 181, 31))
        self.comboBox_5.setObjectName(("comboBox_5"))
        self.label_10 = QtGui.QLabel(self.groupBox_6)
        self.label_10.setGeometry(QtCore.QRect(0, 20, 41, 31))
        self.label_10.setObjectName(("label_10"))
        self.comboBox_6 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_6.setGeometry(QtCore.QRect(310, 20, 171, 29))
        self.comboBox_6.setObjectName(("comboBox_6"))
        self.groupBox_7 = QtGui.QGroupBox(self)
        self.groupBox_7.setGeometry(QtCore.QRect(30, 510, 541, 71))
        self.groupBox_7.setTitle((""))
        self.groupBox_7.setObjectName(("groupBox_7"))
        self.comboBox_7 = QtGui.QComboBox(self.groupBox_7)
        self.comboBox_7.setGeometry(QtCore.QRect(130, 20, 281, 31))
        self.comboBox_7.setObjectName(("comboBox_7"))
        self.label_11 = QtGui.QLabel(self.groupBox_7)
        self.label_11.setGeometry(QtCore.QRect(20, 20, 51, 31))
        self.label_11.setObjectName(("label_11"))
        self.checkBox = QtGui.QCheckBox(self.groupBox_7)
        self.checkBox.setGeometry(QtCore.QRect(420, 20, 111, 26))
        self.checkBox.setObjectName("checkBox")
        self.groupBox_8 = QtGui.QGroupBox(self)
        self.groupBox_8.setGeometry(QtCore.QRect(40, 580, 511, 141))
        self.groupBox_8.setTitle((""))
        self.groupBox_8.setObjectName(("groupBox_8"))
        self.comboBox_8 = QtGui.QComboBox(self.groupBox_8)
        self.comboBox_8.setGeometry(QtCore.QRect(90, 30, 141, 31))
        self.comboBox_8.setObjectName(("comboBox_8"))
        self.label_12 = QtGui.QLabel(self.groupBox_8)
        self.label_12.setGeometry(QtCore.QRect(5, 30, 141, 31))
        self.label_12.setObjectName(("label_12"))
        self.lineEdit_5 = QtGui.QLineEdit(self.groupBox_8)
        self.lineEdit_5.setGeometry(QtCore.QRect(260, 30, 113, 33))
        self.lineEdit_5.setObjectName(("lineEdit_5"))
        self.lineEdit_6 = QtGui.QLineEdit(self.groupBox_8)
        self.lineEdit_6.setGeometry(QtCore.QRect(390, 30, 113, 33))
        self.lineEdit_6.setObjectName(("lineEdit_6"))
        self.lineEdit_7 = QtGui.QLineEdit(self.groupBox_8)
        self.lineEdit_7.setGeometry(QtCore.QRect(262, 100, 111, 33))
        self.lineEdit_7.setObjectName(("lineEdit_7"))
        self.lineEdit_8 = QtGui.QLineEdit(self.groupBox_8)
        self.lineEdit_8.setGeometry(QtCore.QRect(390, 100, 111, 33))
        self.lineEdit_8.setObjectName(("lineEdit_8"))
        self.label_13 = QtGui.QLabel(self.groupBox_8)
        self.label_13.setGeometry(QtCore.QRect(280, 0, 66, 21))
        self.label_13.setObjectName(("label_13"))
        self.label_14 = QtGui.QLabel(self.groupBox_8)
        self.label_14.setGeometry(QtCore.QRect(410, 0, 66, 21))
        self.label_14.setObjectName(("label_14"))
        self.label_15 = QtGui.QLabel(self.groupBox_8)
        self.label_15.setGeometry(QtCore.QRect(280, 70, 66, 21))
        self.label_15.setObjectName(("label_15"))
        self.label_16 = QtGui.QLabel(self.groupBox_8)
        self.label_16.setGeometry(QtCore.QRect(420, 70, 66, 21))
        self.label_16.setObjectName(("label_16"))
        self.comboBox_9 = QtGui.QComboBox(self.groupBox_8)
        self.comboBox_9.setGeometry(QtCore.QRect(110, 100, 111, 29))
        self.comboBox_9.setObjectName(("comboBox_9"))
        self.label_17 = QtGui.QLabel(self.groupBox_8)
        self.label_17.setGeometry(QtCore.QRect(10, 100, 91, 31))
        self.label_17.setObjectName(("label_17"))
        self.groupBox_9 = QtGui.QGroupBox(self)
        self.groupBox_9.setGeometry(QtCore.QRect(50, 730, 501, 91))
        self.groupBox_9.setObjectName(("groupBox_9"))
        self.lineEdit_9 = QtGui.QLineEdit(self.groupBox_9)
        self.lineEdit_9.setGeometry(QtCore.QRect(150, 20, 81, 33))
        self.lineEdit_9.setObjectName(("lineEdit_9"))
        self.lineEdit_10 = QtGui.QLineEdit(self.groupBox_9)
        self.lineEdit_10.setGeometry(QtCore.QRect(260, 20, 81, 33))
        self.lineEdit_10.setObjectName(("lineEdit_10"))
        self.lineEdit_11 = QtGui.QLineEdit(self.groupBox_9)
        self.lineEdit_11.setGeometry(QtCore.QRect(370, 20, 61, 33))
        self.lineEdit_11.setObjectName(("lineEdit_11"))
        self.label_20 = QtGui.QLabel(self.groupBox_9)
        self.label_20.setGeometry(QtCore.QRect(380, 0, 31, 21))
        self.label_20.setObjectName(("label_20"))
        self.checkBox_2 = QtGui.QCheckBox(self.groupBox_9)
        self.checkBox_2.setGeometry(QtCore.QRect(150, 70, 94, 26))
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtGui.QCheckBox(self.groupBox_9)
        self.checkBox_3.setGeometry(QtCore.QRect(230, 70, 94, 26))
        self.checkBox_3.setObjectName("checkBox_2")
        self.label_18 = QtGui.QLabel(self)
        self.label_18.setGeometry(QtCore.QRect(210, 730, 66, 21))
        self.label_18.setObjectName(("label_18"))
        self.label_19 = QtGui.QLabel(self)
        self.label_19.setGeometry(QtCore.QRect(310, 730, 71, 21))
        self.label_19.setObjectName(("label_19"))
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.openproducts)
        QtCore.QObject.connect(self.comboBox_2, QtCore.SIGNAL("currentIndexChanged(int)"),self.opendatasets)
        QtCore.QObject.connect(self.comboBox_3, QtCore.SIGNAL("currentIndexChanged(int)"),self.openvariables)
        QtCore.QObject.connect(self.comboBox_4, QtCore.SIGNAL("currentIndexChanged(int)"),self.opentimeanddepth)
        QtCore.QObject.connect(self.comboBox_9, QtCore.SIGNAL("currentIndexChanged(int)"),self.changesrs)
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        day1=str(self.comboBox_5.currentText())
        hour1=str(self.comboBox_6.currentText())
        date_val=day1+hour1
        depth=str(self.comboBox_7.currentText())
        variable=str(self.comboBox_4.currentText())
        product=str(self.comboBox_2.currentText())
        dataset=str(self.comboBox_3.currentText())
        xmin=int(float(self.lineEdit.text()))
        xmax=int(float(self.lineEdit_2.text()))
        ymin=int(float(self.lineEdit_3.text()))
        ymax=int(float(self.lineEdit_4.text()))
        dir_out=self.tmp
        rastermin=self.lineEdit_5.text()
        rastermax=self.lineEdit_6.text()
        nb_colors=self.lineEdit_7.text()
        xpixels=float(self.lineEdit_8.text())
        xparallels=int(self.lineEdit_9.text())
        ymeridians=int(self.lineEdit_10.text())
        dpi=int(self.lineEdit_11.text())
        colorbar=str(self.comboBox_8.currentText())
        input_srs=str(self.comboBox_9.currentText())
        epsg_val=input_srs.split(':')[1]
        ll_polar=False
	if self.checkBox_2.isChecked() == True :
	   print "Projection arctic"
           #m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
           #            urcrnrlon=xmax, llcrnrlat=ymin,resolution='l',epsg=epsg_val)   
           ##m = Basemap(projection='npstere',boundinglat=ymin,lon_0=0,round=True,resolution='l')   
           m = Basemap(projection='npstere',boundinglat=ymin,lon_0=0,round=True,resolution='l')   
            #Proj4js.defs["EPSG:3408"] = "+proj=laea +lat_0=90 +lon_0=0 +x_0=0 +y_0=0 +a=6371228 +b=6371228 +units=m +no_defs";
            #
           ll_polar=True
	elif self.checkBox_3.isChecked() == True :
	   print "Projection antarctic"
           m = Basemap(projection='spstere',boundinglat=ymax,lon_0=180,round=True,resolution='l')   
           ll_polar=True
	else : 
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

        print xmin,xmax,ymin,ymax
        if epsg_val == '4326' :
            xmin = (180./np.pi)*xmin; xmax = (180./np.pi)*xmax
            ymin = (180./np.pi)*ymin; ymax = (180./np.pi)*ymax
            print "Cylindric projection"
            print xmin,xmax,ymin,ymax
        ##if self.projection in _cylproj:
        ##    Dateline =\
        ##       _geoslib.Point(self(180.,0.5*(self.llcrnrlat+self.urcrnrlat)))
        ##       hasDateline = Dateline.within(self._boundarypolyxy)
        ##    if hasDateline:
        ##             msg=dedent("""
        ##                        wmsimage cannot handle images that cross
        ##                        the dateline for cylindrical projections.""")
        ##    raise ValueError(msg)
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
       #     long_name="magnitude"
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
       ## except Exception, e:
       ##     print "error"
       ##     print "Execution failed: %s", e
       ##     if hasattr(e, 'reason'):
       ##         print "reason: %s", e.reason
       ##     if hasattr(e, 'code'):
       ##         print ' . code  %s: ', e.code
       ##     if hasattr(e, 'read'):
       ##         print ' . detail:\n%s', e.read()

    def retranslateUi(self):
        print "add text"
        self.setWindowTitle("Cmems selector")
        self.label.setText("Choose Area ")
        self.label_2.setText("Choose Product ")
        self.label_3.setText("Choose Dataset")
        self.label_4.setText("Choose Variable")
        self.label_5.setText("Defined area")
        self.label_6.setText("Lon min")
        self.label_7.setText("Lon max")
        self.label_8.setText("Lat min")
        self.label_9.setText("Lat max")
        self.label_10.setText("Time")
        self.label_11.setText("Depth")
        self.label_12.setText("Colorbar")
        self.label_13.setText("MinValue")
        self.label_14.setText("MaxValue")
        self.label_15.setText("Nb Colors")
        self.label_16.setText("Xpixels")
        self.label_17.setText("Input proj")
        self.label_18.setText("Xparallels")
        self.label_19.setText("Ymeridians")
        self.label_20.setText("Dpi")
        self.checkBox.setText("Add_vectors")
        self.checkBox.setEnabled(False)
        self.checkBox_2.setText("Arc_proj")
        self.checkBox_3.setText("Ant_proj")
        print "add text ok"
        list_area=['ARCTIC','BAL','GLOBAL','IBI','MED','NWS']
        for area in list_area : 
            self.comboBox.addItem(str(area))
        self.comboBox.setEnabled(True)
        self.comboBox_2.setEnabled(False)
        self.comboBox_3.setEnabled(False)
        print "enable OK"

    def changesrs(self) :
        input_srs=str(self.comboBox_9.currentText())
        if input_srs == "EPSG:3408" : 
            self.checkBox_2.setChecked(True)
            self.checkBox_3.setChecked(False)
        elif input_srs == "EPSG:3409" :
            self.checkBox_2.setChecked(False)
            self.checkBox_3.setChecked(True)

    def openproducts(self):
        """Populate combobox with products """
        print "Open products"
        self.comboBox_2.setEnabled(True)
        frame=self.comboBox.currentText()
        self.comboBox_3.clear()
        self.comboBox_2.clear()
        self.comboBox_4.clear()
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
                    self.comboBox_2.addItem(str(key))
            elif str(frame) == "NWS":
                frame1="NORTHWESTSHELF_"
                frame2="NWS"
                if frame1 in key or frame2 in key :
                    self.comboBox_2.addItem(str(key))
            elif str(frame) == "GLOBAL":
                if str(frame) in key :
                    if ind ==  0 :
                        self.comboBox_2.addItem(list_glo[5])
                    elif ind ==  5 : 
                        self.comboBox_2.addItem(list_glo[0])
                    else : 
                        self.comboBox_2.addItem(list_glo[ind])
                    ind+=1
            else :
                if str(frame) in key :
                    self.comboBox_2.addItem(str(key))
        self.comboBox_3.setEnabled(True)

    def opendatasets(self): 
        """Populate combobox with datasets """
        print "Open datasets"
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.comboBox_7.clear()
        self.comboBox_8.clear()
        self.comboBox_9.clear()
        product=str(self.comboBox_2.currentText())
        for key in self.dict_prod[product].keys():
            print "Variable"
            self.comboBox_3.addItem(str(key))
        self.comboBox_4.setEnabled(True)

    def openvariables(self): 
        """Populate combobox with variables """
        print "Open Variable"
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.comboBox_8.clear()
        self.comboBox_9.clear()
        # 0 list_variables
        # 1 list_time
        # 2 list_server
        # 3 list_DGF
        # 4 list_MFTP
        # 5 list_WMS
        # 6 list_depth
        # 7 list_resol
        # print "Open variables"
        product=str(self.comboBox_2.currentText())
        dataset=str(self.comboBox_3.currentText())
        self.comboBox_4.clear()
        url_base=self.dict_prod[product][dataset][5]
        print 'url'
        print url_base
        self.dict_var=self.getXML(url_base)
        print 'Get XML'
        for key in self.dict_var.keys():
            if not str(key).startswith('Automatically'):
                self.comboBox_4.addItem(str(key))
        ## Add current in the list if u, v exist

        variable=str(self.comboBox_4.currentText()) 
        list_area=self.dict_var[str(variable)][2]
        print list_area[0],list_area[1],list_area[2],list_area[3]
        self.lineEdit.setText(list_area[0]) 
        self.lineEdit_2.setText(list_area[1])
        self.lineEdit_3.setText(list_area[2])
        self.lineEdit_4.setText(list_area[3])
        self.comboBox_5.setEnabled(True)
        self.comboBox_6.setEnabled(True)
        self.comboBox_8.setEnabled(True)
        self.comboBox_9.setEnabled(True)
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
            self.comboBox_8.addItem(str(colorbar.split('/')[1]))
        self.lineEdit_5.setText('-50')
        self.lineEdit_6.setText('50')
        self.lineEdit_7.setText('20')
        self.lineEdit_8.setText('800')
        self.lineEdit_9.setText('20')
        self.lineEdit_10.setText('20')
        self.lineEdit_11.setText('300')
        formats=self.wms.getOperationByName('GetMap').formatOptions
        ind=0
        for proj in projections :
            if str(proj) == "EPSG:4326" or str(proj) == "EPSG:3408" or str(proj) == "EPSG:3409" : 
               self.comboBox_9.addItem(str(proj))
            #self.comboBox_9.model().item(ind).setEnabled(False)
            #ind+=1


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
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.comboBox_7.clear()
        # Current combobox values
        product=str(self.comboBox_2.currentText())
        dataset=str(self.comboBox_3.currentText())
        variable=str(self.comboBox_4.currentText())
        resol=self.dict_prod[product][dataset][7][0]
        list_time=self.dict_var[str(variable)][1]
        if "daily" in str(resol) :
            print "Daily variable"
            for value in list_time:
                day=str(value).split()[0][:-13]
                hour=str(value).split()[0][11:]
                self.comboBox_5.addItem(str(day))
            self.comboBox_6.addItem(str(hour))  
        self.comboBox_6.setEnabled(True)
        if "hourly" in str(resol) :
            print "Hourly variable"
            i=0
            day_tmp=''
            for value in list_time :
                day=str(value).split()[0][:-13]
                if day_tmp != day :
                    self.comboBox_5.addItem(str(day))
                    i=i+1
                day_tmp=day
                if i == 1:
                    hour=str(value).split()[0][11:]
                    self.comboBox_6.addItem(str(hour))
        list_prof=self.dict_var[variable][0]
        for value in list_prof : 
            prof=str(value).split()[0]
            self.comboBox_7.addItem(str(prof))
        if variable == "sea_water_velocity" :
           self.checkBox.setEnabled(True)

    def load_options(self,default_values):
        class cmemsval(dict):
            pass
        values=cmemsval()
        for k,v in default_values.items():
            print k,v
            setattr(values, k, v)
        return values

class SectionParams(QDialog):

    """ Dialog for params Section selection """

    def __init__(self): 
        QDialog.__init__(self)
        self.setWindowTitle("Params for section") 
        layout = QFormLayout(self)
        self.minlon_clabelgrid = QLabel("Lon min", self)
        self.minlon_fieldgrid = QLineEdit(self)
        self.maxlon_clabelgrid = QLabel("Lon max", self)
        self.maxlon_fieldgrid = QLineEdit(self)
        self.minlat_clabelgrid = QLabel("Lat min", self)
        self.minlat_fieldgrid = QLineEdit(self)
        self.maxlat_clabelgrid = QLabel("Lat max", self)
        self.maxlat_fieldgrid = QLineEdit(self)
        self.cmin_clabelgrid = QLabel("Contour min", self)
        self.cmin_fieldgrid = QLineEdit(self)
        self.cmax_clabelgrid = QLabel("Contour max", self)
        self.cmax_fieldgrid = QLineEdit(self)
        self.step_clabelgrid = QLabel("Step", self)
        self.step_fieldgrid = QLineEdit(self)
        self.profmin_clabelgrid = QLabel("Prof min", self)
        self.profmin_fieldgrid = QLineEdit(self)
        self.profmax_clabelgrid = QLabel("Prof max", self)
        self.profmax_fieldgrid = QLineEdit(self)
        self.namesection_clabelgrid = QLabel("Section name", self)
        self.namesection_fieldgrid = QLineEdit(self)
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.minlon_clabelgrid, self.minlon_fieldgrid)
        layout.addRow(self.maxlon_clabelgrid, self.maxlon_fieldgrid)
        layout.addRow(self.minlat_clabelgrid, self.minlat_fieldgrid)
        layout.addRow(self.maxlat_clabelgrid, self.maxlat_fieldgrid)
        layout.addRow(self.cmin_clabelgrid, self.cmin_fieldgrid)
        layout.addRow(self.cmax_clabelgrid, self.cmax_fieldgrid)
        layout.addRow(self.step_clabelgrid, self.step_fieldgrid)
        layout.addRow(self.profmin_clabelgrid, self.profmin_fieldgrid)
        layout.addRow(self.profmax_clabelgrid, self.profmax_fieldgrid)
        layout.addRow(self.namesection_clabelgrid, self.namesection_fieldgrid)
        layout.addRow(btn_layout)
        self.setLayout(layout)

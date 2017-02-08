# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#!/usr/bin/env python
## C.REGNIER : Test all CMEMS WMS adress and save in a cPickle and text file
import sys,os,io,glob
import xml.etree.ElementTree as ET
import os,urllib2
import cPickle
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.basemap import pyproj
from datetime import datetime
import numpy as np
import matplotlib
#matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.image import imread
import numpy as np 
import owslib
from pylab import *
import matplotlib.cm as cm
import matplotlib.image as mpimg
import pylab as pl
from tools import *
from thredds_crawler.crawl import Crawl

def getXMLthredds(url_base):
    """ Get XML from WMS adress """
    version="1.1.1"
    print "Adress %s " %(url_base[0])
    try :
        ## Read xml with urllib2
        url=url_base+'?service=WMS&version='+version+'&request=GetCapabilities'
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


try:
    from owslib.wms import WebMapService
except ImportError:
    raise ImportError('OWSLib required to use wmsimage method')
print "crawl"
## Get back the thredds catalog and split it
 ##c = Crawl('http://wms.hycom.org/thredds/catalog.xml', select=[".*-Agg"])
#print c.datasets
#sys.exit(1)

product_name='expt_32.5'
adress='http://wms.hycom.org/thredds/wms/GOMl0.04/'+product_name
#print c.datasets

dict=getXMLthredds(adress)
for var in dict.keys():
    print var
#print dict
wms = WebMapService(adress)
formats=wms.getOperationByName('GetMap').formatOptions
for form in formats :
    print form.split('/')[1]
print 'id: %s, version: %s' %\
(wms.identification.type,wms.identification.version)
print 'title: %s, abstract: %s' %\
(wms.identification.title,wms.identification.abstract)
print 'available layers:'
layer_list=list(wms.contents)
variable='temperature'
variable='ssh'
#print 'projection options:'
print wms[variable].crsOptions
crs_options=wms[variable].crsOptions
## see all options dir(wms['thetao'])
print "Styles"

print " See all attributs" 
print wms[variable].defaulttimeposition
xmin=-180
xmax=180
ymin=-90
ymax=90
xmin=-98.0
xmax=-76.4000244140625
ymin=18.09164810180664
ymax=31.960647583007812

xpixels=1000
aspect=0.5
ypixels = int(aspect*xpixels)
print ypixels
format="jpeg"
format="png"
plt.figure(figsize=(20,12))
long_name=wms[variable].title
print wms[variable].styles
for style in wms[variable].styles.keys():
    print style
#choose_style='boxfill/redblue'
choose_style='boxfill/redblue'
choose_style='boxfill/ncview'
choose_style='boxfill/rainbow'
if choose_style == 'boxfill/redblue' : 
    valuemap="bwr"
elif choose_style == 'boxfill/rainbow' :
    valuemap="jet"
elif choose_style == 'boxfill/jet' :
    valuemap="jet"
elif choose_style == 'boxfill/ncview' :
    valuemap="default"

colorbar=choose_style.split('/')[1]
#choose_style='boxfill/jet'
valmin='-2'
valmax='2'
numbercolor='100'
nb_values=int(numbercolor)
#mapper = cm.ScalarMappable(norm=norm, cmap=valuemap)
intervalDiff = ( float(valmax) - float(valmin) )/(nb_values-1)
print intervalDiff 
rastermin=int(valmin)
rastermax=int(valmax)
value=rastermin
norm = matplotlib.colors.Normalize(vmin=rastermin, vmax=rastermax, clip=True)
items=[]
item_ind=[]
for class_val in range(0, nb_values):
    val=float(class_val)/float(nb_values)
    items.append(float('%.2f'%(value)))
    item_ind.append(val)
    value=value+intervalDiff
print items
rangeval="'"+str(valmin)+','+str(valmax)+"'"
time_change="2016-01-20"
norm_func = mpl.colors.Normalize
norm = norm_func(vmin=rastermin, vmax=rastermax)
#cmap = cm.jet
#cmap = matplotlib.cm.get_cmap('Spectral')
#print wms.getOperationByName('GetMap').formatOptions
print [choose_style]
input_crs=crs_options[2]

epsg_val=input_crs.split(':')[1]
print epsg_val
m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
            urcrnrlon=xmax, llcrnrlat=ymin,resolution='i',epsg=4326)
p = pyproj.Proj(init="epsg:%s" % epsg_val, preserve_units=True)
xmin,ymin = p(m.llcrnrlon,m.llcrnrlat)
xmax,ymax = p(m.urcrnrlon,m.urcrnrlat)
if epsg_val == '4326' :
    xmin = (180./np.pi)*xmin; xmax = (180./np.pi)*xmax
    ymin = (180./np.pi)*ymin; ymax = (180./np.pi)*ymax
    print "Cylindric projection"
    print xmin,xmax,ymin,ymax

print xmin,ymin,xmax,ymax 
elevation='-5.0'
format='png'
img = wms.getmap(layers=[variable],service='wms',bbox=(xmin,ymin,xmax,ymax),
                 size=(xpixels,ypixels),
                 format='image/%s'%format,
                 elevation=elevation,
                 srs=input_crs,
                 time=time_change+'T00:00:00.000Z',
                 colorscalerange=valmin+','+valmax,numcolorbands=numbercolor,logscale=False,
                 styles=[choose_style])
print "OK"
colormap=choose_style.split('/')[1]
ylabel=wms[variable].abstract
long_name=wms[variable].title
title=product_name+" - "+long_name+" "+" - "+time_change
file_pal='./../palettes/thredds/'+colorbar+'.pal'
my_cmap=compute_cmap(file_pal,colorbar)
cm.register_cmap(name=colorbar, cmap=my_cmap)
font=10
xparallels=20
ymeridians=20
norm = mpl.colors.Normalize(vmin=float(valmin), vmax=float(valmax), clip=False) 
parallels=np.round(np.arange(ymin,ymax+xparallels/2,xparallels))
meridians = np.round(np.arange(xmin,xmax+ymeridians/2,ymeridians))
image=imread(io.BytesIO(img.read()))
m.drawcoastlines(color='lightgrey',linewidth=0.25)
m.fillcontinents(color='lightgrey')
m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,linewidth=0.2,dashes=[1, 5])
m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,linewidth=0.2)
## Plot the image
cs=m.imshow(image,origin='upper',alpha=1,cmap=(cm.get_cmap(colorbar,int(numbercolor))),norm=norm)
## Add colorbar
cb=plt.colorbar(cs,orientation='vertical',format='%4.2f',shrink=0.7)
cb.ax.set_ylabel(ylabel, fontsize=int(font)+4)
cl=plt.getp(cb.ax, 'ymajorticklabels')
plt.setp(cl, fontsize=font)
plt.title(title,fontsize=font+4,y=1.05)
plt.show()
plt.savefig(product_name+"_"+long_name+"_"+time_change+".png",dpi=300,bbox_inches='tight') 
#plt.imshow(image,cmap=(cm.get_cmap(colormap,int(numbercolor))))
#plt.colorbar()
sys.exit(1)


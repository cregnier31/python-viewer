# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#!/usr/bin/env python
## C.REGNIER : Test all CMEMS WMS adress and save in a cPickle and text file
import sys,os,io,glob
import xml.etree.ElementTree as ET
import os,urllib2
import cPickle
from mpl_toolkits.basemap import Basemap
import pyproj
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.image import imread
import numpy as np 
import owslib
from pylab import *
import matplotlib.cm as cm
import matplotlib.image as mpimg
import pylab as pl

def getWMS(url_base):
    serverurl=url_base[0]
    version="1.1.1"
    url=url_base[0]+'?service=WMS&version='+version+'&request=GetCapabilities'
    lon_min = -118.8; lon_max = -108.6
    lat_min = 22.15;  lat_max = 32.34
    m = Basemap(llcrnrlon=lon_min, urcrnrlat=lat_max,
                        urcrnrlon=lon_max, llcrnrlat=lat_min,resolution='i',epsg=4326)
    m.wmsimage(serverurl,xpixels=500,verbose=True,
               layers=['thetao'],
               elevation='-0.49402499198913574',
               colorscalerange='271.2,308',numcolorbands='20',logscale=False,
               styles=['boxfill/ferret'])
              # styles=['boxfill/rainbow'])
               #time=datetime.utcnow().strftime('%Y-%m-%dT12:00:00.000Z'),
    plt.figure()
    m.drawcoastlines(linewidth=0.25)
    parallels = np.arange(20,36,2.)
    a=m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
    meridians = np.arange(-120,-100,2.)
    b=m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)




def getXML_new(url_base):
    """ Get XML from WMS adress """
    version="1.1.1"
    print "Adress %s " %(url_base)
    try :
        ## Read xml with urllib2
        url=url_base+'?service=WMS&version='+version+'&request=GetCapabilities'
        print url
        request = urllib2.Request(url, headers={"Accept" : "application/xml"})
        u = urllib2.urlopen(request)
        u=urllib2.urlopen(url)
        value=u.read()
        tree= ET.fromstring( value )
        dict_var={}
        cap = tree.findall('Capability')[0]
        layer1 = cap.findall('Layer')[0]
        layer2 = layer1.findall('Layer')
        list_product=[]
        for l in layer2 :
            print l.find('Title').text
            prod=l.find('Title').text
            list_product.append(prod)
            if "Oceanography" in prod :
                print 'Oceano OK'
                layer3 = l.findall('Layer')[0]
                layer4=layer3.findall('Layer')
                for l2 in layer4: 
                    print l2.find('Name').text
                    print "--------"
                   ## layer4 = l2.findall('Layer')[0]
                   ## for l3 in layer4 :
                   ##    print "========================"
                   ##    print layer3
                   ##    print "========================"
                ##    prod2=l2.find('Name').text
                ##    print prod2
        print list_product
        sys.exit(1) 
##        layer1 = cap.findall('Layer')[0]
##        layer2 = layer1.findall('Layer')[0]
##        layer3 = layer2.findall('Layer')[0]
##        layer4 = layer3.findall('Layer')
##        for l in layer4 :
##           # title=l.find('Title').text
##            print l.find('Name').text
##
        sys.exit(1)
        ##layer2 = layer1.findall('Layer')
        ##for l in layer2 :
        ##    title=l.find('Title').text
        ##    print title

        ##for l in layer1 :
        ##    title=l.find('Title').text
        ##    title=l.find('SRS').text
        ##    print title
        ##    
        sys.exit(1)


        layer2 = layer1.findall('Layer')[0]
        for l in layer2 :
            print l.text
        sys.exit(1)
        layer3 = layer2.findall('Layer')[0]
        sys.exit(1)
        for layer in layer1 :
            print layer
           # title=layer.findall('Title').text
           # print title
            print '---------------------'
        sys.exit(1)
        layer2 = layer1.findall('Title')[0]
        
        print layer2.text
        for l in layer2 : 
            title=l.find('Title').text
            print title
        sys.exit(1)
        #layer2 = layer1.findall('Layer')[0]
        layers = layer2.findall('Layer')
        for l in layers:
            ## Find Variable name
            variable_name=l.findall('Name')
            for name in  variable_name :
                print name
            sys.exit(1)
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

def getXML(url_base):
    version="1.1.1"
    url=url_base+'?service=WMS&version='+version+'&request=GetCapabilities'
    print " URL  %s " %(url)
    try :
        u=urllib2.urlopen(url,timeout=60)
        value=u.read()
        tree= ET.fromstring( value )
        ll_request=True
    except:
        ll_request=False 
        print "Probleme with WMS request"

    return ll_request



def getXML2(url_base):
        ## Read xml with urllib2
        version="1.1.1"
        url=url_base+'?service=WMS&version='+version+'&request=GetCapabilities'
        request = urllib2.Request(url, headers={"Accept" : "application/xml"})
        u = urllib2.urlopen(request)
        u=urllib2.urlopen(url)
        print url
        value=u.read()
        tree= ET.fromstring( value )
        #print ET.dump(tree)
        dict_var={}
        cap = tree.findall('Capability')[0]
        layer1 = cap.findall('Layer')[0]
        layer2 = layer1.findall('Layer')[0]
        layers = layer2.findall('Layer')
        for l in layers:
            #variable_name=l.find('Title').text
            variable_name=l.find('Name').text
            Title=l.find('Title').text
            #print "Title %s " %(Title)
            variable_name=l.find('Abstract').text
            #print 'variable %s ' %(variable_name)
            box=l.find('BoundingBox')
            lonmin=box.attrib['minx']
            lonmax=box.attrib['maxx']
            latmin=box.attrib['miny']
            latmax=box.attrib['maxy']
                #if var_box.attrib == 'minx' :
                #   lonmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxx' :
                #   latmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'miny' :
                #   lonmax=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxy' :
                #   latmax=str(dim.text).split(',')
            #for child in box:
            #    print child
            print lonmin,lonmax,latmin,latmax
            #dimensions=l.findall('LatLonBoundingBox')
            #print dimensions[1].text
            #for dim in dimensions : 
            #    print dim.text
                #if dim.attrib['name'] == 'minx' :
                #   lonmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxx' :
                #   latmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'miny' :
                #   lonmax=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxy' :
                #   latmax=str(dim.text).split(',')
            #print lonmin,lonmax,latmin,latmax
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
            dict_var[str(variable_name)]=list_tot
            return dict_var

def read_file(f):
  '''Read ncview colormaps_<name>.h file'''

  l=open(f).readlines()

  i=-1
  for k in l:
    i+=1
    if k.startswith('static'): break

  l=l[i:]

  i0=l[0].find('{')
  i1=l[-1].find('}')

  l[0]=l[0][i0+1:]
  l[-1]=l[-1][:i1]

  r=[]
  for i in range(len(l)):
    line=l[i].replace(',',' ').strip()
    vals=[int(j) for j in line.split()]
    r=np.hstack((r,vals))

  r.shape=r.size/3,3
  return r/255.


def gen_cmap(file,name='auto',N=None):
  '''Read ncview colormaps_<name>.h file'''
  if name=='auto': name=file.split('colormaps_')[-1][:-2]
  r=read_file(file)
  return pl.matplotlib.colors.ListedColormap(r, name=name, N=N)

try:
    from owslib.wms import WebMapService
except ImportError:
    raise ImportError('OWSLib required to use wmsimage method')
##import urllib2, io
### find the x,y values at the corner points.
###p = pyproj.Proj(init="epsg:%s" % self.epsg, preserve_units=True)
### ypixels not given, find by scaling xpixels by the map aspect ratio.
##print adress
adress="http://geo.weather.gc.ca/geomet/"
dict=getXML_new(adress)
##print dict
sys.exit(1)
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
print layer_list
sys.exit(1)
#print 'projection options:'
print wms['thetao'].crsOptions
options=wms['thetao'].crsOptions
print options
## see all options dir(wms['thetao'])
print "Styles"

styles=wms['thetao'].styles
print styles
print dir(wms['thetao'])
print " See all attributs" 
print wms['thetao'].defaulttimeposition
xmin=-180
xmax=180
ymin=-90
ymax=90
#xmin=-20
#xmax=100
#ymin=-20
#ymax=40
xpixels=1000
aspect=0.5
projection="mercator"
#if projection == 'cyl':
#    aspect = (urcrnrlat-llcrnrlat)/(urcrnrlon-llcrnrlon)
#else:
#    aspect = (ymax-ymin)/(xmax-xmin)
#print aspect
ypixels = int(aspect*xpixels)
print ypixels
format="jpeg"
format="png"
#plt.figure(figsize=(19.2,11.5))
plt.figure(figsize=(20,12))
variable='thetao'
long_name=wms[variable].title
print options[2]
#choose_style='boxfill/redblue'
choose_style='boxfill/redblue'
choose_style='boxfill/ncview'
if choose_style == 'boxfill/redblue' : 
    valuemap="bwr"
elif choose_style == 'boxfill/rainbow' :
    valuemap="jet"
elif choose_style == 'boxfill/jet' :
    valuemap="jet"
elif choose_style == 'boxfill/ncview' :
    valuemap="default"

#choose_style='boxfill/jet'
choose_legend=styles[choose_style]['legend']
print choose_legend
valmin='-5'
valmax='35'
numbercolor='20'
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
time_change="2017-01-20"
norm_func = mpl.colors.Normalize
norm = norm_func(vmin=rastermin, vmax=rastermax)
#cmap = cm.jet
#cmap = matplotlib.cm.get_cmap('Spectral')
#print wms.getOperationByName('GetMap').formatOptions
print [choose_style]
print options[2]
m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
                                  urcrnrlon=xmax, llcrnrlat=ymin,resolution='i',epsg=4326)
print m.aspect
sys.exit(1)
img = wms.getmap(layers=[variable],service='wms',bbox=(xmin,ymin,xmax,ymax),
                 size=(xpixels,ypixels),
                 format='image/%s'%format,
                 elevation='-0.49402499198913574',
                 srs=options[2],
                 time=time_change+'T12:00:00.000Z',
                 colorscalerange=valmin+','+valmax,numcolorbands=numbercolor,logscale=False,
                 styles=[choose_style],legend=choose_legend)
                 #colorscalerange='-5,35',numcolorbands='100',logscale=False,
colormap=choose_style.split('/')[1]
files=glob.glob('./statics/colormaps_'+valuemap+'.h')
files.sort()
cmap=gen_cmap(files[0])
cm.register_cmap(name='ncview', cmap=cmap)
#,N=int(numbercolor))

image=imread(io.BytesIO(img.read()))
lt.imshow(image,cmap=(cm.get_cmap('ncview',int(numbercolor))))
lt.colorbar()
lt.savefig(product+"_"+long_name+"_"+time_change+"_new3.png",dpi=300,bbox_inches='tight')
ys.exit(1)
# print image
parallels=20
meridians=20
ont=16
label=wms[variable].abstract
title=product+" - "+long_name+" "+" - "+time_change
m.drawcoastlines(color='lightgrey',linewidth=0.25)
m.fillcontinents(color='lightgrey')
m.imshow(image,origin='upper',alpha=1,cmap=cmap,norm=norm)
lt.colorbar()
lt.show()
ys.exit(1)
cs=m.imshow(image,origin='upper',alpha=1,cmap=(cm.get_cmap(valuemap,int(numbercolor))),norm=norm)
m.imshow(image,origin='upper',alpha=1)
cb=plt.colorbar(cs,orientation='vertical',format='%4.2f',pad=0.1,shrink=0.7)
cb=plt.colorbar(cs,orientation='vertical',format='%4.2f',shrink=0.7)
vb.ax.set_ylabel(ylabel, fontsize=int(font)+4)
cl=plt.getp(cb.ax, 'ymajorticklabels')
plt.setp(cl, fontsize=font)
plt.colorbar()
plt.title(title,fontsize=font,y=1.05)
parallels=np.round(np.arange(ymin,ymax+xparallels/2,xparallels))
m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,linewidth=0.2)
meridians = np.round(np.arange(xmin,xmax+ymeridians/2,ymeridians))
m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,linewidth=0.2,dashes=[1, 5])
plt.savefig(product+"_"+long_name+"_"+time_change+"_new3.png",dpi=300,bbox_inches='tight')
plt.show()

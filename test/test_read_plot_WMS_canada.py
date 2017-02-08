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
        list_layer=[]
	list_style=[]
        for l in layer2 :
            print l.find('Title').text
            prod=l.find('Title').text
            list_product.append(prod)
            if "Oceanography" in prod :
                print 'Oceano OK'
                layer3 = l.findall('Layer')[0]
                layer4=layer3.findall('Layer')
		for l2 in layer4 :
		   print l2.find('Name').text
                   layer_name=l2.find('Name').text
                   list_layer.append(layer_name)
                   layer5=l2.findall('Style')
                   for l3 in layer5:
                       style_name=l3.find('Name').text
                       print l3.find('Name').text
                       print l3.find('Title').text
                       list_style.append(style_name)
                       print "--------"
    except:
        raise
        print "Error in WMS procedure"
        sys.exit(1)
    return list_layer,list_style

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
            print lonmin,lonmax,latmin,latmax
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
adress="http://geo.weather.gc.ca/geomet/"
layer,style=getXML_new(adress)
print layer,style
wms = WebMapService(adress)
formats=wms.getOperationByName('GetMap').formatOptions
product='GIOPS'
#for form in formats :
#    print form.split('/')[1]
#print 'id: %s, version: %s' %\
#(wms.identification.type,wms.identification.version)
#print 'title: %s, abstract: %s' %\
#(wms.identification.title,wms.identification.abstract)
#print 'available layers:'
#layer_list=list(wms.contents)
xmin=-180
xmax=180
ymin=-90
ymax=90
xpixels=1000
aspect=0.5
projection="mercator"
ypixels = int(aspect*xpixels)
print ypixels
format="png"
plt.figure(figsize=(20,12))
ind_var=4
variable=layer[ind_var]
choose_style=style[ind_var]
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
proj="EPSG:4326"
norm = matplotlib.colors.Normalize(vmin=rastermin, vmax=rastermax, clip=True)
rangeval="'"+str(valmin)+','+str(valmax)+"'"
time_change="2017-02-18"
norm_func = mpl.colors.Normalize
norm = norm_func(vmin=rastermin, vmax=rastermax)
img = wms.getmap(layers=[variable],service='wms',bbox=(xmin,ymin,xmax,ymax),
                 size=(xpixels,ypixels),
                 format='image/%s'%format,
                 #elevation='-0.49402499198913574',
                 srs=proj,
                 time=time_change+'T12:00:00.000Z',
                 colorscalerange=valmin+','+valmax,numcolorbands=numbercolor,logscale=False,
                 styles=[choose_style])

image=imread(io.BytesIO(img.read()))
plt.imshow(image) #,cmap=(cm.get_cmap('ncview',int(numbercolor))))
plt.colorbar()
plt.show()
plt.savefig(product+"_"+variable+"_"+time_change+".png",dpi=300,bbox_inches='tight')
sys.exit(1)
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

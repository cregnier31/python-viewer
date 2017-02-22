## Module to parse xml documents
import sys,os,urllib2
import xml.etree.ElementTree as ET

def ParseXML(url_base):

    """ Get XML from WMS adress and Parse it """

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

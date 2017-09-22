#!/bin/sh
#unset module 
#PYTHONPATH=""
export PYTHONPATH=$PYTHONPATH:/home/cregnier/python/module/motu-client-python
#export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/qgis/qgis-2.8.1_gnu4.8.2/share/qgis/python/plugins/"
#export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/qgis/qgis-2.8.1_gnu4.8.2/share/qgis/python"
#export PATH="/homelocal/sauvegarde/cregnier/Program_files/miniconda2/bin:$PATH"
#export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/matplotlib/matplotlib-1.4.3_gnu4.8.2/lib64/python2.7/site-packages/"
#export LD_LIBRARY_path="/home/modules/versions/64/centos7/qgis/qgis-2.8.1_gnu4.8.2/lib"
echo $PYTHONPATH
python Thredds_explorer.py


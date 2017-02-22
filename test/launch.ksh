#!/bin/sh
unset module 
PYTHONPATH=""
export PYTHONPATH=$PYTHONPATH:/home/cregnier/python/module/motu-client-python
export PATH="/homelocal/sauvegarde/cregnier/Program_files/miniconda2/bin:$PATH"

python test_ihm.py

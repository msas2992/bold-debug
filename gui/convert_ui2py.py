'''
Created on 3 sep. 2015

@author: e.schaeffer
'''


import os
from datetime import datetime

try:
    from PyQt4 import uic  # @UnresolvedImport
    qt_prefix = 'qt4_'
except:
    from PyQt5 import uic  # @UnresolvedImport
    qt_prefix = 'qt5_'

uifiles = [
    {'ui': 'mainwindow_v2',    'out': None,  'force': False,  'skip': False},
    {'ui': 'mainwindow_v2b',   'out': None,  'force': False,  'skip': False},
    {'ui': 'widget_lamp',      'out': None,  'force': False,  'skip': False},    
    {'ui': 'testmode_dialog',      'out': None,  'force': False,  'skip': False},    
]

silent = True
uidir = 'ui'

curpath = os.path.dirname(os.path.abspath(__file__))
dest_path = curpath
source_path = os.path.abspath(os.path.join(curpath, uidir))


for uifile in uifiles:
    infile = os.path.join(uidir, uifile['ui']+'.ui')

    if uifile['skip'] == True:
        if silent == False:
            print('{:s} - skipping'.format(infile))
        continue

    if uifile['out'] is None:
        outfile = os.path.join('.', qt_prefix + uifile['ui'] + '.py')
    else:
        outfile = os.path.join('.', uifile['out'] + '.py')

    if os.path.isfile(infile):
        in_mtime = os.path.getmtime(infile)
    else:
        if silent == False:
            print('{:s} does not exist'.format(infile))
        continue

    convert = False
    if os.path.isfile(outfile):
        out_mtime = os.path.getmtime(outfile)

        if in_mtime > out_mtime:
            # ui file is newer than py file, convert
            convert = True
    else:
        # ui file does not exist, convert
        convert = True

    if uifile['force'] == True:
        convert = True

    if convert == True:
        print('{:s} - converting to {:s}'.format(infile, outfile))
        pyfile = open(outfile, 'w')
        uic.compileUi(infile, pyfile)
    else:
        if silent == False:
            print('{:s} - no action'.format(infile))

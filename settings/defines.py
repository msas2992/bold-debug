'''
Created on 20 mei 2015

@author: e.schaeffer
updates
12-04-2018 ES, 2.0 Python3.6/PyQt5
14-09-2015 PdV 1.30 Implement delay for measuring initial lamp power
05-08-2015 PdV 1.29 Hyperion / Brontes selector in settings file
31-07-2015 PdV 1.28 Hyperion implemented
29-07-2015 PdV increment version for USBRelay close fix
23-07-2015 PdV increment version for Audio message fix
'''

Version = '20231207-deviate'
title = "Bold SecureLock " + Version

ExecutableName = 'boldfct'
ExecutableDescription = 'Bold SecureLock Tester'


STATUS_GREEN = 1
STATUS_RED = 2
STATUS_CLEAR = 0

# I/O connected to 34907A board, tuple(board,channel,pin)
Ry_Takeover     = (200,1,0)
Ry_10kResistor  = (200,1,1)
Ry_Jlink        = (200,1,4)
Ry_Stamp        = (200,1,7)
Ry_SerialEnable = (200,2,0)
Ry_Button       = (200,1,3)

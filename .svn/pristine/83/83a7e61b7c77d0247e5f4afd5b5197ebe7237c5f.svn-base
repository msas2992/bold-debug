'''
Created on 21 mei 2015

@author: e.schaeffer
'''

from serial import Serial
import time

class SerialInterface(Serial):
    time_out = None

    def __init__(self, *args, **kwargs):
        self.time_out = kwargs.get('timeout', 0.1)
        if self.time_out < 0.01:
            self.time_out = 0.01

        kwargs['timeout'] = self.time_out

        Serial.__init__(self, *args, **kwargs)

        
    def write(self, data):
#         print('writing', data, type(data))

        if isinstance(data, str):
            super(SerialInterface, self).write(data.encode())
        else:
            super(SerialInterface, self).write(data)

    # *************************************************************************************
    # standard PySerial is hunting for \n, we have \r
    # not easy to change, this is the reason for the below
    # method, everywhere we use readline() we now use _readline()
    # timeout is parameter for the max time we will wait.
    # *************************************************************************************
    def _readline(self, timeout = None, eol = b'\r'):
        time.sleep(.05)
        if timeout != None :
            orginal_timeout = self.timeout
            self.timeout = timeout
        leneol = len(eol)       # get length of eol char (1...)
        line = bytes()
        
        while True:            
            b = self.read(1)        # get 1 char from serial OR timeout
            if b != b'' :            # if char return and not empty string (bytearray)
                try:
                    c = b.decode()
                except:
                    continue
                line += b           # store in array
                if line[-leneol:] == eol:   # if last char was eol
                    break           # exit loop
            else:                   # no char received
                break

        if timeout != None :
            self.timeout = orginal_timeout

        return line.decode()

    _read_until = _readline

    def _readlines(self, timeout = None, eol = b'\r', findstr = None):
        lines = ''
        while True:
            line = self._readline(timeout=timeout)
#             print('line', len(line), line)

            if len(line) > 0:
                lines += line
            else:
                return lines

            if findstr is not None:
                if findstr in lines:
                    return lines
        return lines




if __name__ == '__main__':
    ser = SerialInterface('COM31',
                          timeout=0.05,
                          baudrate=115200)
    
    # ser.write('[FT,ToolReset]\r\n')
    # lines = ser._readlines(timeout=1, findstr='FT,Ready')
    # print(lines)

    ser.send_break(0.5)
    ser.write('VER'.encode())
    lines = ser._readlines(timeout=1)
    print(lines)

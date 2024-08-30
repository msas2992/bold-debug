import ftd2xx

class FTDINode:
    """Class to communicate with a tremornet node """
    BITMODE_RESET = 0
    BITMODE_SYNCFF = 0x40
    # VID = 0x403
    # PID = 0x6001
    def __init__(self, idx):
        """Create an instance of the Node class with the given index and
        initialize the FTDI
        """
        self.idx = idx
        self.handle = ftd2xx.open(idx)

        self.handle.setBitMode(0xff, self.BITMODE_RESET)
        self.handle.setBitMode(0xff, self.BITMODE_SYNCFF)
        self.handle.setLatencyTimer(1)

    @staticmethod
    def getFirst(vid, pid):
        # Return the first discovered Tremornet Node
        nb_device = ftd2xx.createDeviceInfoList()
        # print('num devices:', nb_device)

        for a in range(0, nb_device):
            details = ftd2xx.getDeviceInfoDetail(a, False)
            # print(details)
            _vid = details['id'] >> 16
            _pid = details['id'] - (vid << 16)
            # print('vid/pid: {:04X} {:04X}'.format(_vid, _pid))
            if _vid == vid and _pid == pid:
                return FTDINode(a)

    def write(self, data):
        # Send data to the device. Data must be a string representing the bytes
        # to be sent. Returns the number of byte written
        return self.handle.write(data)

    def read(self, nchar):
        # Read up to nchars bytes form the device. Use avaiblable to find how much
        # bytes are available
        return self.handle.read(nchar)

    def close(self):
        self.handle.close()

    def available(self):
        # Returns the number of available bytes
        return self.handle.getQueueStatus()



if __name__ == '__main__':

    n = FTDINode.getFirst(0x0403, 0x6014)
    res = n.write('VER\r\n'.encode('UTF-8'))
    print(f'res = {res}')
    while True:
        nb = n.available()
        if nb > 0 :
            res = n.read(nb)
            print(res)
            if(res.find('\r\n'.encode('UTF-8')) != -1):
                break




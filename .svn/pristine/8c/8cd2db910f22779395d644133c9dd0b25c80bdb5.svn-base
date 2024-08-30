import subprocess
import multiprocessing
import os, sys, time
from pprint import pprint

path = 'C:\\Users\\Peter\\eclipse-workspace\\PNE16-Innoseis\\files\\nodesn'
exe = 'nodeSNPNE.exe'

nodesn = os.path.join(path, exe)

try:
    ret = subprocess.check_output([nodesn, '-ln'], shell=True, stderr=subprocess.STDOUT)
except Exception as e:
    ret = str(e.output)

# print(ret)
# print(type(ret))

# pprint(ret)

# rr = ret.split('\\r\\n')
# devices = {}
# device = None
# for r in rr:
#     if r.startswith('\\t'):
#         if device is None:
#             continue

#         if 'ID=' in r:
#             devices[device]['ID'] = r.split('=')[1]
#         if 'LocId=' in r:
#             devices[device]['LocId'] = r.split('=')[1]
#         if 'SerialNumber=' in r:
#             devices[device]['SerialNumber'] = r.split('=')[1]
#         if 'Description=' in r:
#             devices[device]['Description'] = r.split('=')[1]

#     if 'Dev ' in r:
#         nr = r.split(' ')[1]
#         if ':' not in nr:
#             continue
#         nr = nr.replace(':', '')
#         device = int(nr)
#         devices[device] = {}



# pprint(devices)

# tndev = None
# for i,d in devices.items():
#     if d['Description'] == 'Tremornet':
#         tndev = d
#         break

# if tndev is None:
#     print('no tremornet device found')
#     sys.exit()

def doeiets():
    cmd = ['c:\\Users\\Peter\\eclipse-workspace\\PNE16-Innoseis\\files\\nodesn\\nodeSNPNE.exe', '-l', '12660', '-w', '-m', 'T08A01V111912H0002']
    try:
        # ret = subprocess.check_output([nodesn, '-l', '12660', '-w', '-m', 'T08A01V111912H0002'])
        ret = subprocess.check_output(cmd, shell=True)
    except Exception as e:
        print(e.output)

def doeiets2():
    locid = 12660
    try:
        ret = subprocess.check_output([nodesn, '-l', '12660', '-r'], shell=True)
    except Exception as e:
        print('x')
        ret = str(e.output)

    print(ret)
    if 'SUCCESS' in ret:
        print('OK')

if __name__ == '__main__':
    p = multiprocessing.Process(target=doeiets)
    p.start()

    time.sleep(5)
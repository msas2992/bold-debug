'''
Created on Apr 20, 2018

@author: PhilipsRefurb Tester
'''
from settings.settings import CascadedSettings

MSGOPTIONS = ['modelid', 'firmwareversion', 'hardwareversion']

class SettingsTestSequence(CascadedSettings):
    def __init__(self, inifile=''):
        self.inifile = inifile

    # read settings from settings.ini file
    def get_settings(self):
        self.readSettings()

        self.general = {}
        self.barcode = {}

        try:
            self.general['enabled'] = self.getboolean('general', 'enabled')
            self.general['name'] = self.get('general', 'name')
            self.general['image'] = self.get('general', 'image')
            self.general['fileversion'] = self.get('general', 'fileversion')
            self.general['description'] = self.get('general', 'description')

            self.barcode['D'] = self.get('barcode', 'd')
            self.barcode['A'] = self.get('barcode', 'a')

            num = 1
            self.messages = []
            while True:
                msgsection = 'message{:d}'.format(num)
                msg= {}
                if self.has_section(msgsection):
                    optfound = False
                    for opt in MSGOPTIONS:
                        if self.has_option(msgsection, opt):
                            msg[opt] = self.get(msgsection, opt)
                            optfound = True
                        else:
                            msg[opt] = None
                    if optfound == False:
                        return (False, 'message section {:s} incomplete'.format(msgsection))
                    msg['message'] = self.get(msgsection, 'message')
                    self.messages.append(msg)
                    num += 1
                else:
                    break

            self.swblacklist = []
            num = 1
            while True:
                if self.has_section('software'):
                    opt = 'blacklist[{:d}]'.format(num)
                    if self.has_option('software', opt):
                        b = self.get('software', opt)
                        self.swblacklist.append(b)
                        num += 1
                    else:
                        break
                else:
                    break

            self.macprefix = self.get('mac', 'prefix')

        except Exception as e:      # all errors, capture exception in e
            print(e)
            return (False, str(e))  # return exception type 'e'

        return (True, None)

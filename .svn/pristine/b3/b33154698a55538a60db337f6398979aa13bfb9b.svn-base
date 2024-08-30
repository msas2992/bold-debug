'''
Created on 20 mei 2015

@author: e.schaeffer
'''


import configparser
from pprint import pprint
import os


class CascadedSettings():
    def __init__(self, inifile=''):
        self.inifile = inifile
        self.inifiles_read = []

    def setInifile(self, inifile):
        self.inifile = inifile

    def readSettings(self):
        self.params = {}
        self._readSettings(os.path.join('files', self.inifile))

        if 'include' in self.params:
            while True:
                if len(self.params['include']) == 0:
                    break
                filename = self.params['include'].pop()
                self._readSettings(os.path.join('files', filename))
#         pprint(self.params)

    def _readSettings(self, filename):
        # reads settings from inifile, and reads settings from included inifiles as well
        # first setting read is leading
#         print
#         print(filename)
        if os.path.isfile(filename) == False:
            print('filename doesnt exist')
            return False
        else:
            #print('file exists')
            pass

        inihandle = configparser.RawConfigParser()
        inihandle.read(filename)
        try:
            self.inifiles_read.append(filename)
        except:
            self.inifiles_read = [filename]
        sections = inihandle.sections()
#         print(sections)

        for section in sections:
            if section not in self.params:
                if section == 'include':
                    self.params[section] = []
                else:
                    self.params[section] = {}
            options = inihandle.options(section)
            for opt in options:
                if section == 'include':
                    self.params[section].append(inihandle.get(section, opt))
                else:
                    if opt not in self.params[section]:
                        #only add the option if it doesnt already exist
                        self.params[section][opt] = inihandle.get(section, opt)

        return True

    def has_section(self, section):
        if section in self.params:
            return True
        return False

    def has_option(self, section, option):
        if section in self.params:
            if option in self.params[section]:
                return True
        return False
    
    def keys(self, section):
        if section in self.params:
            return list(self.params[section].keys())
                        
        return None

    def get(self, section, option):
        if section in self.params:
            if option in self.params[section]:
                return self.params[section][option]

        raise KeyError('Parameter {:s}.{:s} not found'.format(section, option))

        return None

    def getint(self, section, option):
        sval = self.get(section, option)
        try:
            val = int(sval)
        except:
            raise ValueError('Parameter {:s}.{:s} ({:s}) is not an integer'.format(section, option, sval))
            return None

        return val

    def getfloat(self, section, option):
        sval = self.get(section, option)
        try:
            val = float(sval)
        except:
            raise ValueError('Parameter {:s}.{:s} ({:s}) is not a float'.format(section, option, sval))
            return None

        return val

    def getboolean(self, section, option):
        sval = self.get(section, option)

        if sval.lower() in ['true', 'on', '1', 'yes']:
            val = True
        elif sval.lower() in ['false', 'off', '0', 'no']:
            val = False
        else:
            raise ValueError('Parameter {:s}.{:s} ({:s}) is not a boolean'.format(section, option, sval))
            return None

        return val


class Settings(CascadedSettings):
    inihandle = None

    def __init__(self, inifile=''):
        self.inifile = inifile

    # read settings from settings.ini file
    def get_settings(self):
        self.readSettings()

        try:
            self.module = self.params['general']['module']
            self.logdir = self.params['general']['logdir']

            self.keys = {}
            self.keys['start'] = self.params['keys']['start']
            self.keys['stop'] = self.params['keys']['stop']
        except Exception as e:      # all errors, capture exception in e
            return (False, str(e))  # return exception type 'e'

        return (True, None)



if __name__ == '__main__':
#     cs = CascadedSettings('..\\settings.ini')
    cs = CascadedSettings('..\\9290002579_color.ini')
    cs.readSettings()

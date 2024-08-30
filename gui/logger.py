'''
Created on 31 okt. 2014

@author: e.schaeffer

updates
11-11-2014    PdV change logfile name MAC_BC_TIME.LOG

'''


from datetime import datetime
import os

# *************************************************************************************
# interface to QT log window printer
# *************************************************************************************
class Logger() :
    logdata = ''
    filename_prefix = []

    # clear the logdata variable
    def log_clear(self):
        self.logdata = ''


    # functional test is using Print_Log to write to GUI,
    # all messages are saved in self.logdata
    # end of test this self.logdata is written to file (pass / fail)
    # when running commandline text out the emit and use print txt, instead
    def log_add(self, txt=''):
        # print('log', txt)
        try:
            self.textupdate.emit('log', txt)
        except:
            print (txt,)

        self.logdata += txt
        return len(txt)


    # build the filename C = Color, B = board, BC = both tests
    # filename is MAC + above letter + HHMMSS
    # activated from main when test success or fail
    def log_save(self, success):
        if self.hwsettings.general['log_text'] == False:
            return

        filename = '_'.join(self.filename_prefix)

        filename += '_' + datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
        filename += '.log'

        if success == True:
            path = os.path.join(self.hwsettings.general['logdir'], 'PASS', filename)
        else:
            path = os.path.join(self.hwsettings.general['logdir'], 'FAIL', filename)

        # with as => always close file whatever happens (fail / success)
        with open(path, 'w') as fd:
            fd.write(self.logdata)


    def logAddFilenamePrefix(self, prefix):
        self.filename_prefix.append(str(prefix))


    def logClearFilenamePrefix(self):
        self.filename_prefix = []


    # method to check at start of application if log folders exists
    # return True when OK
    def Check_Log_Folder_Exist(self):
        self.path_pass = os.path.join(self.hwsettings.general['logdir'], 'PASS')
        self.path_fail = os.path.join(self.hwsettings.general['logdir'], 'FAIL')

        self.log_add('log PASS folder = {:s}\n'.format(self.path_pass))
        self.log_add('log FAIL folder = {:s}\n'.format(self.path_fail))

        if not os.path.exists(self.path_pass):
            return False
        if not os.path.exists(self.path_fail):
            return False
        return True



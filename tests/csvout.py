'''
Created on Apr 26, 2018

@author: PhilipsRefurb Tester
'''



class TestData():
    def __init__(self):
        self.values = []
    
    def set10NC(self, s10NC):
        self.s10NC = s10NC

    def setMacAddress(self, mac):
        self.mac = mac
        
    def setPassFail(self, passfail, error=''):
        self.passfail = passfail
        self.error = error
        
    def addTestValue(self, value):
        if isinstance(value, list):
            self.values += value
        elif isinstance(value, dict):
            pass
        else:
            self.values.append(value)
        
    
    def output(self):
        output = [self.s10NC,
                  self.mac,
                  self.passfail,
                  self.error]
        output += self.values
        
        s = map(str, output)
        
        print(';'.join(s))
        
        
        
if __name__ == '__main__':
    
    TT = TestData()
    
    TT.set10NC('92900002761')
    TT.setMacAddress('11:22:33:44:55:66')
    
    TT.addTestValue(5.0)    
    TT.addTestValue([1.0, 3.3, 99])
    TT.setPassFail('FAIL', 'error in power')    
#     TT.addTestValue([44,55,66])    
#     TT.addTestValue(0.0098)
#     TT.addTestValue('trttrt')
        
    
#     TT.setPassFail('PASS', '')
    
    TT.output()
    
    
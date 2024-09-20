'''
Author:     Alex Zaleski

'''

import pandas as pd
import matplotlib.pyplot as plt
from ArduPilot_binParser import ArduPilotLog

class error:
    def __init__ (self, errorMsg):
        self.msg = errorMsg
        self.expected=''
        self.actual=''
        

def Test_Filter_Method(fileName):
    errors = []
    log = ArduPilotLog(fileName)
    log.parse(verbose=False)
 #Test invalid parameter type name
    param_GPS = log.filter("BadParameter")
    expResponce = True
    if param_GPS.empty != expResponce: 
        err=error("Bad filter parameter should have returned empty DataFrame")
        err.expected=expResponce
        err.actual=param_GPS.empty
        errors.append(err)
 #Test good parameter type name
    param_GPS = log.filter("GPS")
    expResponce = 756
    if param_GPS.shape[0]!=expResponce:
        err=error("Incorrect number of messages filtered")
        err.expected=expResponce
        err.actual=param_GPS.shape[0]
        errors.append(err)
    expResponce = ['Date','UTC','MsgType','TimeUS','I','Status','GMS','GWk','NSats','HDop','Lat','Lng','Alt','Spd','GCrs','VZ','Yaw','U']
    if param_GPS.columns.tolist() != expResponce:
        err=error("Filtered column headers are incorrect")
        err.expected=expResponce
        err.actual=param_GPS.columns.tolist()
        errors.append(err)
    return errors
    
    
def Test_All_Method(fileName):
    errors = []
    log = ArduPilotLog(fileName)
    log.parse(verbose=False)
    allData = log.all()
    expResponce = 148394
    if allData.shape[0]!=expResponce:
        err=error("Did not return all messges")
        err.expected=expResponce
        err.actual=allData.shape[0]
        errors.append(err)
    expResponce = ['Date', 'UTC', 'MsgType', 'Type', 'Length', 'Name', 'Format', 'Columns', 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    if allData.columns.tolist() != expResponce:
        err=error("Column headers are incorrect")
        err.expected=expResponce
        err.actual=allData.columns.tolist()
        errors.append(err)
    return errors


def printErrors(errors):
    if errors:
        print('-FAIL-')
        for err in errors:
            print(f'  Error: {err.msg}\n  Expected: {err.expected}\n  Actual: {err.actual}\n')
    else:
        print('PASS')


if __name__=='__main__':
    testFile = ".\\ExampleBinFiles\\00000004.BIN"
    
    print("ArduPilotLog.filter(): ", end='', flush=True)
    errors = Test_Filter_Method(testFile)
    printErrors(errors)
    print("ArduPilotLog.all(): ", end='', flush=True)
    errors = Test_All_Method(testFile)
    printErrors(errors)
    
    


    print("Done!")
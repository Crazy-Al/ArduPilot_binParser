'''
Author: Alex Zaleski

Description:
    This script shows how to create a GreatArc file from an ArduPilot log. 
'''


import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ardupilot_binparser import ArduPilotLog

if __name__ == '__main__':
    import time         #Only used for testing, should be deleted
    import tkinter as tk   #Needed to stops and annoying gray box from popping up.   
    from tkinter.filedialog import askopenfilename  #user to open file manager
    tk.Tk().withdraw()     #Stops and annoying gray box from popping up.

    logFile = askopenfilename(defaultextension='.bin',initialdir=f'{os.getcwd()}/ExampleNinFiles', title="Select .bin file")  #open file manager
    log = ArduPilotLog(logFile)
    log.parse(verbose=True)
    outputName = 'GreatArc_Test_File.ga'
    outputPath = f'{logFile.rsplit('/',2)[0]}/Outputs/{outputName}'
    print(f'GreatArc file saved at: {outputPath}')
    log.saveAsGreatArc(f'{outputPath}')
    
    
    print("Done!")
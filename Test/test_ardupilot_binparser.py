'''
Author:     CrazyAl_
Created:    16 Dec 2023
Modified:   2 June 2025

Description:
    This file tests the functions of ardupilot_binparser.py

Usage:
    python test_ardupilot_binparser.py
'''

import unittest
import os
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ardupilot_binparser import ArduPilotLog

TEST_FILE = "./test_data/00000009.BIN"

class TestArduPilotLog(unittest.TestCase):
    def test_filter(self):
        log = ArduPilotLog(TEST_FILE)
        log.parse(verbose=False)
        ## Test: Invalid parameter handling
        param_GPS = log.filter("BadParameter")
        self.assertEqual(param_GPS.empty, True, "Filter method did not handle invalid parameter input correctly.") 
        ## Test: Good parameter handling
        param_GPS = log.filter("GPS")
        self.assertEqual(param_GPS.shape[0], 1288, "Filter method did not handle valid parameter input correctly.")   
        ## Test: Filter column headers
        expHeaders = ['Date','UTC','MsgType','TimeUS','I','Status','GMS','GWk','NSats','HDop','Lat','Lng','Alt','Spd','GCrs','VZ','Yaw','U']
        self.assertEqual(param_GPS.columns.tolist(),expHeaders, "Column headers were not filtered correctly.")

    def test_all(self):
        log = ArduPilotLog(TEST_FILE)
        log.parse(verbose=False)
        allData = log.all()
        ## Test: Validate all messages parsed
        expNumRows = 295949
        self.assertEqual(allData.shape[0], expNumRows, f'Not all messages parsed, epx: {expNumRows}, actual: {allData.shape[0]}.')
        ### Validate correct column headers
        expHeaders = ['Date', 'UTC', 'MsgType', 'Type', 'Length', 'Name', 'Format', 'Columns', 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
        self.assertEqual(allData.columns.tolist(), expHeaders, "Column headers are not correct.")

if __name__=='__main__':
    unittest.main()
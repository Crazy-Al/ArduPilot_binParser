'''
Author:     Alex Zaleski

'''


import pandas as pd
import matplotlib.pyplot as plt
from ArduPilot_binParser import ArduPilotLog

def printFlightReport(log):
    print('\n-------------------------------------------------')
    print('                  FLIGHT REPORT')
    print('-------------------------------------------------')
    param_STAT = log.filter('STAT')
    takeoffs = param_STAT.loc[(param_STAT['isFlying'] == 1) & (param_STAT['isFlying'].shift() == 0)] # shift, shifts the values in the column down by one row, so that the value at each row is the value from the previous row.
    if takeoffs.empty:
       print(f'TAKEOFF:{"":<8}No takeoff recorded')
    else:
        for takeoff in takeoffs.itertuples():
            print(f'TAKEOFF:{"":<8}{takeoff.Date} @ {takeoff.UTC} UTC.') 
    lands = param_STAT.loc[(param_STAT['isFlying'] == 0) & (param_STAT['isFlying'].shift() == 1)]
    if lands.empty:
        print(f'LANDING:{"":<8}No landing recorded')
    else:
        for land in lands.itertuples():
            print(f'LANDING:{"":<8}{takeoff.Date} @ {takeoff.UTC} UTC.')
    param_GPS = log.filter('GPS')
    print(f'Max Altitude:{"":<3}{round(param_GPS["Alt"].max(),2)} meters')
    print(f'Max Speed:{"":<6}{round(param_GPS["Spd"].max(),2)} m/s')
    print('-------------------------------------------------\n')


def plot_isFlying_Armed(log):
    '''Creates a pd.DataFrame by filtering the log for datetime_UTC, isFlying, and Armed 
    data fields then plots the isFlying and Armed values against datatime_UTC. Function 
    returns the create DataFrame. Use plt.show() externally to show plots.
    
    Args:
        log (ArduPilotLog): A ArduPilotLog object containg the parsed ArduPilot log.
    Return:
        A pd.DataFrame with the fileds datetime_UTC, isFlying, and Armed as columns
    '''
    param_STAT = log.filter('STAT')
    param_STAT = param_STAT[['Date','UTC','isFlying','Armed']]
    param_STAT['datetime_UTC'] = pd.to_datetime(param_STAT['Date']+' ' +param_STAT['UTC'])
    param_STAT = param_STAT[['datetime_UTC', 'isFlying', 'Armed']]
    plt.plot(param_STAT['datetime_UTC'], param_STAT['isFlying'], label='isFlying', marker='o')
    plt.plot(param_STAT['datetime_UTC'], param_STAT['Armed'], label='Armed', marker='x')
    plt.title('Plot of isFlying and Armed over datetime_UTC')
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.yticks([0,1])
    plt.legend()
    plt.grid(True)
    return param_STAT
    
def plot_Alt_Spd(log):
    '''Creates a pd.DataFrame by filtering the log for datetime_UTC, Altitude, and Speed 
    data fields then plots the Altitude on the left y-axis and Speed on the right y-axis 
    against datatime_UTC. Function returns the create DataFrame. e plt.show() externally 
    to show plots.
    
    Args:
        log (ArduPilotLog): A ArduPilotLog object containg the parsed ArduPilot log.
    Return:
        A pd.DataFrame with the fileds datetime_UTC, Alt, and Spd as columns
    '''
    param_GPS = log.filter('GPS')
    param_GPS = param_GPS[['Date','UTC','Alt','Spd']]
    param_GPS['datetime_UTC'] = pd.to_datetime(param_GPS['Date']+' ' +param_GPS['UTC'])
    param_GPS = param_GPS[['datetime_UTC', 'Alt', 'Spd']]
    # Plot altitude against left y-axis and speed against right y-axis
    fig, ax1 = plt.subplots()
    # Plot altitude against left y-axis
    ax1.plot(param_GPS['datetime_UTC'], param_GPS['Alt'], color='b', marker='o', label='Altitude')
    ax1.set_ylabel('Altitude', color='b')
    # Create a secondary y-axis for speed
    ax2 = ax1.twinx()
    ax2.plot(param_GPS['datetime_UTC'], param_GPS['Spd'], color='r', marker='x', label='Speed')
    ax2.set_ylabel('Speed', color='r')
    # Add legends
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines + lines2, labels + labels2, loc='best')
    # Set title and show plot
    plt.title('Altitude and Speed over Time')
    return param_GPS


if __name__ == '__main__':
    import time         #Only used for testing, should be deleted
    import tkinter as tk   #Needed to stops and annoying gray box from popping up.   
    from tkinter.filedialog import askopenfilename  #user to open file manager
    tk.Tk().withdraw()     #Stops and annoying gray box from popping up.

    file = askopenfilename()  #open file manager
    log = ArduPilotLog(file)
    log.parse(verbose=True)
    printFlightReport(log)
    print('\n-------------------------------------------------')
    print(f'{"":<18}SUPPORTING DATA')
    print('-------------------------------------------------')
    param_STAT = plot_isFlying_Armed(log)
    print(param_STAT)
    param_Alt_Spd = plot_Alt_Spd(log)
    print(param_Alt_Spd)
    plt.show()
    print("Done!")
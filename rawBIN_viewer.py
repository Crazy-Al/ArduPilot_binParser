'''
Author: Alex Zaleski
Creation: 14 Aug 2020
Modified: 16 Dec 2023

Description:
    This will allow you to select a .bin file and
    see its content in binary (hex) form.
    The user can input any byte number and see the data starting from 
    that byte number. If the user enters nothing then the next 1024 
    bytes will be displayed. Use 'q' to quit program. 
    Note: There is no error checking implemented on user input.

Usage: 
    ./rawBIN_viewer.py
'''

import tkinter as tk   #Needed to stops and annoying gray box from popping up.   
from tkinter.filedialog import askopenfilename  #user to open file manager
tk.Tk().withdraw()     #Stops and annoying gray box from popping up.

#load .bin file data
File = open(askopenfilename() ,'rb') #open file manager
#get total number of bytes in file
File.seek(0,2) #move curser to end of file
fileSize=File.tell()  #Get the number of bytes in file
File.seek(0)   #move curser back to begining of file
print(f'\nFile: {(File.name).split("/")[-1]}')
print("Total file size: "+str(fileSize)+ " bytes\n")

#read entile file into one variable so we can access parts of the data
binFile=File.read()

start = 0
step = 1024
stop = 0
inpt = ''
while inpt!= 'q':
    inpt = input(":")
    if inpt == '': start = stop  # if user wants next 1024 bytes
    if inpt.isdigit(): start = int(inpt)  # user specified start index
    if inpt != 'q':
        stop = start + step
        print("Viewing range: [" + str(start) + ":" + str(stop)+"]")
        print(binFile[start:stop])   #change range to view differnt parts of the .bin file





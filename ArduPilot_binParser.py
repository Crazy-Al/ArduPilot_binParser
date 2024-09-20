'''
Author:     Alex Zaleski
Created:    16 Dec 2023
Modified:   3 Jan 2024
Version:    4.0

Description:
    -- Information about an Ardupilot .bin File --
    ArduPilot stores its logs in .bin files. If using a Pixhawk the .bin logs are saves to the SD card which
    you can remove and and insert into your computer to download the log files. The .bin file is a binary file
    that logs a ton of inforamation. Each message contains data from a single source, i.e. GPS, IMU, ect. In
    the code below we will refer to the "source" as the Message Type Name. ArduPilot also asignes a unique 
    integer to each Message Type Name, we will call this unique integer the Message Type ID. The log is formed
    be encapsilating each message in a packet. Each packet starts with the two byte packet header,'\xa3\x95', 
    which is followed by the single byte Message Type ID, which is then followed by x bytes of message data.

        Packet Layout
     ------------------------- -------------------------- -------------------
    | Packet Header (2 bytes) | Message Type ID (1 Byte) | Message (x bytes) |
     ------------------------- -------------------------- -------------------

    The first several messages loged are formating messages. ArduPilot has assigned "FMT" as the Message 
    Type Name for these messages and has set the Message Type ID as, '\x80', or 128 in decimal. These FMT 
    messages define how the data of each message type is formatted or organized. The first byte of the FMT 
    message is the Message Type ID that format is defining. This is followed by a single byte defining the 
    expected packet length for that type of message. This packet length includes the 2 byte packet header
    and 1 byte Message Type ID in addition to the actual length of the message. In other words, 
    Packet Length = message length + 3 bytes. The next 4 bytes are the Message Type Name assigned to the 
    message. The following 16 bytes define the data format. Each byte, that is not '\x00', defines the format
    of a data field/column for that message type. These data field identifiers specify the specific type and
    scalar to aply to the data in that field. See, ARDU_TO_STRUCT, in the code below where these idetifiers are 
    used to convert the data to Pyhton Struct format. The remaining 67 bytes define the string column headers 
    for each filed. The important thing to remember is that each log is self-defined and you won't find a standard 
    message format description externally.

        FMT (Format Message Type) Message Layout
     -------------------------- -------------------------- ----------------------------- ------------------------ ----------------------------------------------
    | Message Type ID (1 byte) | Packet length (1 bytes ) | Message Type Name (4 bytes) | Data Format (16 bytes) | Message Type Unique Column Headers (z bytes) |
     -------------------------- -------------------------- ----------------------------- ------------------------ ----------------------------------------------

    The remaining messages after the FMT messages are data messages, non-FMT messages. These messages contain soley 
    data divided into fields. The only way you know what message type the data belongs to is by looking at the 
    Message Type ID byte in the encapsilating packet. Once you know the Message Type ID, you can then look at the 
    FMT messages to define the data fields and their field labels. 

        All non-FMT Messages Layout
     -------------------------------------------------------------------------
    | Data (Packet length (based on the corresponding FMT message) - 3 bytes) |
     -------------------------------------------------------------------------

Usgae:
    python ./ArduPilot_binParser.py
 - OR -
    from ArduPilot_binParser import ArduPilotLog
'''

import struct           # used to convert binary data to usabel data
import pandas as pd     # to export data as .csv
import datetime         # used for date and time properties

class ArduPilotLog:
    def __init__(self, file):
        '''
        This class takes a ardupilot bin filename. When the parse() method is run it will
        open and parse all logde messages into a list of message objects, one object per
        message. 
        a pandas dataframes. This dataframe can be filtered to return useful information.

        Args:
            file (string): Filepath to the .bin file to use.
        modifies:
            Initializes class properties
        Return:
            None
        '''
        self.fileName = file
        self.fileSize = None
        self.ARDU_TO_STRUCT = self.__loadDataFieldFormats() 
        self.packetHeader = b'\xa3\x95'
        self.FMT2ID = {'FMT':128}
        self.msgFormat = {128:[128,89,'FMT','BBnNZ','Type,Length,Name,Format,Columns']} #{msgTypeID:[msgTypeID, packetLength, msgType, ardupilot format, column headers]}
        self.messages = []  # will be a list Message objects

    class Message:  #ArduPilotLog.Message
        def __init__(self):
            '''Internal class to represent a message.
            Args:
                None
            Modifies:
                Initializes message object properties
            Returns:
                None
            '''
            self.date ='NO DATA'
            self.timeUTC ='NO DATA'
            self.typeID = ''
            self.type = ''
            self.data = ''
            self.containsRuntime = False

    def __processMessage(self, msgTypeID, rawMessage):
        '''
        This is where the all hard work happends of converting the binary into
        usable data. A message object is created for every raw binary message
        sent to this method. This method uses the ARDU_TO_STRUCT dictionary to 
        know how to conver the binary data into the correct usable data. This 
        method is what populated the self.messages list.

        Args:
            msgTypeID (int): Integer representation of the Message Type ID for the message being processed.
            rawMessage (byte string): The message, in a string of bytes, to be process. 
        Modifies:
            self.messages: Appends Message objects to this list.
            self.msgFormat: Updates the msgFormat dictionnary with additional message formats
            self.FMT2ID: Updates the FMT2ID dictionary with additional Message Type Name: Mssage Type ID pairs.
        Return: 
            None
        '''
        msg=ArduPilotLog.Message()
        msg.typeID=msgTypeID
        msg.type=self.msgFormat[msg.typeID][2]
        arduByte_format=self.msgFormat[msg.typeID][3]
        msg.containsRuntime = (arduByte_format[0]=='Q')
        structByte_format='<'
        data_multiplier=[]
        #Convert arduByte_format to structByte_format
        for i in arduByte_format:   
            structByte_format+=self.ARDU_TO_STRUCT[i][0]
            data_multiplier.append(self.ARDU_TO_STRUCT[i][1])
        #Convert bytes to human readable data
        msgData=struct.unpack(structByte_format,rawMessage)   #returns tuple
        msgData=list(msgData)  # convert to list so we can modify the data
        for indx,element in enumerate(msgData):
            if isinstance(element,bytes):                       #if element is type bytes
                msgData[indx]=self.__bytes2str(element)
            elif isinstance(element,int):
                msgData[indx]=element*data_multiplier[indx]
        msg.data=msgData
        if msg.type == 'FMT':
            self.FMT2ID.update({msgData[2]:msgData[0]})
            self.msgFormat.update({msgData[0]:msgData.copy()}) #msgData[0] = the message Type ID for the message format being added. msgData[0] != msg.typeID
        self.messages.append(msg)
    
    def __updateDateTime(self):  
        '''Populates the date and time properties for each message. This is done by estimating the 
        time and date based on the nearest previouse GPS message.

        Args:
            None
        Modifies: 
            self.messages: This method updates the date and timeUTC properties of all message objects 
            that are stored in self.messages.
        Return:
            None
        '''
        date='No Data'
        time='No Data'
        lastTimeUpdate=''
        GPS_datum=''
        firstGPS=True
        for msg in self.messages:
            if msg.containsRuntime: msg.data[0]*=1e-6    
            if msg.type=='GPS': 
                lastTimeUpdate = msg.data[0]  #Get TimeUS, time in milisceonds since power-on
                GPS_datum=self.__gps2utc(msg.data[4],msg.data[3]/1000)  #input GWK & GMS, convert GPS time to UTC
                if firstGPS==True:
                    self.__backfillDateTime(lastTimeUpdate,GPS_datum)
                    firstGPS=False
                date = GPS_datum.date()
                time = GPS_datum.time()
            elif msg.containsRuntime:
                if time != "No Data":  # If this is a message comes after the first GPS time stamp
                    timeDiff=msg.data[0]-lastTimeUpdate #new time - old time
                    time = (GPS_datum + datetime.timedelta(seconds=timeDiff)).time()   # "+" because we are adding the time past since the last GPS time update.
            msg.date = date
            msg.timeUTC = time
               

    def __bytes2str(self,byteString):
        '''Convert bytes to string characters
        Args: 
            byteString (bytes): Series of bytes to convert to Unicode string.
        Modifies:
            None
        Return:
            (string): Unicode string representation of the given byteString.
        '''
        string=''
        for byte in byteString:
            if byte!=0:
                string=string+chr(byte)
        return string
    
    def __gps2utc(self,GWk,GMS,leapSecond=18):
        '''Input GPS weeks and Week seconds, convertse the gps time to utc time.
        Args:
            GWK (int): GWK component from the timestamp in the GPS message.
            GMS (int): GMS component from the timestamp in the GPS message.
            leapSeconds (int): (Optional) Look it up if you don't know what leapseconds are.
        Modifies:
            None
        Returns:
            (datetime): DateTime object in UTC corresponding to the given method inputs.
        '''
        GPS_epoch = datetime.datetime(year=1980,month=1,day=6)
        elapsed = datetime.timedelta(weeks=GWk,seconds=(GMS-leapSecond))   #utc=gps-leapseconds
        return GPS_epoch+elapsed

    def __backfillDateTime(self,lastRunTimeUpdate,GPS_datum):
        '''The only real world time stamps we get are from the GPS, however, ardupilot logs data even before
        it recieves it's first GPS ping, so we need to retroactively calculate the date and time for all pre-GPS
        messages. This is done by taking the fiest GPS timestamp and subtracting the run time timesatmp (seconds) 
        for each previouse message to get an estimated log time for that message.

        Args:
            lastRunTimeUpdate (int): The run time since start found in the GPS message. This will be in microSeconds.
            GPS_datum (datetime): datetime object representing the GPS timestamp.
        Modifies:
            self.messages: Modifies the date and time UTC properties of the message objects in self.messages.
        Return:
            None
        '''
        #datetimeformat = "%m-%d-%Y %H:%M:%S.%f"
        date ='No Date'
        time ='No Time'
        for msg in reversed(self.messages): #the first message will be the most recent message before the GPS message.
            if msg.containsRuntime and (msg.date=='No DATA' or msg.timeUTC=='NO DATA'):
                timeDiff=lastRunTimeUpdate-msg.data[0]
                d_t=GPS_datum - datetime.timedelta(seconds=timeDiff)  #we are subtracting the time in seconds that this message occured prior to the first GPS time stamp.
                date = d_t.date()
                time = d_t.time()
            msg.date = date
            msg.timeUTC = time
    
    def __loadDataFieldFormats(self):
        '''This is the key to translating between ArduPilot format and struct format.
        ardu_format: (struct_format)

        Args:
            None
        Modifies:
            None
        Returns:
            (dict): Returns a dictionary where the ardu_format are the keys 
                    and struct_format tuples are the values.
        '''
        long=int   #for python 3
        return {"a": ("64s", None, str),
                "b": ("b", 1, int),
                "B": ("B", 1, int),
                "h": ("h", 1, int),
                "H": ("H", 1, int),
                "i": ("i", 1, int),
                "I": ("I", 1, int),
                "f": ("f", 1, float),
                "n": ("4s", None, str),
                "N": ("16s", None, str),
                "Z": ("64s", None, str),
                "c": ("h", 1.0e-2, float),
                "C": ("H", 1.0e-2, float),
                "e": ("i", 1.0e-2, float),
                "E": ("I", 1.0e-2, float),
                "L": ("i", 1.0e-7, float),
                "d": ("d", 1, float),
                "M": ("b", 1, int),
                "q": ("q", 1, long),  # Backward compat
                "Q": ("Q", 1, long),  # Backward compat
            }
        
    def parse(self, verbose=False):
        '''This decodes the binary into usable data and stores all the messages in a list of message objects. 
        The list of messages will include both FMT messages and non-FMT messages.

        Because reading from disk is a relatively time expensive process, the open() function is set
        to buffer a portion of the file in memory to make reading request quicker. A buffer size of
        1 MB has shown to reduce the processing time, however a larger buffersize can be used if desired.

        Args:
            verbose (bool): (Optional) Set to True if you want parsing progress to be printed to terminal, default False.
        Modifies:
            self.messages: Appends Message objects to this list and updates their date and time properties.
            self.msgFormat: Updates the msgFormat dictionnary with additional message formats
            self.FMT2ID: Updates the FMT2ID dictionary with additional Message Type Name: Mssage Type ID pairs.
        Return: 
            None
        '''
        with open(self.fileName,'rb', buffering=1000000) as binFile:
            binFile.seek(0,2) #move curser to end of file
            self.fileSize=binFile.tell()  #Get the number of bytes in file
            binFile.seek(0)   #move curser back to begining of file
            endOfFile = False if self.fileSize > 0 else True
            tenPercent=self.fileSize*0.1
            if verbose: print(f'\rParsing: {0.0}%', end='')
            while not endOfFile:
                nextBytes = binFile.read(2)
                while nextBytes!=self.packetHeader and not endOfFile:
                   nextBytes = nextBytes[1:] + binFile.read(1)
                   endOfFile = True if len(nextBytes) < 2 else False
                if not endOfFile:
                    msgTypeID = ord(binFile.read(1))  #converts byte to int
                    packetLength = self.msgFormat[msgTypeID][1]
                    rawMessage = binFile.read(packetLength-3)
                    if len(rawMessage) == (packetLength-3): 
                        self.__processMessage(msgTypeID, rawMessage)
                if (binFile.tell()%tenPercent) < 100 and verbose:
                    print(f'\rParsing: {round(binFile.tell()/self.fileSize*100,1)}%', end='')
        if verbose: print(f'\rParsing: {100.0}%')
        self.__updateDateTime()


    def filter(self, msgFilterType: str, csv: bool = False) -> pd.DataFrame:
        '''Creates a dataframe consisting of only the specified message type. The column 
        headers of the dataframe will be defined by the column headers found in the FMT
        message. If csv is specified, the dataFrame will be exported and saved as a .csv.
        CSV is saved to same directory as .bin file.

        Args:
            msgFilterType (string): The Message Type Name of the messages you want displayed
                                    in the dataFrame.
            csv (bool): (Optional) Set to True if you want the resulting dataFrame to be exported 
                        and saved as a .csv, default False.
        Modifies:
            None
        Returns:
            (DataFrame): A dataFrame consisting of messages beloning only to the specified message type.
                         Each row is an indivitual message. 
        '''
        msgTypeID = self.FMT2ID.get(msgFilterType)
        if msgTypeID is None:
            return pd.DataFrame()
        columnHeaders=["Date", "UTC", "MsgType", *self.msgFormat[msgTypeID][4].split(",")]
        #loop through each message in the self.messages list and checks if the message type matches the specified msgFilterType, if so add data to the filteredData list.
        filteredData = [[msg.date.strftime('%Y-%m-%d'), msg.timeUTC.strftime('%H:%M:%S.%f'), msg.type, *msg.data] for msg in self.messages if msg.type == msgFilterType]
        df=pd.DataFrame(data=filteredData, columns=columnHeaders)
        if csv:
            filename=f"{self.fileName[0:-4]}_{msgFilterType}.csv"
            df.to_csv(filename,index=False)
            print(f'CSV saved to {filename}.')
        return df

    
    def all(self, csv=False):
        '''Creates a dataframe of all messages in the self.messages property. 
        Returns dataframe. Saves dataFrame as .csv if csv is set True. CSV is
        saved to same directory as .bin file.

        Args:
            csv (bool): (Optional) Set to True if you want the resulting dataFrame to be exported 
                        and saved as a .csv, default False.
        Modifies:
            None
        Returns:
            (DataFrame): A dataFrame consisting of messages beloning only to the specified message type.
                         Each row is an indivitual message. 

        '''
        metaHeaders = ['Date','UTC','MsgType']
        fmtHeaders = self.msgFormat[self.FMT2ID['FMT']][4].split(",")
        data = [[msg.date.strftime('%Y-%m-%d'), msg.timeUTC.strftime('%H:%M:%S.%f'), msg.type, *msg.data] for msg in self.messages]
        df=pd.DataFrame(data=data)
        columnHeaders = df.columns.tolist()
        columnHeaders[0:(len(metaHeaders)+len(fmtHeaders))]=metaHeaders+fmtHeaders
        df.columns=columnHeaders
        if csv:
            filename=self.fileName[0:-4]+"_ALL.csv"
            df.to_csv(filename,index=False)
            print(f'CSV saved to {filename}.')
        return df
    
    def getMessageTypes(self):
        '''Returns a list of all Message Type Names what are present in the log.
        Args:
            None
        Modifies:
            None
        Return:
            (list): List of Message Type Names present in the log
        '''
        return list(self.FMT2ID.keys())
    



if __name__ == '__main__':
    import time         #Only used for testing, should be deleted
    import tkinter as tk   #Needed to stops and annoying gray box from popping up.   
    from tkinter.filedialog import askopenfilename  #user to open file manager
    tk.Tk().withdraw()     #Stops and annoying gray box from popping up.

    file=askopenfilename()  #open file manager
    tic = time.perf_counter()
    log = ArduPilotLog(file)
    log.parse(verbose=True)
    toc=time.perf_counter()
    print(f'Total time: {toc-tic:0.4f} seconds')
    frame1=log.filter('GPS')
    frame2=log.filter('UNIT',csv=True)
    frame3=log.filter('FMT')
    frame4=log.all(csv=True)
    msgTypes = log.getMessageTypes()  
    print("Done!")

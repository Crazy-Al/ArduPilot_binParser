# ArduPilot_binFile_parser

## Description

The ArduPilotLog class is a useful way to transfer the data in the ArduPilot *.bin* file into a Pandas Dataframe that can be further processed in Python.

## Background on Ardupilot *.bin* Files

### _Packet Layout_

| Packet Header<br>(2 bytes) | Message Type ID<br>(1 byte) | Message<br>(x bytes) |
| ---------------------- | ----------------------- | ---------------- |

ArduPilot stores its logs in *.bin* files. If using a Pixhawk standard compliant flight controller, the *.bin* logs are saved to the SD card, which you can remove and and insert into your computer to download the log files. The *.bin* file is a binary file that logs a ton of information.

Each message contains data from a single *source*, for example GPS, IMU, *etc.* In the code below, we will refer to the "*source*" as the *Message Type Name*. ArduPilot also assigns a unique integer to each *Message Type Name*. We will call this unique integer the *Message Type ID*. The log is formed by encapsulating each message in a packet. Each packet starts with the two byte packet header, `\xa3\x95`, which is followed by the single byte *Message Type ID*, which is then followed by x bytes of message data.

### _FMT (Format Message Type) Message Layout_

| Message Type ID<br>(1 byte) | Packet length<br>(1 byte) | *Message Type Name*<br>(4 bytes) | Data Format<br>(16 bytes) | Message Type Unique Column Headers<br>(z bytes) |
| ------------------------ | ------------------------ | --------------------------- | ---------------------- | -------------------------------------------- |


The first several messages logged are formating messages. ArduPilot has assigned `FMT` as the *Message Type Name* for these messages and has set the *Message Type ID* as, `\x80`, or 128 in decimal.

These `FMT` messages define how the data of each message type is formatted or organized. The first byte of the `FMT` message is the *Message Type ID* that format is defining.

This byte is followed by a single byte defining the expected packet length for that type of message. This packet length includes the 2 byte packet header and 1 byte *Message Type ID*, in addition to the actual length of the message.

In other words, the *packet length* is equal to the *message length* plus 3 bytes, as shown by the following relationship. 

```
'PacketLength' = 'MessageLength' + '3 bytes'
```

The next 4 bytes are the *Message Type Name* assigned to the message.

The following 16 bytes define the data format.

Each byte, that is not `\x00`, defines the format of a data field (or column) for that message type.

These data field identifiers specify the specific type and scalar to apply to the data in that field.

See `ARDU_TO_STRUCT` in the code below, where these identifiers are used to convert the data to a Python `Struct` format.

The remaining 67 bytes define the string column headers for each field. A very important concept to keep in mind is that each log is self-defined, and you won't find a standard message format description externally.

### All non-FMT Messages Layout
 
| Data Packet length<br>(based on the corresponding `FMT` message)<br>3 bytes |
| --------------------------------------------------------------------------- |

The remaining messages after the `FMT` messages are data messages, specifically, non-`FMT` messages. These messages contain only data divided into fields.

The only way you know what message type the data belongs to is by looking at the *Message Type ID* byte in the encapsulating packet.

Once you know the *Message Type ID*, you can then look at the `FMT` messages to define the data fields and their field labels.

## TEST_ArduPilot_binParser (Testing Scipt)

The `TEST_ArduPilot_binParser` module is the unit testing script. Its purpose is to ensure that future changes do not cause unintended errors.

If you make changes to the `ArduPilot_binParser` module, please run `TEST_ArduPilot_binParser` to ensure that no changes cause errors. Furthermore, if you add new functionality to the `ArduPilot_binParser` module, please update the `TEST_ArduPilot_binParser` module by adding appropriate unit tests for those new features.

## rawBIN_Viewer (Support Tool)

This tool displays the raw content of *.bin* files in 1024 byte chunks. To use it, follow these simple steps.

1. Run the file with Python.

2. Select the *.bin* file to view.

3. Give a starting byte index of the chunk you want to display.

Pressing `ENTER` with no input will display the next 1024 byte chunk. Alternatively, you can input another index to jump to another area in the file.

## example_implementation_*.py (Example Scripts)

These scripts are examples of possible ways you can use and implement the `ArduPilotLog` class.

## Installation

Clone and copy the `ArduPilot_binParser.py` file into your project directory or Python library directory.

## Usage

### Option 1 - As a standalone Python program

`python ./ArduPilot_binParser.py`

### Option 2 - As an imported Pythonmodule

`from ArduPilot_binParser import ArduPilotLog`

## Contributing

❤ Contributions are welcome!

Before submitting a merge request, please run TEST_ArduPilot_binParser.py and ensure that all tests pass.

## Authors and acknowledgment

**Author:** Alexander Zaleski

## Project status

Project is in active development.

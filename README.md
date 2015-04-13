pseudocap
=========
A Python 3, cross-platform implementation of cap.exe

## Requirements
Requires cap.exe (SPECIFIC VERSION!), some signed files (user-supplied) and the latest Python 3.4+.

## What It Does
1. The same thing as cap.exe create, but not as a Windows exe.

## Command Line Arguments
### Help

    > pseudocap.py -h

    usage: pseudocap.py FILENAME CAP FIRSTFILE [optional files]

    CAP, but cross-platform
    
    positional arguments:
      filename             Autoloader name
      cap                  Location of cap.exe
      firstfile            Name of first signed file
    
    optional arguments:
      -h, --help           show this help message and exit
      --second SECONDFILE  Name of second signed file
      --third THIRDFILE    Name of third signed file
      --fourth FOURTHFILE  Name of fourth signed file
      --fifth FIFTHFILE    Name of fifth signed file
      --sixth SIXTHFILE    Name of sixth signed file
    
    http://github.com/thurask/pseudocap
    
### Example
  
    > pseudocap.py Autoload.exe cap.exe 10.3.1.2726.signed -s 10.3.1.2727.signed
  
  would make an autoloader from those two signed files and name it Autoload.exe (all in the local folder; paths can also be provided).

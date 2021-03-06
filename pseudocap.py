#!/usr/bin/env python3

import os
import binascii
import glob
import sys
import argparse
import filters

_capversion = "3.11.0.18"


def ghetto_convert(intsize):
    """
    Convert from decimal integer to little endian
    hexadecimal string, padded to 16 characters with zeros.
    :param intsize: Integer you wish to convert.
    :type intsize: integer
    """
    hexsize = format(intsize, '08x')  # '00AABBCC'
    newlist = [hexsize[i:i + 2]
               for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
    while "00" in newlist:
        newlist.remove("00")  # extra padding
    newlist.reverse()
    ghetto_hex = "".join(newlist)  # 'CCBBAA'
    ghetto_hex = ghetto_hex.rjust(16, '0')
    return binascii.unhexlify(bytes(ghetto_hex.upper(), 'ascii'))


def make_offset(cap, firstfile, secondfile="", thirdfile="",
                fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
    """
    Create magic offset file for use in autoloader creation.
    Cap.exe MUST match separator version.
    Defined in _capversion.
    :param cap: Location of cap.exe file.
    :type cap: str
    :param firstfile: First signed file. Required.
    :type firstfile: str
    :param secondfile: Second signed file. Optional.
    :type secondfile: str
    :param thirdfile: Third signed file. Optional.
    :type thirdfile: str
    :param fourthfile: Fourth signed file. Optional.
    :type fourthfile: str
    :param fifthfile: Fifth signed file. Optional.
    :type fifthfile: str
    :param sixthfile: Sixth signed file. Optional.
    :type sixthfile: str
    :param folder: Working folder. Optional.
    :type folder: str
    """
    filecount = 0
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    for i in filelist:
        if i:
            filecount += 1
    # immutable things
    separator = binascii.unhexlify(
        """6ADF5D144E4B4D4E474F46464D4E532B170A0D1E0C14532B372A2D3E2C34522F3C534F514\
F514F514F534E464D514E4947514E51474F70709CD5C5979CD5C5979CD5C597""")
    password = binascii.unhexlify("0" * 160)
    singlepad = binascii.unhexlify("0" * 2)
    doublepad = binascii.unhexlify("0" * 4)
    signedpad = binascii.unhexlify("0" * 16)
    filepad = binascii.unhexlify(
        bytes(
            str(filecount).rjust(
                2,
                '0'),
            'ascii'))  # between 01 and 06
    trailermax = int(7 - int(filecount))
    trailermax = trailermax * 2
    trailer = "0" * trailermax  # 00 repeated between 1 and 6 times
    trailers = binascii.unhexlify(trailer)

    capfile = str(glob.glob(cap)[0])
    capsize = os.path.getsize(capfile)  # size of cap.exe, in bytes

    first = str(glob.glob(firstfile)[0])
    firstsize = os.path.getsize(first)  # required
    if (filecount >= 2):
        second = str(glob.glob(secondfile)[0])
        secondsize = os.path.getsize(second)
    if (filecount >= 3):
        third = str(glob.glob(thirdfile)[0])
        thirdsize = os.path.getsize(third)
    if (filecount >= 4):
        fourth = str(glob.glob(fourthfile)[0])
        fourthsize = os.path.getsize(fourth)
    if (filecount >= 5):
        fifth = str(glob.glob(fifthfile)[0])
        fifthsize = os.path.getsize(fifth)

    # start of first file; length of cap + length of offset
    firstoffset = len(separator) + len(password) + 64 + capsize
    firststart = ghetto_convert(firstoffset)
    if (filecount >= 2):
        secondoffset = firstoffset + firstsize  # start of second file
        secondstart = ghetto_convert(secondoffset)
    if (filecount >= 3):
        thirdoffset = secondstart + secondsize  # start of third file
        thirdstart = ghetto_convert(thirdoffset)
    if (filecount >= 4):
        fourthoffset = thirdoffset + thirdsize  # start of fourth file
        fourthstart = ghetto_convert(fourthoffset)
    if (filecount >= 5):
        fifthoffset = fourthstart + fourthsize  # start of fifth file
        fifthstart = ghetto_convert(fifthoffset)
    if (filecount == 6):
        sixthoffset = fifthoffset + fifthsize  # start of sixth file
        sixthstart = ghetto_convert(sixthoffset)

    with open(os.path.join(folder, "offset.hex"), "w+b") as file:
        file.write(separator)
        file.write(password)
        file.write(filepad)
        file.write(doublepad)
        file.write(firststart)
        file.write(singlepad)
        if (filecount >= 2):
            file.write(secondstart)
        else:
            file.write(signedpad)
        file.write(singlepad)
        if (filecount >= 3):
            file.write(thirdstart)
        else:
            file.write(signedpad)
        file.write(singlepad)
        if (filecount >= 4):
            file.write(fourthstart)
        else:
            file.write(signedpad)
        file.write(singlepad)
        if (filecount >= 5):
            file.write(fifthstart)
        else:
            file.write(signedpad)
        file.write(singlepad)
        if (filecount == 6):
            file.write(sixthstart)
        else:
            file.write(signedpad)
        file.write(singlepad)
        file.write(doublepad)
        file.write(trailers)


def make_autoloader(filename, cap, firstfile, secondfile="", thirdfile="",
                    fourthfile="", fifthfile="", sixthfile="",
                    folder=os.getcwd()):
    """
    Python implementation of cap.exe.
    Writes cap.exe, magic offset, signed files to a .exe file.
    Uses output of make_offset().
    :param filename: Name of autoloader.
    :type filename: str
    :param cap: Location of cap.exe file.
    :type cap: str
    :param firstfile: First signed file. Required.
    :type firstfile: str
    :param secondfile: Second signed file. Optional.
    :type secondfile: str
    :param thirdfile: Third signed file. Optional.
    :type thirdfile: str
    :param fourthfile: Fourth signed file. Optional.
    :type fourthfile: str
    :param fifthfile: Fifth signed file. Optional.
    :type fifthfile: str
    :param sixthfile: Sixth signed file. Optional.
    :type sixthfile: str
    :param folder: Working folder. Optional.
    :type folder: str
    """
    make_offset(
        cap,
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile,
        folder)

    filecount = 0
    filelist = [
        firstfile,
        secondfile,
        thirdfile,
        fourthfile,
        fifthfile,
        sixthfile]
    for i in filelist:
        if i:
            filecount += 1
    try:
        with open(os.path.join(os.path.abspath(folder),
                               filename), "wb") as autoloader:
            try:
                with open(os.path.normpath(cap), "rb") as capfile:
                    print("WRITING CAP VERSION", _capversion + "...")
                    while True:
                        chunk = capfile.read(4096)  # 4k chunks
                        if not chunk:
                            break
                        autoloader.write(chunk)
            except IOError as e:
                print("Operation failed:", e.strerror)
            try:
                with open(os.path.join(folder, "offset.hex"), "rb") as offset:
                    print("WRITING MAGIC OFFSET...")
                    autoloader.write(offset.read())
            except IOError as e:
                print("Operation failed:", e.strerror)
            try:
                with open(firstfile, "rb") as first:
                    print(
                        "WRITING SIGNED FILE #1...\n",
                        os.path.basename(firstfile))
                    while True:
                        chunk = first.read(4096)  # 4k chunks
                        if not chunk:
                            break
                        autoloader.write(chunk)
            except IOError as e:
                print("Operation failed:", e.strerror)
            if (filecount >= 2):
                try:
                    print(
                        "WRITING SIGNED FILE #2...\n",
                        os.path.basename(secondfile))
                    with open(secondfile, "rb") as second:
                        while True:
                            chunk = second.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as e:
                    print("Operation failed:", e.strerror)
            if (filecount >= 3):
                try:
                    print(
                        "WRITING SIGNED FILE #3...\n",
                        os.path.basename(thirdfile))
                    with open(thirdfile, "rb") as third:
                        while True:
                            chunk = third.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as e:
                    print("Operation failed:", e.strerror)
            if (filecount >= 4):
                try:
                    print(
                        "WRITING SIGNED FILE #5...\n",
                        os.path.basename(fourthfile))
                    with open(fourthfile, "rb") as fourth:
                        while True:
                            chunk = fourth.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as e:
                    print("Operation failed:", e.strerror)
            if (filecount >= 5):
                try:
                    print(
                        "WRITING SIGNED FILE #5...\n",
                        os.path.basename(fifthfile))
                    with open(fifthfile, "rb") as fifth:
                        while True:
                            chunk = fifth.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as e:
                    print("Operation failed:", e.strerror)
            if (filecount == 6):
                try:
                    print(
                        "WRITING SIGNED FILE #6...\n",
                        os.path.basename(sixthfile))
                    with open(sixthfile, "rb") as sixth:
                        while True:
                            chunk = sixth.read(4096)  # 4k chunks
                            if not chunk:
                                break
                            autoloader.write(chunk)
                except IOError as e:
                    print("Operation failed:", e.strerror)
    except IOError as e:
        print("Operation failed:", e.strerror)

    print(filename, "FINISHED!\n")
    os.remove(os.path.join(folder, "offset.hex"))

if __name__ == '__main__':
    pars = argparse.ArgumentParser(
        description="CAP, but cross-platform",
        epilog="http://github.com/thurask/pseudocap")
    if len(sys.argv) > 1:
        pars.add_argument("filename", help="Autoloader name")
        pars.add_argument("cap", help="Location of cap.exe")
        pars.add_argument(
            "firstfile",
            type=filters.file_exists,
            help="Name of first signed file")
        pars.add_argument(
            "--second",
            dest="secondfile",
            type=filters.file_exists,
            help="Name of second signed file",
            action="store",
            default="")
        pars.add_argument(
            "--third",
            dest="thirdfile",
            type=filters.file_exists,
            help="Name of third signed file",
            action="store",
            default="")
        pars.add_argument(
            "--fourth",
            dest="fourthfile",
            type=filters.file_exists,
            help="Name of fourth signed file",
            action="store",
            default="")
        pars.add_argument(
            "--fifth",
            dest="fifthfile",
            type=filters.file_exists,
            help="Name of fifth signed file",
            action="store",
            default="")
        pars.add_argument(
            "--sixth",
            dest="sixthfile",
            type=filters.file_exists,
            help="Name of sixth signed file",
            action="store",
            default="")
        args = pars.parse_args(sys.argv[1:])
        make_autoloader(
            args.filename,
            args.cap,
            args.firstfile,
            args.secondfile,
            args.thirdfile,
            args.fourthfile,
            args.fifthfile,
            args.sixthfile)
        smeg = input("Press Enter to exit")
    else:
        pars.print_help()
        sys.exit(1)

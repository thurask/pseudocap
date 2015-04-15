#!/usr/bin/env python3

import os
import binascii
import glob
import sys
import argparse

def fileExists(file):
	if not os.path.exists(file):
		raise argparse.ArgumentError("{0} does not exist".format(file))
	if not str(file).endswith(".signed"):
		raise argparse.ArgumentError("{0} is not a valid signed file".format(file))
	return file

def ghettoConvert(intsize):
	hexsize = format(intsize, '08x')  # '00AABBCC'
	newlist = [hexsize[i:i + 2] for i in range(0, len(hexsize), 2)]  # ['00', 'AA','BB','CC']
	while "00" in newlist:
		newlist.remove("00")  # extra padding
	newlist.reverse()
	ghettoHex = "".join(newlist)  # 'CCBBAA'
	ghettoHex = ghettoHex.rjust(16, '0')
	return binascii.unhexlify(bytes(ghettoHex.upper(), 'ascii'))

def makeOffset(cap, firstfile, secondfile="", thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
	filecount = 0
	filelist = [firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile]
	for i in filelist:
		if i:
			filecount += 1
	# immutable things
	separator = binascii.unhexlify("6ADF5D144E4B4D4E474F46464D4E532B170A0D1E0C14532B372A2D3E2C34522F3C534F514F514F514F534E464D514E4947514E51474F70709CD5C5979CD5C5979CD5C597") #3.11.0.18
	password = binascii.unhexlify("0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
	singlepad = binascii.unhexlify("00")
	doublepad = binascii.unhexlify("0000")
	signedpad = binascii.unhexlify("0000000000000000")
	filepad = binascii.unhexlify(bytes(str(filecount).rjust(2, '0'), 'ascii'))  # between 01 and 06
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
		
	
	firstoffset = len(separator) + len(password) + 64 + capsize  # start of first file; length of cap + length of offset
	firststart = ghettoConvert(firstoffset)
	if (filecount >= 2):
		secondoffset = firstoffset + firstsize  # start of second file
		secondstart = ghettoConvert(secondoffset)
	if (filecount >= 3):
		thirdoffset = secondstart + secondsize  # start of third file
		thirdstart = ghettoConvert(thirdoffset)
	if (filecount >= 4):
		fourthoffset = thirdoffset + thirdsize  # start of fourth file
		fourthstart = ghettoConvert(fourthoffset)
	if (filecount >= 5):
		fifthoffset = fourthstart + fourthsize  # start of fifth file
		fifthstart = ghettoConvert(fifthoffset)
	if (filecount == 6):
		sixthoffset = fifthoffset + fifthsize  # start of sixth file
		sixthstart = ghettoConvert(sixthoffset)
		
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
		
def makeAutoloader(filename, cap, firstfile, secondfile="", thirdfile="", fourthfile="", fifthfile="", sixthfile="", folder=os.getcwd()):
	makeOffset(cap, firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile, folder)
	
	filecount = 0
	filelist = [firstfile, secondfile, thirdfile, fourthfile, fifthfile, sixthfile]
	for i in filelist:
		if i:
			filecount += 1
	try:
		with open(os.path.join(os.path.abspath(folder), filename), "wb") as autoloader:
			try:
				with open(os.path.normpath(cap), "rb") as capfile:
					print("WRITING CAP.EXE...")
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
					print("WRITING SIGNED FILE #1...\n", firstfile)
					while True:
						chunk = first.read(4096)  # 4k chunks
						if not chunk:
							break
						autoloader.write(chunk)
			except IOError as e:
				print("Operation failed:", e.strerror)
			if (filecount >= 2):
				try:
					print("WRITING SIGNED FILE #2...\n", secondfile)
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
					print("WRITING SIGNED FILE #3...\n", thirdfile)
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
					print("WRITING SIGNED FILE #5...\n", fourthfile)
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
					print("WRITING SIGNED FILE #5...\n", fifthfile)
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
					print("WRITING SIGNED FILE #6...\n", sixthfile)
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
	parser = argparse.ArgumentParser(description="CAP, but cross-platform", usage="%(prog)s FILENAME CAP FIRSTFILE [optional files]", epilog="http://github.com/thurask/pseudocap")
	if len(sys.argv) > 1:
		parser.add_argument("filename", help="Autoloader name")
		parser.add_argument("cap", help="Location of cap.exe")
		parser.add_argument("firstfile", type=fileExists, help="Name of first signed file")
		parser.add_argument("--second", dest="secondfile", type=fileExists, help="Name of second signed file", action="store", default="")
		parser.add_argument("--third", dest="thirdfile", type=fileExists, help="Name of third signed file", action="store", default="")
		parser.add_argument("--fourth", dest="fourthfile", type=fileExists, help="Name of fourth signed file", action="store", default="")
		parser.add_argument("--fifth", dest="fifthfile", type=fileExists, help="Name of fifth signed file", action="store", default="")
		parser.add_argument("--sixth", dest="sixthfile", type=fileExists, help="Name of sixth signed file", action="store", default="")
		args = parser.parse_args(sys.argv[1:])
		makeAutoloader(args.filename, args.cap, args.firstfile, args.secondfile, args.thirdfile, args.fourthfile, args.fifthfile, args.sixthfile)
		smeg = input("Press Enter to exit")
	else:
		parser.print_help()
		sys.exit(1)

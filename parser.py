#!/usr/bin/env python3
#
# Copyright (C) 2014 Andreas Schulz <andi.schulz@me.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 US

import sys, time
from datetime import datetime

class LogEntry(object):
    def __init__(self, date, time, proxyIP, proxyPort, dataURL, speed):
        self.date = date
        self.time = time
        self.proxyIP = proxyIP
        self.proxyPort = proxyPort
        self.dataURL = dataURL
        self.speed = speed

    def getOutput(self):
        return (self.time + ";" + 
                self.date + ";" + 
                str(self.speed) + ";" + 
                self.dataURL + ";" + 
                self.proxyIP + ";" + 
                self.proxyPort + "\n")


def checkIfShouldAppend(someList):
    shouldAppend = True
    for substring in someList:
        if "failed" in substring:
            shouldAppend = False
        elif "ERROR" in substring:
            shouldAppend = False
        elif "Retrying" in substring:
            shouldAppend = False
    return shouldAppend


def main(argv=None):
    if not argv:
        argv = sys.argv
    try:
        filename = argv[1]
    except IndexError:
        print("Please provide a file!")
        return

    allentries = []
    
    try:
        input_file = open(sys.argv[1], "r")
    except FileNotFoundError:
        print("Please provide an existing file!")
        return

    a = datetime.now()

    while (True):
        line = input_file.readline()
        if not line: break
        newEntry = []
        newEntry.append(line)
        while (True):
            aLine = input_file.readline()
            if not aLine:
                allentries.append(newEntry)
                break
            if not aLine.startswith("--"):
                newEntry.append(aLine)
            else:
                allentries.append(newEntry)
                newEntry = []
                newEntry.append(aLine)

    input_file.close()

    entries = []
    for entry in allentries:
        if checkIfShouldAppend(entry):
            entries.append(entry)

    #entries now contains only useful entries.

    entryObjects = []

    for entry in entries:
        firstSplits = entry[0].split(" ")
        someDate = firstSplits[0][2:]
        someTime = firstSplits[1][:-2]
        someURL = firstSplits[3][:-1]
        secondSplits = entry[1].split(" ")
        someIP = secondSplits[2][:-1]
        thirdSplits = entry[2].split(" ")
        portSplit = thirdSplits[2].split(":")
        somePort = portSplit[1][:-3]
        someSpeed = 0

        for subString in entry:
            if "B/s" in subString:
                split = subString.split("(")
                aSplit = split[1][:-1].split(")")
                speedString = aSplit[0]
                if "MB" in speedString:
                    bSplit = speedString.split(" ")
                    stringy = bSplit[0].replace(",", ".")
                    someSpeed = int(float(stringy) * 1024)
                else:
                    bSplit = speedString.split(" ")
                    stringy = bSplit[0].replace(",", ".")
                    someSpeed = int(float(stringy))

        entryObjects.append(LogEntry(someDate, someTime, someIP, somePort, someURL, someSpeed))


    entryObjects.sort(key=lambda x: x.speed, reverse=True)

    output_filename = "R_" + str(sys.argv[1]) + "_[" + time.strftime("%d.%m.%Y,%H:%M:%S") + "].txt"
    w = open(output_filename, "w")
    for entry in entryObjects:
        w.write(entry.getOutput())
    w.close()

    b = datetime.now()
    c = b - a
    milli = int(c.total_seconds() * 1000)
    print("Took me " + str(milli) + "ms!")

if __name__ == '__main__':
    sys.exit(main(sys.argv))


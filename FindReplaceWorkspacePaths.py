# ------------------------------------------------------------------------------------------
# FindReplaceWorkspacePaths.py
# Purpose: Fix broken paths in all map documents residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# 02/20/2013
# Created on: Feb 28 2013
# Created by: Matthew McSpadden

# ------------------------------------------------------------------------------------------
# Import system modules
import arcpy, os, sys, datetime
from datetime import datetime
startTime = datetime.now().strftime("%m%d%Y_%H%M%S")

# ------------------------------------------------------------------------------------------
# Local variables:
# txt report output
reportPath = sys.path[0]
infoFile = reportPath + "\\FindReplaceWorkspacePaths_" + startTime + ".txt"

# ------------------------------------------------------------------------------------------
# Read the parameter values:
# 1: Directory
# 2: Old Workspace Path
# 3: New Workspace Path
directory = arcpy.GetParameterAsText(0)
oldPath = arcpy.GetParameterAsText(1)
newPath = arcpy.GetParameterAsText(2)

# ------------------------------------------------------------------------------------------
# Create output info text file.
tInfoFile = file(infoFile, 'wt')
tInfoFile = open(infoFile, 'w')
tInfoFile.write("Start Time: " + startTime)
tInfoFile.write("\n")
tInfoFile.write("\n")

# Report the process starting
tInfoFile.write("Parameters: " + "\n" + "Directory = " + directory + "\n" + "Old Workspace Path = "
                + oldPath + "\n" + "New Workspace Path = " + newPath)
tInfoFile.write("\n")
tInfoFile.write("\n")
tInfoFile.write("Finding Map Documents with Broken Paths...")
tInfoFile.write("\n")

# ------------------------------------------------------------------------------------------
# Walk the directory tree starting at Directory.
# Return the root directory, subdirectories, and a list of files.
# Find the mxds from the list of files and their full system path.
# Get access to the mxd.
try:
        for root, dirs, files in os.walk(directory):
                for filename in files:
                        extension = os.path.splitext(filename)
                        if extension[1] == ".mxd":
                            fullpath = os.path.join(root, filename)
                            mxd = arcpy.mapping.MapDocument(fullpath)
                            brkList = arcpy.mapping.ListBrokenDataSources(mxd)
                            if len(brkList) > 0: #Finds if mxd has broken data sources

                                # Report the mxds and their broken data sources.
                                tInfoFile.write("Found MXD: " + fullpath)
                                tInfoFile.write("\n")
                                tInfoFile.write("Broken Data Sources: ")
                                for brkItem in brkList:
                                       tInfoFile.write(brkItem.name + ", ")
                                tInfoFile.write("\n")

                                # Fix MXD
                                mxd.findAndReplaceWorkspacePaths(oldPath,newPath)

                                # Save Copy of MXD
                                copyPath = extension[0] + "(COPY)" + extension[1]
                                mxd.saveACopy(copyPath)
                                tInfoFile.write("Saved Copy As: " + os.path.join(root, copyPath))
                                tInfoFile.write("\n")

                                # Find if any broken data sources remain and report to file.
                                brkList2 = arcpy.mapping.ListBrokenDataSources(mxd)
                                if len(brkList2) > 0:
                                        tInfoFile.write("Result: Couldn't Fix: ")
                                        for brkItem in brkList2:
                                                tInfoFile.write(brkItem.name + ", ")
                                        tInfoFile.write("\n")
                                        tInfoFile.write("\n")
                                else:
                                        tInfoFile.write("Result: Fixed All Broken Data Sources in " + filename)
                                        tInfoFile.write("\n")
                                        tInfoFile.write("\n")
        

# ------------------------------------------------------------------------------------------
# Write the output to the report.
        stopTime = datetime.now().strftime("%m%d%Y_%H%M%S")
        tInfoFile.write("Finished: " + stopTime)
        tInfoFile.write("\n")
        if tInfoFile:
                tInfoFile.close()
except:
        # make sure to close up the filinput no matter what.
        tInfoFile.write("Unknown Error. Script Did Not Complete")
        if tInfoFile:
                tInfoFile.close()

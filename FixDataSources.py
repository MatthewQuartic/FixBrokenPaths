#-------------------------------------------------------------------------------------------
# FixDataSources
# Purpose: Fix broken paths in all map documents residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# Created on: 04/02/2013
# Created by: Matthew McSpadden

#-------------------------------------------------------------------------------------------
# Import system modules
import arcpy, os, sys, datetime, csv
from datetime import datetime
startTime = datetime.now().strftime("%m%d%Y_%H%M%S")

# ------------------------------------------------------------------------------------------
# Local variables:
# txt report output
reportPath = sys.path[0]
infoFile = reportPath + "\\FixDataSources_" + startTime + ".txt"

#-------------------------------------------------------------------------------------------
# Read the parameter values:
# 0: Directory
#    Valid Values: System File or Directory
# 1: Old Workspace Path
#    Valid Values: String
# 2: Old Workspace Type
#    Valid Values: ACCESS_WORKSPACE, ARCINFO_WORKSPACE, CAD_WORKSPACE, EXCEL_WORKSPACE, FILEGDB_WORKSPACE,
#                  NONE, OLEDB_WORKSPACE, PCCOVERAGE_WORKSPACE, RASTER_WORKSPACE, SDE_WORKSPACE,
#                  SHAPEFILE_WORKSPACE, TEXT_WORKSPACE, TIN_WORKSPACE, VPF_WORKSPACE
# 3: New Workspace Path
#    Valid Values: Workspace
# 4: New Workspace Type
#    Valid Values: ACCESS_WORKSPACE, ARCINFO_WORKSPACE, CAD_WORKSPACE, EXCEL_WORKSPACE, FILEGDB_WORKSPACE,
#                 OLEDB_WORKSPACE, PCCOVERAGE_WORKSPACE, RASTER_WORKSPACE, SDE_WORKSPACE, SHAPEFILE_WORKSPACE,
#                 TEXT_WORKSPACE, TIN_WORKSPACE, VPF_WORKSPACE
# 5: CSV File:
#    Valid Values: File with .csv Extension
#    Valid Format: New layer name must be second item in each row and old layer name must be third item in
#                  each row. Code will test for empty values and instances where layer names are identical.
directory = arcpy.GetParameterAsText(0)
oldPath = arcpy.GetParameterAsText(1)
oldType = arcpy.GetParameterAsText(2)
newPath = arcpy.GetParameterAsText(3)
newType = arcpy.GetParameterAsText(4)
csvFile = arcpy.GetParameterAsText(5)

#-------------------------------------------------------------------------------------------
# If CSV File is given, create a ditionary where the key is the old layer name and the value
#       is the new layer name.
if csvFile != "":
        csvBool = 1
        csvDict = {} # Initialize Dictionary
        with open(csvFile) as f: # Opens CSV File
                reader = csv.reader(f, delimiter = ',')
                for row in reader:
                        if row[1] != row[2] and row[1] != "" and row[2] != "":
                                csvDict[row[2]] = row[1] # Add to dictionary
else:
        csvBool = 0

# ------------------------------------------------------------------------------------------
# Create output info text file.
tInfoFile = file(infoFile, 'wt')
tInfoFile = open(infoFile, 'w')
tInfoFile.write("Start Time: " + startTime)
tInfoFile.write("\n" + "\n")

# Report the process starting
tInfoFile.write("Parameters: " + "\n" + "Directory = " + directory + "\n" + "Old Workspace Path = "
                + oldPath + "\n" + "Old Workspace Type = " + oldType + "\n" + "New Workspace Path = "
                + newPath + "\n" + "New Workspace Type = " + newType)
if csvFile <> "":
        tInfoFile.write("\n" + "CSV File = " + csvFile)
tInfoFile.write("\n" + "\n")
tInfoFile.write("Finding Map Documents with Broken Paths...")
tInfoFile.write("\n")

#-------------------------------------------------------------------------------------------
# Walk the directory tree starting at directory.
# Return the path, a list of directories, and a list of files.
# Find the mxds from the list of files and their full path
# Get access to the mxd.
try:
        for root, dirs, files in os.walk(directory):
                for filename in files:
                        extension = os.path.splitext(filename)
                        if extension[1] == ".mxd":
                            fullpath = os.path.join(root, filename)
                            mxd = arcpy.mapping.MapDocument(fullpath)
                            brkList = arcpy.mapping.ListBrokenDataSources(mxd)
                            if len(brkList) > 0: # Finds if mxd has broken data sources
                                        
                                # Report the mxds and their broken data sources.
                                tInfoFile.write("Found MXD: " + fullpath)
                                tInfoFile.write("\n")
                                #tInfoFile.write("Broken Data Sources: ")       # For Testing
                                #for brkItem in brkList:        # For Testing                
                                #       tInfoFile.write(brkItem.name + ", ")    # For Testing
                                #tInfoFile.write("\n")  # For Testing

                                # Fix paths in the mxd.
                                if oldPath == "ALL" and oldType == "NONE":
                                        mxd.replaceWorkspaces("", "NONE", newPath, newType)
                                elif oldPath == "ALL" and oldType != "NONE":
                                        mxd.replaceWorkspaces("", oldType, newPath, newType)
                                else:
                                        mxd.replaceWorkspaces(oldPath, oldType, newPath, newType)
                                        
                                #tInfoFile.write("Fixed Paths" + "\n") # For Testing
                                
                                # Update each layers definition query and label SQL query(if not a table).
                                for lyr in brkList:
                                        if newType == "FILEGDB_WORKSPACE" or newType == "SDE_WORKSPACE":
                                                try:
                                                        if lyr.dataSource:
                                                                lyr.definitionQuery = lyr.definitionQuery.replace("[", "\"")
                                                                lyr.definitionQuery = lyr.definitionQuery.replace("]", "\"")
                                                                lyr.definitionQuery = lyr.definitionQuery.replace("*", "%")
                                                                        
                                                        try:
                                                                if lyr.supports("LABELCLASSES"):
                                                                        for lblClass in lyr.labelClasses:
                                                                                lblClass.SQLQuery = lblClass.SQLQuery.replace("[", "\"")
                                                                                lblClass.SQLQuery = lblClass.SQLQuery.replace("]", "\"")
                                                                                lblClass.SQLQuery = lblClass.SQLQuery.replace("*", "%")
                                                        except:
                                                                pass
                                                except:
                                                        tInfoFile.write(lyr.name + " Does Not Support Definition and Label Class SQL Queries" + "\n")

                                # If there are any remaining broken layers, try to find them in the csv dictionary and fix them.                
                                brkList2 = arcpy.mapping.ListBrokenDataSources(mxd)
                                if len(brkList2) > 0 and csvBool == 1:
                                        for lyr in brkList2:
                                                try:
                                                        itemSource = lyr.dataSource
                                                        pathTail = os.path.split(itemSource)
                                                        for key, value in csvDict:
                                                                if pathTail[1] == key:
                                                                        lyr.replaceDataSource(newPath, newType, value)
                                                                        lyr.name = value

                                                                        # Update the layers definition query and label SQL query(if not a table).
                                                                        if newType == "FILEGDB_WORKSPACE" or newType == "SDE_WORKSPACE":
                                                                                lyr.definitionQuery = lyr.definitionQuery.replace("[", "\"")
                                                                                lyr.definitionQuery = lyr.definitionQuery.replace("]", "\"")
                                                                                lyr.definitionQuery = lyr.definitionQuery.replace("*", "%")
                                                                                try:
                                                                                        if lyr.supports("LABELCLASSES"):
                                                                                                for lblClass in lyr.labelClasses:
                                                                                                        lblClass.SQLQuery = lblClass.SQLQuery.replace("[", "\"")
                                                                                                        lblClass.SQLQuery = lblClass.SQLQuery.replace("]", "\"")
                                                                                                        lblClass.SQLQuery = lblClass.SQLQuery.replace("*", "%")
                                                                                except:
                                                                                        pass # Layer doesn't support labelclasses. Do nothing.
                                                except:
                                                        pass
                                else:
                                        pass # No more broken layers or csv file not specified.
                                # Find if any broken data sources remain and report to file. 
                                brkList3 = arcpy.mapping.ListBrokenDataSources(mxd)
                                if len(brkList3) > 0:
                                        tInfoFile.write("Result: Broken Layer(s) Still Remaining: ")
                                        for brkItem in brkList3:
                                                tInfoFile.write(brkItem.name + ", ")
                                        tInfoFile.write("\n" + "\n")
                                else:
                                        tInfoFile.write("Result: Fixed All Broken Data Sources in " + filename)
                                        tInfoFile.write("\n" + "\n")
        
                                # Save a copy of the mxd and report it.
                                copyPath = extension[0] + "(COPY)" + extension[1] 
                                mxd.saveACopy(copyPath)
                                tInfoFile.write("Saved Copy As: " + os.path.join(root, copyPath))
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

#-------------------------------------------------------------------------------------------
# ReplaceWorkspaces
# Purpose: Fix broken paths in all map documents residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# Created on: 02/20/2013
# Created by: Matthew McSpadden

#-------------------------------------------------------------------------------------------
# Import system modules
import arcpy, os, sys, datetime
from datetime import datetime
startTime = datetime.now().strftime("%m%d%Y_%H%M%S")

# ------------------------------------------------------------------------------------------
# Local variables:
# txt report output
reportPath = sys.path[0]
infoFile = reportPath + "\\ReplaceWorkspaces_" + startTime + ".txt"

#-------------------------------------------------------------------------------------------
# Read the parameter values:
# 0: Workspace
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
workspace = arcpy.GetParameterAsText(0)
oldPath = arcpy.GetParameterAsText(1)
oldType = arcpy.GetParameterAsText(2)
newPath = arcpy.GetParameterAsText(3)
newType = arcpy.GetParameterAsText(4)

# ------------------------------------------------------------------------------------------
# Create output info text file.
tInfoFile = file(infoFile, 'wt')
tInfoFile = open(infoFile, 'w')
tInfoFile.write("Start Time: " + startTime)
tInfoFile.write("\n")
tInfoFile.write("\n")

# Report the process starting
tInfoFile.write("Parameters: " + "\n" + "Workspace = " + workspace + "\n" + "Old Workspace Path = "
                + oldPath + "\n" + "Old Workspace Type = " + oldType + "\n" + "New Workspace Path = "
                + newPath + "\n" + "New Workspace Type = " + newType)
tInfoFile.write("\n")
tInfoFile.write("\n")
tInfoFile.write("Finding Map Documents with Broken Paths...")
tInfoFile.write("\n")

#-------------------------------------------------------------------------------------------
# Walk the directory tree starting at Workspace.
# Return the path, a list of directories, and a list of files.
# Find the mxds from the list of files and their full path
# Get access to the mxd.
try:
        for root, dirs, files in os.walk(workspace):
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

                                # Fix the mxd.
                                if oldPath == "ALL" and oldType == "NONE":
                                        mxd.replaceWorkspaces("", "NONE", newPath, newType)
                                elif oldPath == "ALL" and oldType != "NONE":
                                        mxd.replaceWorkspaces("", oldType, newPath, newType)
                                else:
                                        mxd.replaceWorkspaces(oldPath, oldType, newPath, newType)

                                # Update each layers definition query and label SQL query(if not a table).
                                for lyr in brkList:
                                        if newType == "FILEGDB_WORKSPACE" or newType == "SDE_WORKSPACE":
                                                brkSource = lyr.dataSource
                                                desc = arcpy.Describe(brkSource)
                                                if desc.DataType != "Table":
                                                        if lyr.supports("DEFINITIONQUERY"):
                                                                lyr.definitionQuery = lyr.definitionQuery.replace("[", "\"")
                                                                lyr.definitionQuery = lyr.definitionQuery.replace("]", "\"")
                                                                lyr.definitionQuery = lyr.definitionQuery.replace("*", "%")

                                                        if lyr.supports("LABELCLASSES"):
                                                                for lblClass in lyr.labelClasses:
                                                                    lblClass.SQLQuery = lblClass.SQLQuery.replace("[", "\"")
                                                                    lblClass.SQLQuery = lblClass.SQLQuery.replace("]", "\"")
                                                                    lblClass.SQLQuery = lblClass.SQLQuery.replace("*", "%")
                                                else:
                                                        lyr.definitionQuery = lyr.definitionQuery.replace("[", "\"")
                                                        lyr.definitionQuery = lyr.definitionQuery.replace("]", "\"")
                                                        lyr.definitionQuery = lyr.definitionQuery.replace("*", "%")

                                # Find if any broken data sources remain and report to file.
                                brkList2 = arcpy.mapping.ListBrokenDataSources(mxd)
                                if len(brkList2) > 0:
                                        tInfoFile.write("Result: Couldn't Fix: ")
                                        for brkItem in brkList2:
                                                tInfoFile.write(brkItem.name + ", ")
                                                tInfoFile.write("\n")
                                                tInfoFile.write("\n")
                                else:
                                        tInfoFile.write("Result: Fixed All Broken Data Sources")
                                        tInfoFile.write("\n")
                                        tInfoFile.write("\n")
                                
                                # Save the mxd.    
                                mxd.save() 

# ------------------------------------------------------------------------------------------
# Write the output to the report.
        #tInfoFile.write(arcpy.GetMessages())
        stopTime = datetime.now().strftime("%m%d%Y_%H%M%S")
        tInfoFile.write("Finished: " + stopTime)
        tInfoFile.write("\n")
        if tInfoFile:
                tInfoFile.close()

except:
        # make sure to close up the filinput no matter what.
        tInfoFile.write(arcpy.GetMessages(3))
        tInfoFile.write("\n")
        if tInfoFile:
                tInfoFile.close()

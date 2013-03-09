# ReplaceDataSource
# Purpose: Fix broken paths for a specified layer in all map documents residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# Created on: 02/20/2013
#Created by: Matthew McSpadden

#-------------------------------------------------------------------------------------------
# Import system modules
import arcpy, os, sys, datetime
from datetime import datetime
startTime = datetime.now().strftime("%m%d%Y_%H%M%S")

# ------------------------------------------------------------------------------------------
# Local variables:
# txt report output
reportPath = sys.path[0]
infoFile = reportPath + "\\ReplaceDataSource_" + startTime + ".txt"

# ------------------------------------------------------------------------------------------
# Read the parameter values:
# 0: Workspace
#    Valid Values: System File or Directory
# 1: Find Layer
#    Valid Values: String
# 2: Replace Workspace
#    Valid Values: Workspace
# 3: Workspace Type
#    Valid Values: ACCESS_WORKSPACE, ARCINFO_WORKSPACE, CAD_WORKSPACE, EXCEL_WORKSPACE, FILEGDB_WORKSPACE,
#                 OLEDB_WORKSPACE, PCCOVERAGE_WORKSPACE, RASTER_WORKSPACE, SDE_WORKSPACE, SHAPEFILE_WORKSPACE,
#                 TEXT_WORKSPACE, TIN_WORKSPACE, VPF_WORKSPACE
# 4: Replace Layer
#    Valid Values: String
workspace = arcpy.GetParameterAsText(0)
oldLayer = arcpy.GetParameterAsText(1)
newWorkspace = arcpy.GetParameterAsText(2)
newWorkspaceType = arcpy.GetParameterAsText(3)
newLayer = arcpy.GetParameterAsText(4)

# ------------------------------------------------------------------------------------------
# Create output info text file.
tInfoFile = file(infoFile, 'wt')
tInfoFile = open(infoFile, 'w')
tInfoFile.write("Start Time: " + startTime)
tInfoFile.write("\n")
tInfoFile.write("\n")

# Report the process starting
tInfoFile.write("Parameters: " + "\n" + "Workspace = " + workspace + "\n" + "Find Layer = "
                + oldLayer + "\n" + "Replace Workspace = " + newWorkspace + "\n" + "Workspace Type = "
                + newWorkspaceType + "\n" + "Replace Layer = " + newLayer)
tInfoFile.write("\n")
tInfoFile.write("\n")
tInfoFile.write("Finding Map Documents with Broken Paths...")
tInfoFile.write("\n")

#-------------------------------------------------------------------------------------------
# Walk the directory tree starting at Workspace.
# Return the path, a list of directories, and a list of files.
# Find the mxds from the list of files and their full path.
# Get access to the mxd.
for root, dirs, files in os.walk(workspace):
        for filename in files:
                extension = os.path.splitext(filename)
                if extension[1] == ".mxd":
                    fullpath = os.path.join(root, filename)
                    mxd = arcpy.mapping.MapDocument(fullpath)
                    lyrCount = 0 # Initialize counter

                    # Create a list of broken data sources in the mxd.
                    # Cycle through list to find the specified layer and fix it's data source using the replaceDataSource method.
                    # Rename the layer in the mxd.
                    for lyr in arcpy.mapping.ListBrokenDataSources(mxd):                       
                        lyr.replaceDataSource(newWorkspace, newWorkspaceType, newLayer)
                        lyr.name = newLayer
                        mxd.save()
                        lyrCount = lyrCount +1
                    tInfoFile.write("Updated " + str(lyrCount) + " layer(s) in " + fullpath)
                    tInfoFile.write("\n")
                    tInfoFile.write("\n")

# ------------------------------------------------------------------------------------------
# Write the output to the report.
#tInfoFile.write(arcpy.GetMessages())
stopTime = datetime.now().strftime("%m%d%Y_%H%M%S")
tInfoFile.write("Finished: " + stopTime)
tInfoFile.write("\n")
if tInfoFile:
        tInfoFile.close()
                                    
                            

# ReplaceWorkspaces
# Purpose: Fix broken paths for all map documents with broken paths residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# 02/20/2013
#
import arcpy, os
#
# Read the parameter values:
# 1: Workspace
# 2: Find Workspace Path
# 3: Find Workspace Type
# 4: Replace Workspace Path
# 5: Replace Workspace Type
#
workspace = arcpy.GetParameterAsText(0)
oldPath = arcpy.GetParameterAsText(1)
oldType = arcpy.GetParameterAsText(2)
newPath = arcpy.GetParameterAsText(3)
newType = arcpy.GetParameterAsText(4)
#
# Walk the directory tree starting at Workspace.
# Return the path, a list of directories, and a list of files.
# Find the mxds from the list of files and their full path
# Get access to the mxd.
#
for root, dirs, files in os.walk(workspace):
        for filename in files:
                extension = os.path.splitext(filename)
                if extension[1] == ".mxd":
                    fullpath = os.path.join(root, filename)
                    mxd = arcpy.mapping.MapDocument(fullpath)
                    brkList = arcpy.mapping.ListBrokenDataSources(mxd)
#
# Find mxds with broken data paths.
# Use ReplaceWorkspaces to fix broken data paths.
# Save the mxd.
#
                    if len(brkList) > 0:
                        if oldPath == "ALL":
                                mxd.replaceWorkspaces("",oldType,newPath, newType)
                        else:
                                mxd.replaceWorkspaces(oldPath,oldType,newPath, newType)

# For each layer, update it's definition query and label SQL query.
#
                    for lyr in arcpy.mapping.ListLayers(mxd):
                        if newType == "FILEGDB_WORKSPACE" or "SDE_WORKSPACE":
                                if lyr.supports("DEFINITIONQUERY"):
                                        lyr.definitionQuery = lyr.definitionQuery.replace("[", "\"")
                                        lyr.definitionQuery = lyr.definitionQuery.replace("]", "\"")
                                        lyr.definitionQuery = lyr.definitionQuery.replace("*", "%")

                                if lyr.supports("LABELCLASSES"):
                                        for lblClass in lyr.labelClasses:
                                            lblClass.SQLQuery = lblClass.SQLQuery.replace("[", "\"")
                                            lblClass.SQLQuery = lblClass.SQLQuery.replace("]", "\"")
                                            lblClass.SQLQuery = lblClass.SQLQuery.replace("*", "%")
                    mxd.save()

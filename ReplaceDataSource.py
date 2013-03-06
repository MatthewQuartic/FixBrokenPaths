# ReplaceDataSource
# Purpose: Fix broken paths for a specified layer in all map documents residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# 02/20/2013
#
import arcpy, os

# Read the parameter values:
# 1: Workspace
# 2: Find Layer
# 3: Replace Workspace
# 4: Workspace Type
# 5: Replace Layer
#
workspace = arcpy.GetParameterAsText(0)
oldLayer = arcpy.GetParameterAsText(1)
newWorkspace = arcpy.GetParameterAsText(2)
newWorkspaceType = arcpy.GetParameterAsText(3)
newLayer = arcpy.GetParameterAsText(4)

# Walk the directory tree starting at Workspace.
# Return the path, a list of directories, and a list of files.
# Find the mxds from the list of files and their full path.
# Get access to the mxd.
#
for root, dirs, files in os.walk(workspace):
        for filename in files:
                extension = os.path.splitext(filename)
                if extension[1] == ".mxd":
                    fullpath = os.path.join(root, filename)
                    mxd = arcpy.mapping.MapDocument(fullpath)

# Create a list of broken data sources in the mxd.
# Cycle through list to find the specified layer and fix it's data source using the replaceDataSource method.
# Rename the layer in the mxd.
# Save the mxd.
#
                    for lyr in arcpy.mapping.ListBrokenDataSources(mxd):
# Test if layer is a table view. If so, fix data source, rename layer, and save.
#
                            for list in arcpy.mapping.ListTableViews(mxd):
                                    if list.dataSource == oldLayer:
                                            lyr.replaceDataSource(newWorkspace, newWorkspaceType, newLayer)
                                            mxd.save()
                                    else:
                                            if lyr.supports("DATASOURCE"): #Won't work for table views. Reason lyr is tested as table first.
                                                    if lyr.dataSource == oldLayer:
                                                            lyr.replaceDataSource(newWorkspace, newWorkspaceType, newLayer)
                                                            lyr.name = newLayer
                                                            mxd.save()

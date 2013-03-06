# FindAndReplaceWorkspacePaths
# Purpose: Fix broken paths in all map documents residing under a specified folder/directory.
# ArcGIS Version 10.1
# Python Version 2.7
# 02/20/2013
#
import arcpy, os

# Read the parameter values:
# 1: Workspace
# 2: Find Workspace Path
# 3: Replace Workspace Path
#
Workspace = arcpy.GetParameterAsText(0)
Find_Workspace_Path = arcpy.GetParameterAsText(1)
Replace_Workspace_Path = arcpy.GetParameterAsText(2)

# Walk the directory tree starting at Workspace.
# Return the root directory, subdirectories, and a list of files.
# Find the mxds from the list of files and their full system path.
# Get access to the mxd.
#
for root, dirs, files in os.walk(Workspace):
        for filename in files:
                extension = os.path.splitext(filename)
                if extension[1] == ".mxd":
                    fullpath = os.path.join(root, filename)
                    mxd = arcpy.mapping.MapDocument(fullpath)
                    brkList = arcpy.mapping.ListBrokenDataSources(mxd)

# Find mxds with broken data paths.
# Use findAndReplaceWorkspacePaths to fix broken data paths.
# Save the mxd.
#
                    if len(brkList) > 0: 
                        mxd.findAndReplaceWorkspacePaths(Find_Workspace_Path,Replace_Workspace_Path)
                        mxd.save()

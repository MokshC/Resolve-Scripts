#!/usr/bin/env python
# Moksh

"""
This file serves to return a DaVinci Resolve object
"""

import os
import sys

# import GetResolve but internally to avoid possible import error
# input: none
# output: bmd.scriptapp("Resolve")
def GetResolve():
    try:
    # The PYTHONPATH needs to be set correctly for this import statement to work.
    # An alternative is to import the DaVinciResolveScript by specifying absolute path (see ExceptionHandler logic)
        import DaVinciResolveScript as bmd
    except ImportError:
        if sys.platform.startswith("darwin"):
            expectedPath="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
        elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
            import os
            expectedPath=os.getenv('PROGRAMDATA') + "\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"
        elif sys.platform.startswith("linux"):
            expectedPath="/opt/resolve/Developer/Scripting/Modules/"

        # check if the default path has it...
        print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
        try:
            import imp
            bmd = imp.load_source('DaVinciResolveScript', expectedPath+"DaVinciResolveScript.py")
        except ImportError:
            # No fallbacks ... report error:
            print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
            print("For a default DaVinci Resolve installation, the module is expected to be located in: "+expectedPath)
            sys.exit()
    return bmd.scriptapp("Resolve")

# Global Variables
resolve = GetResolve()
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
tl = project.GetCurrentTimeline()

################################################################################################
# Functions #
#############

# gets stored info from /tmp/
# input: none
# output: color, name, note [str]
def read():

	# path of parent and filename
	parent = "/tmp/Mokshs-Marker-Tool/"
	filename = sorted(os.listdir(parent))[-1] # this ensures to only get the newest file
	path = parent + filename

	# open the storage of the flags
	storage = open(path, "r")

	# read convert the markers to correct format
	rawMem = storage.readlines()
	mem = []
	for i in rawMem:
		mem.append(i.strip())
	
	return mem[0], mem[1], mem[2]

# Gets current frame number
# input: tl [timeline item]
# output: frame [str]
def currentFrame(tl):

	start = int(tl.GetStartFrame())
	currentTC = tl.GetCurrentTimecode()
	fps = int(round(float(tl.GetSetting('timelineFrameRate'))))

	tcLst = currentTC.split(':') # split TC into lst
	seconds = (int(tcLst[0]) * 3600) + (int(tcLst[1]) * 60) + int(tcLst[2]) # convert to seconds
	frames = (seconds * fps) +  int(tcLst[3]) - start # convert to frames

	return frames

# Change marker color and names based on stored memory information
def main():

	# this block will make sure the button still works if you switch projects
	project = projectManager.GetCurrentProject() # get project
	tl = project.GetCurrentTimeline() # get tl

	# getting necessary information from project and stored memory
	frame = currentFrame(tl)
	markers = tl.GetMarkers()
	color, name, note = read()	

	# if name or note is left empty, leave the original			
	if str(name) == "":
		name = markers[frame]['name']			
	if str(note) == "":
		note = markers[i]['note']

	tl.DeleteMarkerAtFrame(frame) # delete marker
	# replace it			
	tl.AddMarker(frame, color, name, note, markers[frame]["duration"], markers[frame]["customData"])


main()


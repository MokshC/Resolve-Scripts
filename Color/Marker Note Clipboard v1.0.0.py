# Moksh
# -*- coding: utf-8 -*-

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
projectManager = resolve.GetProjectManager() # get manager
ColorLst = ['Green','Blue','Cyan','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
flags = []

################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Marker Note Clipboard",
			"ID": "DCWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True,},
			"Geometry": [1000,950,600,140], # x-position, y-position, width, height
			}, 
			[ui.VGroup({"Spacing": 10}, [
				
				# Edit group 1
				ui.HGroup({"Spacing": 3,}, [
					ui.LineEdit({"ID": "desc1", "Text": '', "Weight": 2}),
					ui.Button({"ID": "edit1", "Text": "Edit Note", "Weight": 1})
					]),

				# Edit group 2
				ui.HGroup({"Spacing": 3,}, [
					ui.LineEdit({"ID": "desc2", "Text": '', "Weight": 2}),
					ui.Button({"ID": "edit2", "Text": "Edit Note", "Weight": 1})
					]),

				# Edit group 3
				ui.HGroup({"Spacing": 3,}, [
					ui.LineEdit({"ID": "desc3", "Text": '', "Weight": 2}),
					ui.Button({"ID": "edit3", "Text": "Edit Note", "Weight": 1})
					])
				])
			])

itm = window.GetItems() # not sure what this does

checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in window.WindowTitle) else sys.exit()

################################################################################################
# Functions #
#############

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

# replace description of marker from first line
def _edit3(ev):

	# this block will make sure the button still works if you switch projects
	global projectManager # allows global edit of projectManager
	projectManager = resolve.GetProjectManager() # get manager
	project = projectManager.GetCurrentProject() # get project
	tl = project.GetCurrentTimeline() # get tl
	
	frame = currentFrame(tl)
	markers = tl.GetMarkers()

	# if name is left empty, it is original name			
	if str(itm["desc3"].Text) != "":
		desc = str(itm["desc3"].Text)
	else:
		desc = markers[frame]['note']

	tl.DeleteMarkerAtFrame(frame) # delete marker
	# replace it			
	tl.AddMarker(frame, markers[frame]["color"], markers[frame]["name"], desc, markers[frame]["duration"], markers[frame]["customData"])

# replace description of marker from first line
def _edit2(ev):

	# this block will make sure the button still works if you switch projects
	global projectManager # allows global edit of projectManager
	projectManager = resolve.GetProjectManager() # get manager
	project = projectManager.GetCurrentProject() # get project
	tl = project.GetCurrentTimeline() # get tl
	
	frame = currentFrame(tl)
	markers = tl.GetMarkers()

	# if name is left empty, it is original name			
	if str(itm["desc2"].Text) != "":
		desc = str(itm["desc2"].Text)
	else:
		desc = markers[frame]['note']

	tl.DeleteMarkerAtFrame(frame) # delete marker
	# replace it			
	tl.AddMarker(frame, markers[frame]["color"], markers[frame]["name"], desc, markers[frame]["duration"], markers[frame]["customData"])

# replace description of marker from first line
def _edit1(ev):

	# this block will make sure the button still works if you switch projects
	global projectManager # allows global edit of projectManager
	projectManager = resolve.GetProjectManager() # get manager
	project = projectManager.GetCurrentProject() # get project
	tl = project.GetCurrentTimeline() # get tl
	
	frame = currentFrame(tl)
	markers = tl.GetMarkers()

	# if name is left empty, it is original name			
	if str(itm["desc1"].Text) != "":
		desc = str(itm["desc1"].Text)
	else:
		desc = markers[frame]['note']

	tl.DeleteMarkerAtFrame(frame) # delete marker
	# replace it			
	tl.AddMarker(frame, markers[frame]["color"], markers[frame]["name"], desc, markers[frame]["duration"], markers[frame]["customData"])

# needed to close window
def _close(ev):
	disp.ExitLoop()
window.On.DCWin.Close = _close

################################################################################################
# GUI Elements #
# manipulations

# button presses
window.On.edit1.Clicked = _edit1
window.On.edit2.Clicked = _edit2
window.On.edit3.Clicked = _edit3
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################

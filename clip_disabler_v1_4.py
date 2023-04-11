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
ColorLst = ['Green','Blue','Cyan','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']

################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Clip Disabler",
			"ID": "CDWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True,},
			"Geometry": [1000,950,260,130], # x-position, y-position, width, height
			}, 
			[ui.VGroup({"Spacing": 1}, [
				ui.Button({"ID": "Button", "Text": "Disable/Enable", "Weight": 3}),
				ui.HGroup({"Spacing": 1,}, [ 	
					ui.ComboBox({"ID": "mark_color", "Weight": 0}),
					ui.LineEdit({"ID": "mark_name", "Text": '', "Weight": 2}),
					ui.Button({"ID": "Flip", "Text": "Flip Marker", "Weight": 1})
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

# checks if any track is locked
# input: timeline [item]
# output: T/F [bool]
def trackslocked(timeline):
	
	# checks each track, if any is locked return true
	for i in range(1, timeline.GetTrackCount("video")+1):
		if timeline.GetIsTrackLocked("video", i):
			return True

	# else return false
	return False

# unlocks all tracks
# input: timeline [item]
# output: none
def unlock_tracks(timeline):

	global resolve
	for i in range(1, timeline.GetTrackCount("video")+1):
		timeline.SetTrackLock("video", i, False)

# locks all tracks
# input: timeline [item]
# output: none
def lock_tracks(timeline):

	global resolve
	for i in range(1, timeline.GetTrackCount("video")+1):
		timeline.SetTrackLock("video", i, True)

# disables/enables clip
# input: clip [item]
# output: none
def disable_clip(clip):

	# if clip is enabled, disable
	if clip.GetClipEnabled():
		clip.SetClipEnabled(False)
	# if clip is disabled, enable	
	else:
		clip.SetClipEnabled(True)

# Change current marker color and name
def _flip(ev):

	# this block will make sure the button still works if you switch projects
	projectManager = resolve.GetProjectManager() # get manager
	project = projectManager.GetCurrentProject() # get project
	tl = project.GetCurrentTimeline() # get tl
	
	frame = currentFrame(tl)
	markers = tl.GetMarkers()
	
	# if name is left empty, it is original name			
	if str(itm["mark_name"].Text) != "":
		name = str(itm["mark_name"].Text)
	else:
		name = markers[frame]['name']

	tl.DeleteMarkerAtFrame(frame) # delete marker
	# replace it			
	tl.AddMarker(frame, str(itm["mark_color"].CurrentText), name, markers[frame]["note"], markers[frame]["duration"], markers[frame]["customData"])

def _main(ev):

	# this block will make sure the button still works if you switch projects
	global resolve # get resolve
	projectManager = resolve.GetProjectManager() # get manager
	project = projectManager.GetCurrentProject() # get project
	timeline = project.GetCurrentTimeline() # get tl
	clip = timeline.GetCurrentVideoItem() # get clip
	
	# disables clip
	if not trackslocked(timeline):
		disable_clip(clip)
	# bypasses clip lock, if it is on
	else:
		unlock_tracks(timeline)
		disable_clip(clip)
		lock_tracks(timeline)

# needed to close window
def _close(ev):
	disp.ExitLoop()
window.On.CDWin.Close = _close

################################################################################################
# GUI Elements #
# manipulations
itm['mark_color'].AddItems(ColorLst) # adds items to dropdown
# button presses
window.On.Button.Clicked = _main
window.On.Flip.Clicked = _flip
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################

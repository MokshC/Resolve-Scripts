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

################################################################################################
# Functions #
#############

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

def main():

	# this block will make sure the button still works if you switch projects
	global projectManager # allows global edit of projectManager
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

main()

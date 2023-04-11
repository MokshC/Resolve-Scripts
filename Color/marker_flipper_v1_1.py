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
projectManager = resolve.GetProjectManager()
project = projectManager.GetCurrentProject()
tl = project.GetCurrentTimeline()
origColorLst = ['Yellow','All','Blue','Cyan','Green','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
newColorLst = ['Green','Blue','Cyan','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Marker Flipper",
			"ID": "CDWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True,},
			"Geometry": [1500,500,280,120], # x-position, y-position, width, height
			}, 
			[ui.VGroup({"Spacing": 10,},[
				# Color flip				
				ui.HGroup({"Spacing": 1,}, [ 	
					ui.Label({"ID": "flip_label","Text": "Flip ", "Weight": 0}),
					ui.ComboBox({"ID": "orig_color", "Weight": 0}),
					ui.Label({"ID": "to_label","Text": " markers to ", "Weight": 0}),
					ui.ComboBox({"ID": "new_color", "Weight": 0})
				]),
				# Name flip
				ui.HGroup({"Spacing": 1,}, [ 	
					ui.Label({"ID": "name_label","Text": "Flip names to ", "Weight": 0}),
					ui.LineEdit({"ID": "mark_name", "Text": '', "Weight": 1})
				]),
				# Flip button
				ui.Button({"ID": "Button", "Text": "Flip!", "Weight": 0}),]), 
			])

itm = window.GetItems() # not sure what this does

checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in window.WindowTitle) else sys.exit()

################################################################################################
# Functions #
#############

# Change all marker colors and names based on input information
def _main(ev):

	markers = tl.GetMarkers() # get all markers

	# for every marker, delete it and replace it with one of new color and name
	for i in markers:
		if markers[i]["color"] == str(itm["orig_color"].CurrentText):

			# if name is left empty, it is original name			
			if str(itm["mark_name"].Text) != "":
				name = str(itm["mark_name"].Text)
			else:
				name = markers[i]['name']

			tl.DeleteMarkerAtFrame(i) # delete marker
			# replace it			
			tl.AddMarker(i, str(itm["new_color"].CurrentText), name, markers[i]["note"], markers[i]["duration"], markers[i]["customData"])

# needed to close window
def _close(ev):
	disp.ExitLoop()
window.On.CDWin.Close = _close

################################################################################################
# GUI Elements #
# manipulations
itm['orig_color'].AddItems(origColorLst) # adds items to dropdown
itm['new_color'].AddItems(newColorLst) # adds items to dropdown
# button presses
window.On.Button.Clicked = _main
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################

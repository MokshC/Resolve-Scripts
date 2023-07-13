#!/usr/bin/env python
# Moksh

"""
This file serves to return a DaVinci Resolve object
"""

import os
import sys
from datetime import date

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
newColorLst = ['Red','Blue','Cyan','Green','Yellow','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']
################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Marker Memory Editor",
			"ID": "MMWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True,},
			"Geometry": [1500,500,280,200], # x-position, y-position, width, height
			}, 
			[ui.VGroup({"Spacing": 10,},[
				# Color flip				
				ui.HGroup({"Spacing": 1,"Weight":2}, [ 	
					ui.Label({"ID": "flip_label","Text": "Flip marker to ", "Weight": 0}),
					ui.ComboBox({"ID": "new_color", "Weight": 0})
				]),
				# Name flip
				ui.HGroup({"Spacing": 1,"Weight":2}, [ 	
					ui.Label({"ID": "name_label","Text": "Flip name to ", "Weight": 0}),
					ui.LineEdit({"ID": "mark_name", "Text": '', "Weight": 1})
				]),
				# Note flip
				ui.VGroup({"Spacing": 3,"Weight":5}, [ 	
					ui.Label({"ID": "note_label","Text": "Flip note to ", "Weight": 0}),
					ui.LineEdit({"ID": "mark_note", "Text": '', "Weight": 5})
				]),
				# Flip button
				ui.Button({"ID": "Button", "Text": "Add to Memory", "Weight": 0}),]), 
			])

itm = window.GetItems() # not sure what this does

checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in window.WindowTitle) else sys.exit()

################################################################################################
# Functions #
#############

# Add marker info to /tmp/ memory
def _main(ev):

	# Collect information from UI
	color = itm["new_color"].CurrentText
	name = str(itm["mark_name"].Text)
	note = str(itm["mark_note"].Text)
	
	# path of parent and filename
	parent = "/tmp/Mokshs-Marker-Tool/"
	filename = str(date.today()).replace("-","") + ".txt"
	path = parent + filename

	# if the folder doesn't exist, create it
	if os.path.isdir(parent) == False:
		os.mkdir(parent)	
	
	# now open the path
	storage = open(path, 'w')

	# write marker info to storage
	marker = '\n'.join([color, name, note])
	storage.write(marker)


# needed to close window
def _close(ev):
	disp.ExitLoop()
window.On.MMWin.Close = _close

################################################################################################
# GUI Elements #
# manipulations
itm['new_color'].AddItems(newColorLst) # adds items to dropdown
# button presses
window.On.Button.Clicked = _main
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################


# Moksh
# -*- coding: utf-8 -*-

import sys

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
timeline = project.GetCurrentTimeline()
color_lst = ['All','Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']

def main_ui():
	# vertical group
	window = [ui.VGroup({"Spacing": 10,},[
			# horizontal groups
			# Color for marker selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "color_label","Text": "What color marker should be exported?", "Weight": 4}),
				ui.ComboBox({"ID": "marker_color", "Weight": 2})
			]),
			# Preset selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "preset_label","Text": "What preset should I used?", "Weight": 4}),
				ui.ComboBox({"ID": "render_preset", "Weight": 2})
			]),
			# Timeline selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "tl_preset_label","Text": "What timeline should I used?", "Weight": 4}),
				ui.ComboBox({"ID": "tl_preset", "Weight": 3})
			]),
			# File name selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "name_label","Text": "What should it be named?", "Weight": 3}),
				ui.LineEdit({"ID": "file_name", "Text": str(timeline.GetName()), "Weight": 4}),
				ui.ComboBox({"ID": "dot_underscore", "Weight": 1})
			]),
			# Export to text
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "export_label","Text": "Export to:", "Weight": 1}),				
				ui.Label({"ID": "export_path","Text": "Please select a folder", "Weight": 4}),
				ui.Button({"ID": "export_location","Text":"Select Export Location", "Weight": 1})
			]),
			# button for export
			ui.Button({"ID": "Export", "Text": "Add to Render Queue", "Weight": 0})
			]) 
		]
	return window



################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Markers to Render Queue",
			"ID": "MTRWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [1500,500,700,200], # x-position, y-position, width, height
			}, 
			main_ui())


itm = window.GetItems() # Grabs all UI elements to be manipulated

checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in window.WindowTitle) else sys.exit()

################################################################################################
# Functions #
#############


# gets index of timeline
# input: project [item], tl_name [str]
# output: i [int]
def tl_idx(proj, tl_name):

	print(tl_name)

	for i in range(1,proj.GetTimelineCount()+1):
		name = proj.GetTimelineByIndex(i).GetName()
		if name == tl_name:
			print(i)
			return int(i)

# creates list of all timelines in project, and sets current timeline as Default
# input: project [item]
# output: tl_lst [list]
def tl_lst(proj):
	
	tl_lst = [] # placeholder will be filled
	orig_tl = str(timeline.GetName()) # timeline name of current tl

	# gets every tl name in project and appends to lst
	for i in range(1,proj.GetTimelineCount()+1):
		name = proj.GetTimelineByIndex(i).GetName()
		if name != orig_tl: # does not append original name
			tl_lst.append(name)
		
	tl_lst = sorted(tl_lst) # sorts list		
	# start list of timeline names with current timeline and "All"
	# tl_lst.insert(0,"All")
	tl_lst.insert(0, orig_tl)

	return tl_lst # return the list

# creates a sorted list of all render presets
# input: project [item]
# output: presets [sorted list]
def preset_lst(project):
	renders = project.GetRenderPresets()
	presets = []

	for i in renders:
		presets.append(str(renders[i]))	

	return sorted(presets)

# gets all markers of selected color from timeline
# input: timeline [item]
# output: marker start positons in color_markers [lst]
#         and all info in markers [dict]
def get_markers(tl):
	# color is selected from current text
	color = itm["marker_color"].CurrentText
	print("Looking for "+color+" markers")

	# gets ALL markers	
	markers = tl.GetMarkers()

	# gets only the markers of color selected
	color_markers = []
	print("Returning...")
	for i in markers:	
		if color == "All":
			color_markers.append(i)	
		elif markers[i]["color"] == color:				
			color_markers.append(i)
	# if theres no markers at the end print an error
	if color_markers == []:
		print("    ERROR " + color + " markers not found")

	return sorted(color_markers), markers

# needed to close window
def _close(ev):
	disp.ExitLoop()

# opens file browser and stores as text on ui
def _file_browser(ev):
	location = fu.RequestDir()
	itm["export_path"].Text = str(location) 

# recursively adds _## to duplicate names in list given
# input [lst]
# output [lst]
def dup_fix(names):

	if sorted(list(set(names))) == sorted(names):
		return names

	else:
		padding = len(str(len(names)))
		
		for i in range(len(names)):
			names[i] = names[i] + '_' + str(i+1).zfill(padding)
		dup_fix(names)

# using UI gets filename user has selected, '#'s will count up from 1
# with padding based on number of markers
# input: markers [lst]
# output: filenames [lst]
def get_filenames(markers):

	filenames = [] # placeholder list will be filled
	padding = len(str(len(markers))) # finds padding by finding highest number 
	num = 1 # starting counter

	# for every marker create a name
	for mark in markers:
		padded_num = str(num).zfill(padding) # number with padding
		name = str(padded_num).join(str(itm["file_name"].Text).split('#')) + str(itm['dot_underscore'].CurrentText)
		filenames.append(name)
		num += 1

	return filenames

# this will create render projects and start rendering
# input: project, timeline, markers, all_markers, path, filenames
# output: none
def export_stills(proj, tl, markers, all_markers, path, filenames):

	print("Setting TL")
	proj.SetCurrentTimeline(tl)
	print("Set")
	print("Setting Preset")
	proj.LoadRenderPreset(itm["render_preset"].CurrentText) # set preset for render
	print("Set")
	startFrame = tl.GetStartFrame() # get start frame of timeline
	counter = 0 # used in for loop for file names
	print("Setting in/out points")
	# for every marker create a unique render job
	for mark in markers:
		print("  ", counter)
		in_point = startFrame + mark
		out_point = startFrame + mark + all_markers[mark]['duration'] - 1
		print("    Calculated")		
		# set settings to selected by user
		print(in_point, out_point)
		print(path) 
		print(filenames[counter])
		proj.SetRenderSettings({"MarkIn": in_point, "MarkOut": out_point, "TargetDir": path, "CustomName": filenames[counter]})
		proj.AddRenderJob() # adds render job
		counter += 1
	print("Done")
	# proj.StartRendering() # starts render after loop


def _main(ev):

	# gets all the details down to the clip
	global resolve
	global itm
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	timeline = project.GetTimelineByIndex(tl_idx(project, itm["tl_preset"].CurrentText))
	# clip = timeline.GetCurrentVideoItem()		
	
	# get a list of all the markers of selected color
	markers, all_markers = get_markers(timeline)
	# get path to export to
	path = itm["export_path"].Text
	# get file names
	filenames = get_filenames(markers)
	# start exporting
	export_stills(project, timeline, markers, all_markers, path, filenames)

################################################################################################
# GUI Elements #
# manipulations
itm['marker_color'].AddItems(color_lst) # adds items to dropdown
itm["render_preset"].AddItems(preset_lst(project)) # adds list of render presets to dropdown
itm["tl_preset"].AddItems(tl_lst(project)) # adds list of timelines to dropdown
itm['dot_underscore'].AddItems(["",".","_","#"]) # adds dot and underscore to dropdown
# button presses
window.On.Export.Clicked = _main
window.On.export_location.Clicked = _file_browser
window.On.MTRWin.Close = _close
# window loops
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################

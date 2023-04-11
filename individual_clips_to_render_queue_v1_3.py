# Moksh
# -*- coding: utf-8 -*-

import sys
from collections import Counter


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

def main_ui():
	# vertical group
	window = [ui.VGroup({"Spacing": 10,},[
			# horizontal groups
			# Preset selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "preset_label","Text": "What preset should I use?", "Weight": 4}),
				ui.ComboBox({"ID": "render_preset", "Weight": 2})
			]),
			# Timeline selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "tl_preset_label","Text": "What timeline should I use?", "Weight": 4}),
				ui.ComboBox({"ID": "tl_preset", "Weight": 3})
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
window = disp.AddWindow({"WindowTitle": "Moksh's Individual Clips to Render Queue",
			"ID": "ICEWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [1500,500,700,150], # x-position, y-position, width, height
			}, 
			main_ui())


itm = window.GetItems() # Grabs all UI elements to be manipulated

checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in window.WindowTitle) else sys.exit()

################################################################################################
# Functions #
#############


# gets all source names from tl
# input: tl [item]
# output: name_lst [lst]
def source_names(tl):

	# fill item_lst with all clips in tl
	clip_lst = []
	for i in range(1, timeline.GetTrackCount("video")+1):
		clip_lst.extend(tl.GetItemListInTrack("video",i))


	# gets all the source names, ins, and outs from clips, avoiding clips that are disabled
	name_lst = []
	in_lst = []
	out_lst = []
	for clip in clip_lst:
		if clip.GetClipEnabled():
			name_lst.append(str(clip.GetMediaPoolItem().GetClipProperty('Reel Name')))
			in_lst.append(clip.GetStart())
			out_lst.append(clip.GetEnd())
		else:
			pass

	print(name_lst)
	print(in_lst)
	print(out_lst)
	return name_lst, in_lst, out_lst

# gets index of timeline
# input: project [item], tl_name [str]
# output: i [int]
def tl_idx(proj, tl_name):

	for i in range(1,proj.GetTimelineCount()+1):
		name = proj.GetTimelineByIndex(i).GetName()
		if name == tl_name:
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

	# if there are no duplicates return the list as is
	if len(set(names)) == len(names):
		return names
	
	dups = Counter(names) # creates a dictionary of all names with how many times they occur
	idx_names = list(enumerate(names)) # lst with index of each item
	
	for i in dups: # for every item
		if dups[i] > 1: # if there are multiple
			# get their indexes as a list
			indexes = []
			for x in idx_names:
				if x[1] == i:
					indexes.append(x[0])
			# now add a number to the end of each name with padding
			for num in range(dups[i]):
				padded_num = str(num).zfill(len(str(dups[i])))
				if num > 0:
					names[indexes[num]] = str(i) + "_" + str(padded_num)

	return names

# this will create render projects and start rendering
# input: project, timeline, markers, all_markers, path, filenames
# output: none
def export(proj, tl, in_points, out_points, path, filenames):

	proj.SetCurrentTimeline(tl)
	proj.LoadRenderPreset(itm["render_preset"].CurrentText) # set preset for render
	counter = 0 # used in for loop for file names

	# for every clip name
	for name in filenames:
		in_point = in_points[counter]
		out_point = out_points[counter] - 1

		if name == '':
			name = 'source name'

		# set settings to selected by user
		proj.SetRenderSettings({"MarkIn": in_point, "MarkOut": out_point, "TargetDir": path, "CustomName": name})
		proj.AddRenderJob() # adds render job
		counter += 1


def _main(ev):

	# gets all the details down to the clip
	global resolve
	global itm
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	timeline = project.GetTimelineByIndex(tl_idx(project, itm["tl_preset"].CurrentText))
	# clip = timeline.GetCurrentVideoItem()		
	
	# get path to export to
	path = itm["export_path"].Text
	# get file names, ins, and outs
	clip_names, in_points, out_points = source_names(timeline)
	# adds _## to duplicates
	clip_names = dup_fix(clip_names)
	print(clip_names)
	# start exporting
	export(project, timeline, in_points, out_points, path, clip_names)

################################################################################################
# GUI Elements #
# manipulations
itm["render_preset"].AddItems(preset_lst(project)) # adds list of render presets to dropdown
itm["tl_preset"].AddItems(tl_lst(project)) # adds list of timelines to dropdown
# button presses
window.On.Export.Clicked = _main
window.On.export_location.Clicked = _file_browser
window.On.ICEWin.Close = _close
# window loops
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################

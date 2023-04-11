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
			# Timeline selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "tl_label","Text": "What timeline should I used?", "Weight": 4}),
				ui.ComboBox({"ID": "tl_combobox", "Weight": 3})
			]),
			# File name selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "name_label","Text": "What should the file be named?", "Weight": 3}),
				ui.LineEdit({"ID": "name_edit", "Text": "Notes_" + str(timeline.GetName()), "Weight": 4})
			]),
			# Export to text
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "export_label","Text": "Export to:", "Weight": 1}),				
				ui.Label({"ID": "export_path","Text": "Please select a folder", "Weight": 4}),
				ui.Button({"ID": "export_path_button","Text":"Select Export Location", "Weight": 1})
			]),
			# button for export
			ui.Button({"ID": "Create", "Text": "Create .txt", "Weight": 0})
			]) 
		]
	return window



################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Marker Note Exporter",
			"ID": "MNEWin", 
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

# converts frame number to timecode
# input: frame [int], timeline [item]
# output: TC [str ##:##:##:##]
def frameToTC(frame, tl):

	start = int(tl.GetStartFrame()) # get start frame offset
	frame += start # offset by frame count because it normally starts at 0
	fps = int(round(float(tl.GetSetting('timelineFrameRate'))))
	timecode = []	
	
	timecode.append(str(frame // (3600 * fps)).rjust(2, '0')) # hours 
	frame = frame % (3600 * fps) # remove the hours from frame
	timecode.append(str(frame // (60 * fps)).rjust(2, '0')) # mins
	frame = frame % (60 * fps) # remove the mins from frame
	timecode.append(str(frame // fps).rjust(2, '0')) # secs
	frame = frame % fps
	timecode.append(str(frame).rjust(2, '0')) #frames	

	tc_str = ':'.join(timecode)

	return tc_str

# finds the largest name in the markers and returns that length + 4
# input: markers {dict}
# output: nameLen + 4 [int]
def maxLen(markers):

	nameLen = 8

	for i in markers:
		if nameLen < len(markers[i]['name']):
			nameLen = len(markers[i]['name'])

	print(nameLen + 4)
	return (nameLen + 4)
	

# Creates a text file with marker info
# input: path [str], name [str], timeline [item]
# output: none
def create_txt(path, name, tl):

	path = str(path) + str(name)	# combined path and name for open()
	textFile = open(path, 'w')	# create the text file
	markers = tl.GetMarkers()
	
	color = itm["marker_color"].CurrentText	# color is selected from current text
	
	nameLen = maxLen(markers)	# find longest name

	# add header to .txt
	textFile.write('-' * 75 + '\n')
	textFile.write('Timecode' + (' ' * 8) + 'Name' + (' ' * (nameLen-4)) + 'Note\n')
	textFile.write('-' * 75 + '\n')

	for i in sorted(markers):
		if color == "All":
			timecode = frameToTC(int(i), tl) # get timecode as str
			textFile.write('{0: <16}{1: <{2}}{3: <10}'.format(timecode, markers[i]['name'].strip(), nameLen, markers[i]["note"].strip())) # type it out formatted
			textFile.write('\n')
		else: # if there is only one color chosen
			if color == markers[i]['color']:
				timecode = frameToTC(int(i), tl) # get timecode as str
				textFile.write('{0: <16}{1: <{2}}{3: <10}'.format(timecode, markers[i]['name'].strip(), nameLen, markers[i]["note"].strip())) # type it out formatted
				textFile.write('\n')
# needed to close window
def _close(ev):
	disp.ExitLoop()

# opens file browser and stores as text on ui
def _file_browser(ev):
	location = fu.RequestDir()
	itm["export_path"].Text = str(location) 

def _main(ev):

	# gets all the details down to the clip
	global resolve
	global itm
	projectManager = resolve.GetProjectManager()
	project = projectManager.GetCurrentProject()
	timeline = project.GetTimelineByIndex(tl_idx(project, itm["tl_combobox"].CurrentText))	

	create_txt(itm["export_path"].Text, str(itm["name_edit"].Text) + '.txt', timeline) # path, name, timeline

	disp.ExitLoop()

################################################################################################
# GUI Elements #
# manipulations
itm['marker_color'].AddItems(color_lst) # adds items to dropdown
itm["tl_combobox"].AddItems(tl_lst(project)) # adds list of timelines to dropdown
# button presses
window.On.Create.Clicked = _main
window.On.export_path_button.Clicked = _file_browser
window.On.MNEWin.Close = _close
# window loops
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################

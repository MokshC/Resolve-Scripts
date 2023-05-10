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
color_lst = ['All','Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']

def splash1_ui():

	# vertical group
	window = [ui.VGroup({"Spacing": 20,},[
			ui.Label({"ID": "splash1_label","Text": "Please open all projects to search in read only mode, then open the project with the recap timeline.", "Weight": 1}),
			ui.HGap(),
			# button for renumber
			ui.Button({"ID": "splash1", "Text": "Done!", "Weight": 1})
			])	
		]
	return window

def main_ui():

	# vertical group
	window = [ui.VGroup({"Spacing": 10,},[			
			
			# Recap Timeline Selection
			ui.HGroup({"Spacing": 1}, [
				ui.Label({"ID": "tl_preset_label","Text": "Please select recap timeline", "Weight": 4}),
				ui.ComboBox({"ID": "tl_preset", "Weight": 3})
			]),
			
			# Timeline to trace from label
			ui.HGroup({"Spacing": 1}, [
				ui.VGap(),
				ui.Label({"ID": "tl_label","Text": "What timeline should I search?", "Weight": 1}),
				ui.VGap()
			]),

			# browser for projects and timelines
			ui.HGroup({"Spacing": 0, "Weight": 10}, [
				ui.Tree({"ID": "proj_browser", 'SortingEnabled': 'true', 'SelectionMode': 'ExtendedSelection', 
					'Events': {'ItemDoubleClicked': True, 'ItemClicked': True}, "Weight": 10}),
				ui.Tree({"ID": "tl_browser", 'SortingEnabled': 'true', 'SelectionMode': 'ExtendedSelection', 
					'Events': {'ItemDoubleClicked': True, 'ItemClicked': True}, "Weight": 10}),
			]),
			
			
			ui.HGap(),
			
			# Exact match checkbox
			ui.HGroup({}, [
				ui.VGap(),
				ui.CheckBox({"ID": "exact_check","Text": "Exact Matches Only", "Checked": True, "Weight": 1}),
				ui.VGap()
			]),

			# Export button
			ui.HGroup({}, [
				ui.VGap(),
				ui.Button({"ID": "Export", "Text": "Grab Stills", "Weight": 1}),
				ui.VGap()
			]),
		])]

	return window


def splash2_ui():

	# vertical group
	window = [ui.VGroup({"Spacing": 20,},[
			ui.Label({"ID": "splash2_label","Text": "Please open the powergrade album that still will be grabbed to.", "Weight": 1}),
			ui.HGap(),
			# button for renumber
			ui.Button({"ID": "splash2", "Text": "Done!", "Weight": 1})
			])	
		]
	return window

################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# splash1 definition
splash1 = disp.AddWindow({"WindowTitle": "Moksh's Recap Trace Assist",
			"ID": "S1Win", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [100,700,600,100], # x-position, y-position, width, height
			}, 
			splash1_ui())


splash1itm = splash1.GetItems() # Grabs all UI elements to be manipulated

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's Recap Trace Assist",
			"ID": "ARTWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [100,700,700,500], # x-position, y-position, width, height
			}, 
			main_ui())


itm = window.GetItems() # Grabs all UI elements to be manipulated

# splash2 definition
splash2 = disp.AddWindow({"WindowTitle": "Moksh's Recap Trace Assist",
			"ID": "S2Win", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [100,700,600,100], # x-position, y-position, width, height
			}, 
			splash2_ui())


splash2itm = splash2.GetItems() # Grabs all UI elements to be manipulated


checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in window.WindowTitle) else sys.exit()


################################################################################################
# Functions #
#############

# builds out both trees for project and timelines
def treeBuild():

	# proj tree building
	header = itm['proj_browser'].NewItem() # creating the header for the tree
	header.Text[0] = 'Projects' # first column
	itm['proj_browser'].SetHeaderItem(header) # add header
	itm['proj_browser'].ColumnCount = 1 # adding columns to tree
	itm['proj_browser'].ColumnWidth[0] = 300 # setting column width

	# get list of projects
	projectManager.GotoRootFolder() # Goes to root in project manager 
	projLst = projectManager.GetProjectListInCurrentFolder() # gets all the projects listed

	# add all projects to proj tree
	for i in sorted(projLst):
		newRow = itm['proj_browser'].NewItem() # creates a new item
		newRow.Text[0] = str(i) # adds text to it
		itm['proj_browser'].AddTopLevelItem(newRow) # adds it to the tree

	# tl tree building
	header = itm['tl_browser'].NewItem() # creating the header for the tree
	header.Text[0] = 'Timelines' # first column
	itm['tl_browser'].SetHeaderItem(header) # add header
	itm['tl_browser'].ColumnCount = 1 # adding columns to tree
	itm['tl_browser'].ColumnWidth[0] = 300 # setting column width

# creates list of all timelines in project, and sets current timeline as Default
# input: project [item]
# output: tl_lst [list]
def tl_lst(proj):
	
	tl_lst = [] # placeholder will be filled

	# gets every tl name in project and appends to lst
	for i in range(1,proj.GetTimelineCount()+1):
		name = proj.GetTimelineByIndex(i).GetName()
		tl_lst.append(name)
		
	tl_lst = sorted(tl_lst) # sorts list

	return tl_lst # return the list

# gets index of timeline
# input: project [item], tl_name [str]
# output: i [int]
def tl_idx(proj, tl_name):

	for i in range(1,proj.GetTimelineCount()+1):
		name = proj.GetTimelineByIndex(i).GetName()
		if name == tl_name:
			return int(i)

# needed to close window
def _close(ev):
	disp.ExitLoop()

# Gets currently selected project
# input: none
# output: project [item]
def getProj():

	selectedItm = itm['proj_browser'].SelectedItems() # get selected project (its a dictionary with key: 1)
	projName = selectedItm[1].Text[0] # get project name (key 1, item 0)

	projectManager.LoadProject(projName) # Load into the project
	proj = projectManager.GetCurrentProject() # get project

	return proj

# fill lst with all clips in given timeline
# input: tl [item]
# output: clip_lst [lst of items]
def getClips(tl):

	clip_lst = [] # list tp be filled

	# for every video track get every clip and add to list
	for i in range(1, tl.GetTrackCount("video")+1):
		clip_lst.extend(tl.GetItemListInTrack("video",i))

	return clip_lst

# returns list of all indecies of an item in a list
# input: idxlst [lst], item [anything that can be in a list]
# output: indices [lst] 
def indexAll(idxlst, item):

	indicies = []
	for i in range(len(idxlst)):
		if item.strip() == idxlst[i].strip():
			indicies.append(i)

	return indicies

# checks if a var's frame in other var
# input: var [lst in form [int, int]], searchVar [lst in form [int, int]]
# output: True or False [bool]
def frameInRange(var, searchVar):

	# just checks if start frame and end frame in between searchVar frames, or if searchVar is inside var
	if (var[0] >= searchVar[0]) and (var[0] <= searchVar[1]):
		return True
	elif (var[1] >= searchVar[0]) and (var[1] <= searchVar[1]):
		return True
	elif ((searchVar[0] >= var[0]) and (searchVar[0] <= var[1]) and (searchVar[1] >= var[0]) and (searchVar[1] <= var[1])):
		return True
	return False

# returns list of all indecies of an item in a list
# input: idxlst [lst], item [lst in form [str,int,int]]
# output: indices [lst] 
def indexVars(exactVars, var):

	indicies = []
	for i in range(len(exactVars)):
		if (var[0].strip() == exactVars[i][0].strip()) and frameInRange(var[1:3], exactVars[i][1:3]):
			indicies.append(i)

	return indicies

# gets list of all TCs where clips are found in given timeline
# input: clips [lst of clip items], tl [timeline item]
# output: tcLst [lst of TCs]
def getTCs(recapClips, tl):

	searchClips = getClips(tl) # get all clips from search timeline

	# get info of every clip we are searching
	reelNames = []
	exactVars = []
	# get reel name of every clip being searched in timeline
	# gets name, start, and end of each as well for if exact is checked
	for clip in searchClips:
		try:
			item = clip.GetMediaPoolItem()
			reelName = item.GetClipProperty('Reel Name')
			exactVar = [item.GetClipProperty('File Name'), int(item.GetClipProperty('Start')) + int(clip.GetLeftOffset()), int(item.GetClipProperty('Start')) + int(clip.GetRightOffset())]
		except:
			reelName = clip.GetName()
			exactVar = ['', -1, -1]

		# if statement to remove framcounts
		if ('.[' in exactVar[0]):
			exactVar[0] = exactVar[0][:exactVar[0].rfind('.[')] # remove framcount and add
		elif ('_[' in exactVar[0]):
			exactVar[0] = exactVar[0][:exactVar[0].rfind('_[')] # remove frame count and add

		reelNames.append(reelName) # add reel name to list of every clip in timeline
		exactVars.append(exactVar) # add vars to list of every clip in timeline

	tcLst = [] # placeholder
	# for every recap clip, search the timeline for clips of the same name and record the timecode
	for i in range(len(recapClips)):
		clip = recapClips[i] # get clip item 
		# get name of clip
		try:
			item = clip.GetMediaPoolItem()
			name = item.GetClipProperty('Reel Name')
			var = [item.GetClipProperty('File Name'), int(item.GetClipProperty('Start')) + int(clip.GetLeftOffset()), int(item.GetClipProperty('Start')) + int(clip.GetRightOffset())]
		except:
			name = clip.GetName()
			var = ['', 0, 0]

		# if statement to remove framcounts
		if ('.[' in var[0]):
			var[0] = var[0][:var[0].rfind('.[')] # remove framcount
		elif ('_[' in var[0]):
			var[0] = var[0][:var[0].rfind('_[')] # remove framcount

		# if exact clips only checkbox checked
		if itm['exact_check'].Checked:

			# if the var is found grab TCs, add it to list
			varidx = indexVars(exactVars, var) # finds every occurance of var
			idxLen = len(varidx)
			if idxLen >= 1: # if there are occurances of the var collect TCs
				for i in varidx:

					# this if statement tries to find exact frame, if it fails still will not be grabbed
					mediaStart = int(searchClips[i].GetMediaPoolItem().GetClipProperty('Start')) + int(searchClips[i].GetLeftOffset())	# starting frame of searchclip
					mediaEnd = int(searchClips[i].GetMediaPoolItem().GetClipProperty('End')) + int(searchClips[i].GetRightOffset())	# ending frame of searchclip

					if var[1] == mediaStart:	# if ther are the same then just assign it
						tc = searchClips[i].GetStart()
					elif (var[1] > mediaStart) and (var[1] <= mediaEnd):	# if the start frame of the recap is inside the main timeline, grab at that point
						tc = int(searchClips[i].GetStart()) + (var[1] - mediaStart)
					else:	# else do not grab
						tc = '' 	# placeholder

					if (tc not in tcLst) and (tc != ''): # if we already collected the TC ignore it
						tcLst.append(tc)
		else:
			# if the name is found grab TCs, add it to list
			nameidx = indexAll(reelNames, name) # finds every occurance of name
			idxLen = len(nameidx)
			if idxLen >= 1: # if there are occurances of the name collect TCs
				for i in nameidx:
					tc = searchClips[i].GetStart()
					if tc not in tcLst: # if we already collected the TC ignore it
						tcLst.append(tc)

	print(sorted(tcLst))

	return sorted(tcLst)

# converts frame number to timecode
# input: frame [int], timeline [item]
# output: TC [str ##:##:##:##]
def frameToTC(frame, tl):

	# start = int(tl.GetStartFrame()) # get start frame offset
	# frame += start # offset by frame count because it normally starts at 0
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

# grabs stills
# input: tcs [lst], path [str], tl [timeline item]
# output: stills
def exportStills(tcs, tl):

	for tc in sorted(tcs):
		tc_str = frameToTC(tc, tl)
		tl.SetCurrentTimecode(tc_str)
		tl.GrabStill()

	
# Fills tl broser tree with all the timeslines of selected project
def _tl_fill(ev):

	itm["tl_browser"].Clear() # clear the browser to fill it again
	proj = getProj() # get the selected project
	tlLst = tl_lst(proj) # get list of all timelines in project

	# fill the tree with timelines
	for i in sorted(tlLst):
		newRow = itm['tl_browser'].NewItem() # creates a new item
		newRow.Text[0] = str(i) # adds text to it
		itm['tl_browser'].AddTopLevelItem(newRow) # adds it to the tree

def main():

	if "Moksh" not in window.WindowTitle:
		sys.exit()
	# Get information from the UI
	recapTL = origProj.GetTimelineByIndex(tl_idx(origProj, itm["tl_preset"].CurrentText)) # get timeline selected in dropdown
	recapClips = getClips(recapTL) # get all clips in recapTL
	# The steps below are to double check what should already be done in getProj()
	searchProj = (itm['proj_browser'].SelectedItems()) # get selected project from UI (its a dictionary with key: 1)
	projectManager.LoadProject(searchProj[1].Text[0]) # Load into the project by name
	searchProj = projectManager.GetCurrentProject() # set searchProj to project item of current project
	searchTL = searchProj.GetTimelineByIndex(tl_idx(searchProj, itm["tl_browser"].SelectedItems()[1].Text[0])) # get timeline selected in dropdown

	searchProj.SetCurrentTimeline(searchTL) # set current timeline to what should be searched
	tcLst = getTCs(recapClips, searchTL) # gets list of all TCs where recap clips are found
	exportStills(tcLst, searchTL) # both creates txt with TCs and exports stills there

def _mainWin(ev):
	if "Moksh" not in window.WindowTitle:
		sys.exit()
	splash1.Hide()
	disp.ExitLoop()
	itm["tl_preset"].AddItems(tl_lst(projectManager.GetCurrentProject())) # adds list of timelines to dropdown
	global origProj # setting global variable
	origProj = projectManager.GetCurrentProject()
	window.Show()
	disp.RunLoop()
	window.Hide()

def _splash2Win(ev):
	window.Hide()
	disp.ExitLoop()
	splash2.Show()
	disp.RunLoop()
	splash2.Hide()

def _mainWin2(ev):
	splash2.Hide()
	disp.ExitLoop()

	main()

	window.Show()
	disp.RunLoop()
	
	window.Hide()
################################################################################################
# GUI Elements #
# manipulations

treeBuild() # builds tree	
# button presses
splash1.On.splash1.Clicked = _mainWin
splash1.On.S1Win.Close = _close
window.On.Export.Clicked = _splash2Win
window.On.ARTWin.Close = _close
window.On.proj_browser.ItemDoubleClicked = _tl_fill
splash2.On.splash2.Clicked = _mainWin2
splash2.On.S2Win.Close = _close
# window loops
splash1.Show()
disp.RunLoop()
splash1.Hide()
#################################################################################################

# Moksh
# -*- coding: utf-8 -*-

import sys
import os

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
filePath = "/"

# UI for done window
def doneUI():
	# vertical group
	window = [ui.VGroup({"Spacing": 10,},[
			ui.Label({"ID": "done_label","Text": "EDL Created!\nPlease see the same path as the original EDL.", "Weight": 1})
			])
		]
	return window

def main_ui():
	# vertical group
	window = [ui.VGroup({"Spacing": 10,},[
			# horizontal groups
			# EDL Path collection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "path_label","Text": "EDL:", "Weight": 1}),				
				ui.Label({"ID": "EDL_path","Text": "", "Weight": 4}),
				ui.Button({"ID": "path_button","Text":"Select EDL", "Weight": 1})
			]),
			# Timeline selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "tl_label","Text": "What timeline is it referencing?", "Weight": 4}),
				ui.ComboBox({"ID": "tl_combobox", "Weight": 3})
			]),
			# Track selection
			ui.HGroup({"Spacing": 1,}, [ 	
				ui.Label({"ID": "track_label","Text": "What track is it referencing?", "Weight": 4}),
				ui.ComboBox({"ID": "track_combobox", "Weight": 3}),
				ui.VGap(),
				ui.Button({"ID": "refresh_button","Text":"Refresh Tracklist", "Weight": 2})
			]),
			# EDL Edit Checkboxes
			ui.HGap(),
			ui.HGroup({"Spacing": 1,}, [
				ui.Label({"ID": "checkbox_label","Text": "What should be added to the EDL?", "Weight": 1}),
				ui.VGap(),
				ui.HGroup({"Spacing": 10,},[
					ui.VGroup({"Spacing": 1,}, [
						ui.CheckBox({"ID": "camera_checkbox","Text": "Camera", "Checked": False, "Weight": 1}),
						ui.CheckBox({"ID": "clipmarker_checkbox","Text": "Clip Markers", "Checked": True, "Weight": 1}),
						ui.CheckBox({"ID": "transform_checkbox","Text": "Clip Transform", "Checked": False, "Weight": 1}),
						ui.CheckBox({"ID": "path_checkbox","Text": "File Path", "Checked": False, "Weight": 1}),
						
					]),
					ui.VGroup({"Spacing": 1,}, [
						ui.CheckBox({"ID": "colorspace_checkbox","Text": "Input Color Space", "Checked": False, "Weight": 1}),
						ui.CheckBox({"ID": "lut_checkbox","Text": "Input LUT", "Checked": False, "Weight": 1}),	
						ui.CheckBox({"ID": "sizing_checkbox","Text": "Input Sizing Preset", "Checked": False, "Weight": 1}),
						ui.CheckBox({"ID": "par_checkbox","Text": "PAR", "Checked": False, "Weight": 1}),
					]),
					ui.VGroup({"Spacing": 1,}, [
						ui.CheckBox({"ID": "resolution_checkbox","Text": "Source Resolution", "Checked": False, "Weight": 1}),
						ui.CheckBox({"ID": "tlmarker_checkbox","Text": "Timeline Markers", "Checked": False, "Weight": 1}),
						ui.CheckBox({"ID": "tlres_checkbox","Text": "Timeline Resolution", "Checked": False, "Weight": 1}),						
					]),	
				]),
			]),
			ui.HGap(),
			# button for export
			ui.Button({"ID": "edit_button", "Text": "Add to EDL!", "Weight": 0})
			]) 
		]
	return window



################################################################################################
# Window creation #
###################

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?

# window definition
window = disp.AddWindow({"WindowTitle": "Moksh's EDL Toolbox",
			"ID": "EDLkit", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [50,800,700,300], # x-position, y-position, width, height
			}, 
			main_ui())

doneWindow = disp.AddWindow({"WindowTitle": "Moksh's EDL Toolkit",
			"ID": "EDLdone", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [50,800,350,70], # x-position, y-position, width, height
			}, 
			doneUI())


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

# creates list of all video tracks in timeline
# input: timeline [item]
# output: tracks [list]
def track_lst(tl):

	print("Creating Track List")

	tracks = []	# placeholder
	for i in range(1, tl.GetTrackCount("video")+1):	# for every track adds "V#" to list
		tracks.append("V" + str(i))

	print(tracks)

	return tracks 	# returns list

# checks if EDL line starts with cut number (like ###)
# input: line [str]
# output: True or False [bool]
def numline(line):

	for char in line[:3]:	# for the first 3 characters
		if (ord(char) < 48) or (ord(char) > 57):	# if they don't land between '0' and '9' return false
			return False
		return True	# return true

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

# converts timecode to frame number
# input: tc [str], timeline [item]
# output: frame [int]
def tcToFrame(tc, tl):

	fps = int(round(float(tl.GetSetting('timelineFrameRate'))))	# get framerate of timeline
	tclst = list(map(int, tc.split(':')))	# turn tc into list of int values

	# quick math to convert each section of list to frames and sum them	
	frame = tclst[3]
	frame += fps * tclst[2]
	frame += 60 * fps * tclst[1]
	frame += 3600 * fps * tclst[0]

	return frame


# checks if timecode is in record timecode of a line of EDL
# input: tc [str in ##:##:##:## format], line [str], tl [timeline item]
# output: True/False [bool]
def tcInLine(tc, line, tl):
	
	# if the timecode either matches or is within the range, return True
	if tc == line[-25:-14]:
		return True
	elif (tcToFrame(tc, tl) >= tcToFrame(line[-25:-14], tl)) and (tcToFrame(tc, tl) < tcToFrame(line[-13:-2], tl)):
		return True
	# else return false
	return False


# finds clip in clips list and returns clip
# input: guess [clip item], clips [lst of clips], line [str], edl [lst of str]m tl [timeline item] 
# output: clip [clip]
def clipFind(guess, clips, line, edl, tl):

	# if the tc of guess is correct just return the guess
	if tcInLine(frameToTC(guess.GetStart(), tl), line, tl):
		return guess

	idx = clips.index(guess)	# where is the guess clip
	
	# middle out search starting at guess clip
	dist = max(len(clips)-idx, idx) 	# maximum travel from guess to edge of clips
	for x in range(dist):

		if (idx + x < len(clips)) and (idx - x - 1 > -1):	# search both ways if neither direction is outside list, and return if TC found in line
			if tcInLine(frameToTC(clips[idx - x - 1].GetStart(), tl), line, tl):
				return clips[idx - x - 1]
			elif tcInLine(frameToTC(clips[idx + x].GetStart(), tl), line, tl):
				return clips[idx + x]
		elif (idx + x >= len(clips)) and (idx - x - 1 > -1):	# search only backwards if forwards is outside range, return if TC found in line
			if tcInLine(frameToTC(clips[idx - x - 1].GetStart(), tl), line, tl):
				return clips[idx - x - 1]
		else:	# search only forwards, if TC found in line return it
			if tcInLine(frameToTC(clips[idx + x].GetStart(), tl), line, tl):
				return clips[idx + x]

	# if nothing is found simply return guess and hope
	return guess

# needed to close window
def _close(ev):
	disp.ExitLoop()

# refreshes track list when new tl selected
def _new_tracks(ev):

	global timeline
	timeline = project.GetTimelineByIndex(tl_idx(project, itm["tl_combobox"].CurrentText))
	itm["track_combobox"].Clear()
	itm["track_combobox"].AddItems(track_lst(timeline))

# opens file browser and stores as global variable filePath
def _file_browser(ev):
	global filePath
	filePath = fu.RequestFile()

	# this if statement avoids errors from different operating systems
	if sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
		itm["EDL_path"].Text = str(filePath[filePath.rfind('/')+1:])
	else:
		itm["EDL_path"].Text = str(filePath[filePath.rfind('\\')+1:])


# adds clip markers to EDL as locators
# input: currentClip [item], timeline [item], newf [file with write permission]
# output: none
def addClipMark(currentClip, timeline, newf):
	markers = currentClip.GetMarkers()	# get markers from current clip
	for i in sorted(markers):	# for each marker
		frame = int(currentClip.GetStart()) + int(i) - int(currentClip.GetLeftOffset())	# get frame
		color = markers[i]['color'].upper()	# get color
		comment = markers[i]['name'] + " - " + markers[i]['note']	# get comment 
		newf.write('{0} {1} {2: <8}{3}\n'.format('*LOC:', frameToTC(frame, timeline), color, comment))	# write it out in Avid's locator format

# adds timeline markers to EDL as locators
# input: markers [dict], tl [item], clip [item], newf [file with write permission]
# output: markers [dict]
def addTLMark(markers, tl, clip, newf):
	
	# get clip in and out
	start = clip.GetStart()
	end = clip.GetEnd()

	# for each marker on the timeline, check if it is in clip range and write it
	for mark in sorted(markers):

		frame = int(tl.GetStartFrame()) + int(mark)	# get start frame of marker

		if (frame >= start) and (frame < end):	# check if frame is inbetween in and out
			color = markers[mark]['color']
			comment = markers[mark]['name'] + ' - ' + markers[mark]['note']
			newf.write('{0} {1} {2: <8}{3}\n'.format('*LOC:', frameToTC(frame, tl), color, comment))	# write it out in Avid's locator format	
			markers.pop(mark)	# gets rid of mark so you don't need to double hit it in for loop 
	
	return markers	# will update markers for rerun of this script, so it will search less

# adds input color space to EDL, if there is one
# input: media [item], newf [file with write permission]
# output: none
def addCS(media, newf):

	colorspace = media.GetClipProperty('Input Color Space')	# get color space
	# if it has a color space write that line
	if colorspace != '':
		newf.write('{0} {1}\n'.format('* Input Color Space:', colorspace))
	
# adds input LUT to EDL, if there is one
# input: media [item], newf [file with write permission]
# output: none
def addLUT(media, newf):

	lut = media.GetClipProperty('Input LUT')	# get input LUT

	# if it has a LUT write that line
	if lut != '':
		newf.write('{0} {1}\n'.format('* Input LUT:', lut))

# adds input sizing to EDL
# input: media [item], newf [file with write permission]
# output: none
def addInSizing(media, newf):

	sizing = media.GetClipProperty('Input Sizing Preset')	# get input sizing

	# if it has a sizing write that line
	if sizing != '' and sizing != 'None':
		newf.write('{0} {1}\n'.format('* Input Sizing Preset:', sizing))

# adds PAR (pixel aspect ratio) to EDL
# input: media [item], newf [file with write permission]
# output: none
def addPar(media, newf):

	par = media.GetClipProperty('PAR')	# get PAR

	# if it has a PAR write that line
	if par != '':
		newf.write('{0} {1}\n'.format('* PAR:', par))

# adds file path to EDL
# input: media [item], newf [file with write permission]
# output: none
def addPath(media, newf):

	path = media.GetClipProperty('File Path')	# get file path

	# if it has a path write that line
	if path != '':
		newf.write('{0} {1}\n'.format('* File Path:', path))

# adds clip transform information to EDL
# input: clip [item], newf [file with write permission]
# output: none
def addTrans(clip, newf):

	transform = clip.GetProperty()	# get transform info

	# if it has transform information write it
	if transform != {}:
		newf.write('{0} {1}\n'.format('* Clip Transform:', transform))


# adds camera information to EDL
# input: media [item], newf [file with write permission]
# output: none
def addCam(media, newf):

	try:
		cam = media.GetMetadata('Camera Type')	# get camera

		# if it has a cam write that line
		if cam != '':
			newf.write('{0} {1}\n'.format('* Camera:', cam))
	except:
		pass

# adds source resolution to EDL
# input: clip [item], newf [file with write permission]
# output: none
def addRes(media, newf):

	res = media.GetClipProperty('Resolution')	# get file path

	# if it has a res write that line
	if res != '':
		newf.write('{0} {1}\n'.format('* Source Resolution:', res))

# adds timeline resolution to tail to EDL
# input: tl [item], newf [file with write permissions]
# output: none
def addTLRes(tl, newf):

	width = tl.GetSetting('timelineResolutionWidth')	# get width
	height = tl.GetSetting('timelineResolutionHeight')	# get height
	res = width + 'x' + height				# organize them

	# if it has a res write that line
	if res != 'x':
		newf.write('{0} {1}\n'.format('* Timeline Resolution:', res))

# opens EDL completed window
def doneWin():
	doneWindow.Show()
	disp.RunLoop()
	doneWindow.Hide()

# adds checked off items to EDL
# input: none
# output: none
def _main(ev):

	itm['edit_button'].Enabled = False # you can't press the button now

	global timeline	# now this function will change the global timeline variable

	# File operations
	f = open(filePath, "r")	# open EDL at path
	edl = f.readlines()	# get EDL lines

	if itm['tlres_checkbox'].Checked:	# if timeline metadata needs to be added adjust end of EDL by removing \n
		while edl[-1] == '\n':
			edl = edl[:-1]

	# this if statement avoids errors from different operating systems
	if sys.platform.startswith("darwin") or sys.platform.startswith("linux"):
		os.rename(filePath, filePath[:filePath.rfind('/')+1] + 'old_' + itm["EDL_path"].Text)	# rename old edl to old_[edl name]
	else:
		os.rename(filePath, filePath[:filePath.rfind('/')+1] + 'old_' + itm["EDL_path"].Text)	# rename old edl to old_[edl name]
		
	newf = open(filePath, "w")	# write EDL path

	# Collecting information
	timeline = project.GetTimelineByIndex(tl_idx(project, itm["tl_combobox"].CurrentText)) 	# Get timeline from dropdown
	track = int((itm["track_combobox"].CurrentText)[1:])	# Get track number
	clips = timeline.GetItemListInTrack('video', track)	# get clips on track
	tlMarkers = timeline.GetMarkers()	# get all timeline markers

	# adding lines to new edl
	currentClip = clips[0]	# keep count of clip alongside EDL
		
	y = 0	# placeholder for while statement
	total = len(edl)
	while y < total:	# this while statement will go through every line of the EDL
		itm['edit_button'].Text = "{:.2%}".format(float(y)/float(total)) # loading counter going up
		line = edl[y]	# get current line
		newf.write(line)	# always write a line

		# now write all the comments if it is a clip line
		if numline(line):
			# write everything after the already exisitng information on EDL (like clipname)
			while (y+1 != total) and (numline(edl[y+1]) == False):	
				newf.write(edl[y+1])
				y += 1

			currentClip = clips[int(line[:3]) - 1]	# guess for what the current clip in the edl is referencing on the TL
			currentClip = clipFind(currentClip, clips, line, edl, timeline)	# checks if guess is correct (middle out)

			# if clipmarkers are selected, add clip markers in EDL
			if itm["clipmarker_checkbox"].Checked:
				addClipMark(currentClip, timeline, newf)

			# if tl markers are selected, add them to EDL
			if itm["tlmarker_checkbox"].Checked:
				tlMarkers = addTLMark(tlMarkers, timeline, currentClip, newf)

			# if clip transform checked, add to EDL
			if itm["transform_checkbox"].Checked:
				addTrans(currentClip, newf)

			try:
				media = currentClip.GetMediaPoolItem()

				# if input color space selected, add to EDL
				if itm["colorspace_checkbox"].Checked:
					addCS(media, newf)
	
				# if input LUT checked, add to EDL
				if itm["lut_checkbox"].Checked:
					addLUT(media, newf)
	
				# if input sizing checked, add to EDL
				if itm["sizing_checkbox"].Checked:
					addInSizing(media, newf)
				
				# if camera checked, add to EDL
				if itm["camera_checkbox"].Checked:	
					addCam(media, newf)
				
				# if camera checked, add to EDL
				if itm["resolution_checkbox"].Checked:
					addRes(media, newf)

				# if PAR checked, add to EDL
				if itm["par_checkbox"].Checked:
					addPar(media, newf)
	
				# if path checked, add to EDL
				if itm["path_checkbox"].Checked:
					addPath(media, newf)

			except:
				pass

		y += 1	# keeps the while loop moving

	# add timeline metadata section at bottom
	itm['edit_button'].Text = "Adding Timeline Metadata"
	if itm['tlres_checkbox'].Checked:
		newf.write('*\n* ============================================================\n')
		newf.write('* Timeline Metadata\n* ------------------------------------------------------------\n* \n')
		addTLRes(timeline, newf)

	itm['edit_button'].Text = "Add to EDL again!" # button text reset
	itm['edit_button'].Enabled = True # you can press the button now
	# doneWin()
	# disp.ExitLoop()

################################################################################################
# GUI Elements #
# manipulations
itm["tl_combobox"].AddItems(tl_lst(project)) # adds list of timelines to dropdown
itm["track_combobox"].AddItems(['V1']) # adds list of timelines to dropdown
# button presses
window.On.edit_button.Clicked = _main
window.On.path_button.Clicked = _file_browser
window.On.refresh_button.Clicked = _new_tracks
window.On.EDLkit.Close = _close
doneWindow.On.EDLdone.Close = _close
# window loops
window.Show()
disp.RunLoop()
window.Hide()
#################################################################################################
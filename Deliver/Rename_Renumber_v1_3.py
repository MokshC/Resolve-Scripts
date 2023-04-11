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
color_lst = ['All','Blue','Cyan','Green','Yellow','Red','Pink','Purple','Fuchsia','Rose','Lavender','Sky','Mint','Lemon','Sand','Cocoa','Cream']


################################################################################################
# Window creation #
###################

########
#  UI  #
########
# UI for splash window
def splashUI():
	# vertical group
	window = [ui.VGroup({"Spacing": 20,},[
			# button for rename
			ui.Button({"ID": "Name", "Text": "Rename", "Weight": 10}),
			# button for renumber
			ui.Button({"ID": "Number", "Text": "Renumber", "Weight": 10})
			])	
		]
	return window

# UI for rename window
def nameUI():
	# vertical group
	window = [ui.VGroup({"Spacing": 5,},[
			# File Path Selection
			ui.HGroup({"Spacing": 2,}, [ 	
				ui.Label({"ID": "tiff_label","Text": "Rename Tiff in:", "Weight": 2}),				
				ui.Label({"ID": "tiff_path","Text": "Please select a folder", "Weight": 4}),
				ui.Button({"ID": "tiff_choose","Text":"Select Tiff Location", "Weight": 1})
			]),
			# Find Name
			ui.HGroup({"Spacing": 3,}, [ 	
				ui.Label({"ID": "name_label","Text": "Find: ", "Weight": 1}),
				ui.LineEdit({"ID": "name_edit", "Text": "", "Weight": 3})
			]),
			# Replace Name
			ui.HGroup({"Spacing": 3,}, [ 	
				ui.Label({"ID": "rename_label","Text": "Replace: ", "Weight": 1}),
				ui.LineEdit({"ID": "rename_edit", "Text": "", "Weight": 3})
			]),
			# button for renumber
			ui.HGroup({"Spacing": 3,}, [ 
				ui.HGap(),	
				ui.Button({"ID": "Rename", "Text": "Rename!", "Weight": 1}),
				ui.HGap()
			])	
		])]
	return window

# UI for renumber window
def numUI():
	# vertical group
	window = [ui.VGroup({"Spacing": 10,},[
			# File Path Selection
			ui.HGroup({"Spacing": 5,}, [ 	
				ui.Label({"ID": "tiff_label","Text": "Rename Tiff in:", "Weight": 2}),				
				ui.Label({"ID": "tiff_path","Text": "Please select a folder", "Weight": 4}),
				ui.Button({"ID": "tiff_choose","Text":"Select Tiff Location", "Weight": 1})
			]),
			# Find Numbers section
			ui.HGroup({"Spacing": 5,}, [ 	
				ui.Label({"ID": "break_label","Text": "What did you use to separate file name and frame number?", "Weight": 0}),
				ui.HGap(),
				ui.ComboBox({"ID": "break_box", "Weight": 1})
			]),
			# Replace Numbers section
			ui.HGroup({"Spacing": 5,}, [ 	
				ui.Label({"ID": "padding_label","Text": "Digits in filename: ", "Weight": 0}),
				ui.DoubleSpinBox({"ID": "padding_box", "Value": 7, "Weight": 1}),
				ui.HGap(),
				ui.Label({"ID": "start_label","Text": "Starting Frame: ", "Weight": 0}),
				ui.LineEdit({"ID": "start_edit", "Text": "86400", "Weight": 3})
			]),
			# button for renumber
			ui.HGroup({"Spacing": 5,}, [ 
				ui.HGap(),	
				ui.Button({"ID": "Renumber", "Text": "Renumber!", "Weight": 1}),
				ui.HGap()
			])	
		])]
	return window

ui = fu.UIManager # get UI utility from fusion
disp = bmd.UIDispatcher(ui) # gets display settings?


########
#Window#
########
# splash window definition
splash = disp.AddWindow({"WindowTitle": "Moksh's Batch Namer",
			"ID": "SPLWin", 
			'WindowFlags': {'Window': True,'WindowStaysOnTopHint': True},
			"Geometry": [500,500,300,150], # x-position, y-position, width, height
			}, 
			splashUI())


# window for rename
nameWindow = disp.AddWindow({"WindowTitle": "Moksh's Renamer",
				"ID": "NAMEWin",
				"WindowFlags": {'Window': True,'WindowStaysOnTopHint': True},
				"Geometry": [500,500,1000,150], # x-position, y-position, width, height
				}, 
				nameUI())

# window for renumber
numWindow = disp.AddWindow({"WindowTitle": "Moksh's Renumberer",
				"ID": "NUMWin",
				"WindowFlags": {'Window': True,'WindowStaysOnTopHint': True},
				"Geometry": [500,500,700,150], # x-position, y-position, width, height
				}, 
				numUI())

if "Moksh" not in (nameWindow.WindowTitle and numWindow.WindowTitle and splash.WindowTitle):
	sys.exit()

checksum = ''
for i in [77, 111, 107, 115, 104] : checksum += chr(i)
checksum = '' if (checksum in (nameWindow.WindowTitle and numWindow.WindowTitle and splash.WindowTitle)) else sys.exit()

################################################################################################
# Functions #
#############

# opens file browser and stores as text on ui
def _file_browser(ev):
	location = fu.RequestDir()
	# this will allow the function to work in both windows
	nameItm["tiff_path"].Text = str(location) 
	numItm["tiff_path"].Text = str(location) 

# needed to close window
def _close(ev):
	disp.ExitLoop()

# decides renumber order to not overwrite any files
# input: tiff [str]
# output: range [lst]
def orderDecide(tiff, total):

	breaker = numItm['break_box'].CurrentText # get breaker before numbers
	end = tiff.rfind('.') # this is to find extension
	name = tiff[:end] # name is tiff without the extension

	# if requested start is less than given, go forwards
	if int(numItm['start_edit'].Text) <= int(name[name.rfind(breaker)+1:]):
		print("forwards")
		return range(total)
	# else go backwards
	else:
		print("backwards")
		return range(total-1,-1,-1)

# taking in a list, returns a renumbered list
# input: 'str'
# output: 'str'
def newName(tiff):
	
	old = nameItm['name_edit'].Text.strip()
	new = nameItm['rename_edit'].Text.strip()

	return tiff.replace(old, new)

# taking in a list, returns a renamed list
# input: 'str'
# output: 'str'
def newNum(tiff, num):

	# collecting information from UI	
	breaker = numItm['break_box'].CurrentText # get breaker before numbers

	ind = tiff.rfind(breaker) + 1 # gets index of breaker 

	# if the breaker is not in the file, return original name
	if ind == 0:
		return tiff
	else:
		# This is to deal with the file extension
		end = tiff.rfind('.') # this is to find extension
		name = tiff[:end] # name is tiff without the extension
		ind = name.rfind(breaker) + 1

		return str(name[:ind]) + str(num) + str(tiff[end:])
	

# main rename function
def _rename(ev):

	path = numItm['tiff_path'].Text # gets path from UI
	files = os.listdir(path) # gets all files in path
	total = len(files) # gets total amount

	# loading button
	nameItm['Rename'].Enabled = False # you can't press the button now
	nameItm['Rename'].Text = "{:.2%}".format(0/total) # changes text to in prog
	
	print(nameItm['Rename'].Text)

	# for every file rename it!!
	for i in range(total):
		os.rename(path+files[i], path+newName(files[i])) # renaming
		nameItm['Rename'].Text = "{:.2%}".format(float(i)/float(total)) # loading counter going up

	nameItm['Rename'].Text = "Rename!"
	nameItm['Rename'].Enabled = True # let you click the button again


# main renumber function
def _renumber(ev):
	
	# collecting values from UI
	path = nameItm['tiff_path'].Text # gets path from UI
	padding = int(numItm["padding_box"].Value) # get padding from UI
	files = sorted(os.listdir(path)) # gets all files in path in order
	total = len(files) # gets total amount
	
	# loading button
	numItm['Renumber'].Enabled = False # you can't press the button now
	numItm['Renumber'].Text = "{:.2%}".format(0/total) # changes text to in prog

	rangeTotal = orderDecide(files[0], total) # decide order of rename, so not to overwrite

	# for every file renumber it!!
	for i in rangeTotal:

		number = str(int(numItm['start_edit'].Text) + i).zfill(padding) # get the number

		os.rename(path+files[i], path+newNum(files[i], number)) # renumbering
		numItm['Renumber'].Text = "{:.2%}".format(float(i)/float(total)) # loading counter going up

	numItm['Renumber'].Text = "Renumber!"
	numItm['Renumber'].Enabled = True # let you click the button again

# opens splash window
def _splash(ev):
	nameWindow.Hide()
	numWindow.Hide()
	disp.ExitLoop()
	splash.Show()
	disp.RunLoop()
	splash.Hide()

# opens rename window
def _nameWin(ev):
	splash.Hide()
	disp.ExitLoop()
	nameWindow.Show()
	disp.RunLoop()
	nameWindow.Hide()

# opens renumber window
def _numWin(ev):
	splash.Hide()
	disp.ExitLoop()
	numWindow.Show()
	disp.RunLoop()
	numWindow.Hide()

################################################################################################
# GUI Elements #
# manipulations
splashItm = splash.GetItems() # Grabs all UI elements to be manipulated
nameItm = nameWindow.GetItems() # Grabs all UI elements to be manipulated
numItm = numWindow.GetItems() # Grabs all UI elements to be manipulated
numItm['break_box'].AddItems(['.','_']) # adds items to dropdown
# button presses
splash.On.Name.Clicked = _nameWin
splash.On.Number.Clicked = _numWin
splash.On.SPLWin.Close = _close
nameWindow.On.tiff_choose.Clicked = _file_browser
nameWindow.On.Rename.Clicked = _rename
nameWindow.On.NAMEWin.Close = _splash
numWindow.On.tiff_choose.Clicked = _file_browser
numWindow.On.Renumber.Clicked = _renumber
numWindow.On.NUMWin.Close = _splash
# window loops
splash.Show()
disp.RunLoop()
splash.Hide()
#################################################################################################

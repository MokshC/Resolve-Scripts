# Moksh
# -*- coding: utf-8 -*-

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
projectManager = resolve.GetProjectManager() # get manager
flags = []

################################################################################################
# Functions #
#############

# in a temporary text document stores flag information
# input: txt [lst]
# output: flags_date.txt 
def store(txt):

	# path of parent and filename
	parent = "/tmp/Mokshs-Flag-Tool/"
	filename = str(date.today()).replace("-","") + ".txt"
	path = parent + filename

	# if the folder doesn't exist, create it
	if os.path.isdir(parent) == False:
		os.mkdir()	
	
	# now open the path
	storage = open(path, 'w')

	txt = '\n'.join(txt)
	storage.write(str(txt))
	

# Copy current clip's flags
def main():

	global flags # allows global edit of flags
	proj = projectManager.GetCurrentProject() # get project
	tl = project.GetCurrentTimeline() # get tl
	clip = timeline.GetCurrentVideoItem() # get clip

	flags = clip.GetFlagList()
	store(flags)

main()

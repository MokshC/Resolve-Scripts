[comment]: <> (The GitHub Repo for this project can be found at https://github.com/MokshC/Resolve-Scripts/)


# Resolve-Scripts
Scripts made for [Black Magic's DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve/). All of these are scripts I use professionally, and they greatly improve my workflow. I believe everyone should have access to them, so here they are.

<br/><br/>

## Things to be aware of
- The below tutorials assume you copied my file structure in your Resolve Scripts folder
- This is tested on Windows and Linux in DaVinci Resolve 18.1.4, the below versions are all for Windows.

<br/><br/>

## Table of Contents
- [Installing Scripts](#installing-scripts)
- [Clip Disabler](#clip-disabler)
- [Marker Note Clipboard](#marker-note-clipboard)
- [Marker Flipper](#marker-flipper)
- [Recap Assist](#recap-assist)
- [EDL Toolbox](#edl-toolbox)
- [Marker Note Exporter](#marker-note-exporter)
- [Markers to Render Queue](#markers-to-render-queue)
- [Individual Clips to Render Queue](#individual-clips-to-render-queue)
- [Renamer and Renumberer](#renamer-and-renumberer)

<br/><br/>

## [Installing Scripts](https://github.com/MokshC/Resolve-Scripts/archive/refs/heads/main.zip)<a name="installing-scripts"/>
***Note**: Visible scripts change based on the page you’re on, there are folders within the scripts dropdown like “Edit”, “Color”, and “Deliver”. When on one of those pages the scripts showing will be from those folders. You can still access them from any page by navigating the drop downs.*

### Steps
1. In Resolve open the Fusion page, in the toolbar click “Fusion > Fusion Settings”
2. Click “Path Map” in the Fusion drop down of the settings window, and make sure “Scripts” is set to “UserPaths:Scripts”. If not, hit the “Reset” button.
3. Click "Script" in the Fusion drop down of the settings window, change selection from python 2.7 to python 3
   - This step is only Resolve version 18.1.4 or later
4. Hit the save button to update all of your changes
5. [Download this repository](https://github.com/MokshC/Resolve-Scripts/archive/refs/heads/main.zip)
6. Unzip and add it to your scripts path. These paths can also be found by clicking the folder icon at the bottom right of "Path Map" from step 2.
   - **LINUX**: Home/.local/share/DaVinciResolve/Fusion/Scripts
     - Hint: if you can’t find .local try hitting Ctrl+H to show hidden folders
   - **WINDOWS**: C:\Users\{NAME}\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts
     - Hint: if you can’t find AppData try going to View > Hidden items in file explorer and hitting the checkbox 
   - **MAC**: /Library/Application Support/Blackmagic Design/Fusion/Scripts
7. Restart Resolve
8. Now when you go open Resolve and, in the toolbar, click “Workspace > Scripts” several scripts should be available.
   
<br/><br/>
   
## [Clip Disabler](https://github.com/MokshC/Resolve-Scripts/blob/main/Color/clip_disabler_v1_5.py)<a name="clip-disabler"/>
### Description
Used to disable clips and flip marker colors and names.
In the color page, in the toolbar, click “Workspace > Scripts > Clip Disabler”.

### DISABLING AND ENABLING CLIPS
“Disable/Enable” button will disable and enable the currently selected clip. This can be seen on the Timeline view.
Hint: Sometimes Resolve will only refresh the clip if you do something like click on another clip
Hint: You don’t need to unlock any tracks for this button to work

### COPYING AND PASTING FLAGS
1. Click the "Copy Flags" button to copy flags on currently selected clip.
2. Click the "Paste Flags" button to paste onto a new clip.
   - **Hint**: This does not copy flag descriptions, and doesn't delete already placed flags.

### EDITING MARKERS
The drop down, text box, and “Flip Marker” button all work together.
1. In the drop down select the color you would like to change the current marker to
2. In the text box adding text will change the name of the marker to what you’ve typed.
   - **Hint**: Leaving it blank leaves the name unchanged, it doesn’t delete it.
3. Have your play head on a marker and click “Flip Marker” to enact changes!

<br/><br/>

## [Marker Note Clipboard](https://github.com/MokshC/Resolve-Scripts/blob/main/Color/Marker%20Note%20Clipboard%20v1.0.0.py)<a name="marker-note-clipboard"/>
### Description
Made as a companion to [Clip Disabler](#clip-disabler). It allows you to quickly replace marker notes.
In the color page, in the toolbar, click “Workspace > Scripts > Marker Note Clipboard”.

### Steps
1. In the text box adding text will change the name of the marker to what you’ve typed.
   - **Hint**: Leaving it blank leaves the name unchanged, it doesn’t delete it.
2. Have your play head on a marker and click “Edit Note” next to the note you want to enact changes!

<br/><br/>

## [Marker Flipper](https://github.com/MokshC/Resolve-Scripts/blob/main/Color/Marker%20Flipper%20v1.2.0.py)<a name="marker-flipper"/>
### Description
Flips marker colors and names for a selected marker color.

### Steps
1. In the color page, in the toolbar, click “Workspace > Scripts > Marker flipper”
2. Using drop downs in the first row you can “Flip [Color1] markers to [Color2]”
   - **Hint**: If you set them to the same color, it will only edit the name of the marker
3. Using the “Flip names to [Name]” and "Flip notes to [Note]" you can change the names or notes of all the above [Color1] markers.
   - **Hint**: Leaving it blank leaves the name unchanged, it doesn’t delete it.
4. Hit the “Flip!” button to enact changes!

<br/><br/>

## [Recap Assist](https://github.com/MokshC/Resolve-Scripts/blob/main/Color/Recap_Assist_v1_6.py)<a name="recap-assist"/>
### Description
Grabs stills for a recaps using a recap timeline and a search timeline.

### Steps
1. Open every project you would like to search for recap shots in read only then open the project with the recap you are tracing to.
2. Create a timeline with only the recap shots in it
3. On the color page, in the toolbar, click “Workspace > Scripts > Recap Assist”
4. Read the warning splash, click “Done!”
5. In the drop down select the timeline of just the recap you’re tracing to.
6. In the “Projects” list, **double click** a project to load it.
7. In the “Timelines” list select a timeline to search for shots to grab stills from.
8. On the color page create and open a power grade album where stills will be grabbed to.
9. Click “Grab Stills” to start the search!
   - **Hint**: By default the exact clip search is checked, unchecking it will search by reel name instead of filename and timecode.
11. Read the warning splash, click “Done!”

<br/><br/>

## [EDL Toolbox](https://github.com/MokshC/Resolve-Scripts/blob/main/Edit/edl_toolbox_v1_1.py)<a name="edl-toolbox"/>
### Description
Adds various information to EDL from metadata, the timeline, and individual clip data.

### Steps
1. In Resolve, export your EDL as you normally do.
2. In the edit page, in the toolbar, click “Workspace > Scripts > EDL Toolbox”
3. To select EDL click "Select EDL" and navigate to the EDL you just exported
4. In the "What timeline is it referencing?" dropdown select the timeline that was used to create the EDL
5. In the "What track is it referencing?" dropdown select the track that was used to create the EDL, if the track is not visible click "Refresh Tracklist" and try again
6. In the checkboxes below select all the information you want to add to the EDL
7. Click "Add to EDL!". The EDL should be edited, the original will now be named old_[name of EDL]

<br/><br/>

## [Marker Note Exporter](https://github.com/MokshC/Resolve-Scripts/blob/main/Deliver/marker_notes_exporter_v1_3.py)<a name="marker-note-exporter"/>
### Description
Creates a .txt document with all marker names, notes, and timecodes in timecode order.

### Steps
1. In the deliver page, in the toolbar, click “Workspace > Scripts > Marker Notes Exporter”
2. In the “What color marker should be exported?” drop down select a color to export, or choose all to export all marker notes
3. In the “What timeline should I use?” drop down select the timeline to export markers from.
4. In the “What should the file be named?” text box type the name you’d like the .txt file to have.
5. To select export path, click “Select Export Location” and navigate to the desired folder then click “Choose”.
   - **Hint**: The “Please select a folder” text should change to the path you’ve selected.
6. Click “Create .txt” to export a text document with the above settings.

<br/><br/>

## [Markers to Render Queue](https://github.com/MokshC/Resolve-Scripts/blob/main/Deliver/markers_to_render_queue_v1_5.py)<a name="markers-to-render-queue"/>
### Description
Exports sections of timeline covered by markers, 1 frame for single marker or longer section for span markers. This can be used to easily create SDR stills or automate patches.

### Steps
1. Create a Render Preset you would like to use with this Script on the deliver page in resolve, make sure to set “Filename uses” to “Custom name”.
2. In the deliver page, in the toolbar, click “Workspace > Scripts > Markers to Render Queue”
3. In the “What color marker should be exported?” drop down select a color to export, or choose all
4. In the “What preset should I use?” drop down select the desired preset that all clips will render at.
5. In the “What timeline should I use?” drop down select the timeline to export markers from.
6. In the “What should it be named?” text box type the name you’d like the .txt file to have. The following dropdown has options for “.”, “_”, or “#” to be added to the end of the name
   - **Hint**: Adding # to the file name will have the file names count up (ex. prores# -> prores1, prores2, prores3)
7. To select export path, click “Select Export Location” and navigate to the desired folder then click “Choose”.
   - **Hint**: The “Please select a folder” text should change to the path you’ve selected.
8. Click “Add to Render Queue” to populate the render queue with all the markers in the timeline with the settings you just filled out!

<br/><br/>

## [Individual Clips to Render Queue](https://github.com/MokshC/Resolve-Scripts/blob/main/Deliver/individual_clips_to_render_queue_v1_3.py)<a name="individual-clips-to-render-queue"/>
### Description
Adds all clips from a selected timeline to the render queue with specified settings.

### Steps
1. Create a Render Preset you would like to use with this Script on the deliver page in resolve, make sure to set “Filename uses” to “Custom name”.
2. Create a timeline that you’d like each individual clip to be rendered from
3. In the deliver page, in the toolbar, click “Workspace > Scripts > Individual clips to render queue”
4. In the “What preset should I use?” drop down select the desired preset that all clips will render at.
5. In the “What timeline should I use?” drop down select the timeline you’d like to render every clip from.
6. To select export path, click “Select Export Location” and navigate to the desired folder then click “Choose”.
   - **Hint**: The “Please select a folder” text should change to the path you’ve selected.
7. Click “Add to Render Queue” to populate the render queue with all the clips in the timeline with the settings you just filled out!

<br/><br/>

## [Renamer and Renumberer](https://github.com/MokshC/Resolve-Scripts/blob/main/Utility/Rename_Renumber_v1_3.py)<a name="renamer-and-renumberer"/>
### Description
Can rename or renumber any image sequence, or any set of files in general!

### RENAME
1. On any page, in the toolbar, click “Workspace > Scripts > Moksh’s Renamer and Renumberer”
2. Click Rename
3. To select search path, click “Select Tiff Location” and navigate to the desired folder then click “Choose”.
   - **Hint**: You won’t see the image sequence there since this view only shows folders.
   - **Hint**: The “Please select a folder” text should change to the path you’ve selected.
4. Fill the “Find:” text box with what the script will search for to replace. It’s best to have the whole file name up to the frame number, to prevent mistakes when replacing.
5. Fill the “Replace:” text box with what to replace the “Find:” with.
6. Hit “Rename!” to enact changes!

### RENUMBER
1. In the deliver page, in the toolbar, click “Workspace > Scripts > Moksh’s Renamer and Renumberer”
2. Click Renumber
3. To select search path, click “Select Tiff Location” and navigate to the desired folder then click “Choose”.
   - **Hint**: You won’t see the image sequence there since this view only shows folders.
   - **Hint**: The “Please select a folder” text should change to the path you’ve selected.
4. Use the drop down to select how the file number is separate from the name in the current name. (ex. For “.” the name would look like NAME_UDH_HDR.0068180.tif)
5. Use the “Digits in filename” carousel to select how many digits you want in the new filename. (ex. For “7” NAME_UDH_HDR.0068180.tif)
6. Fill the “Starting Frame” text box with what you would like the new starting frame number to be
7. Hit “Renumber!” to enact changes!




## Coot plumage - Adding a feathery flourish to Coot.

A small collection of mostly time saving add-ons for the model building software Coot. Works with both Coot 0.9.x and Coot 1.x (set the `COOT_VERSION` variable in plumage.py, see installation).
Installation instructions can be found at the end of this file.

Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)

## Molprobity to Coot
Extract a list of residues from the Molprobity multi-criterion table produced by the web server and send them to coot. Buttons and hotkeys are provided to quickly cycle through residues in this list within coot to quickly fix issues without having to keep cross-referencing back to the table.  
To start, send the model to the molprobity server at [molprobity.biochem.duke.edu](molprobity.biochem.duke.edu).  
Click through to the results section named "Multi-criterion chart". This will display a table with all the residues and any validation issues associated with each. Save this webpage as a html file (Right click or File -> Save as...).
Then you can extract a subset of residues from this table and send them to Coot. For example, if you wanted to select all the Rotamer outliers, do:
```
molprobity_to_coot.py --column Rotamer --filter_text OUTLIER <molprobity_html_file>
```
where <molprobity_html_file> is the downloaded html file from molprobity. The script finds cells in the table that contain the value set by --filter_text so you can set this to "Allowed" or any other text that will match whatever you want.  
Alternatively, there are some wrapper scripts that will find the most recent html file in the current directory so you can copy these to that directory and run them by double-clicking them or calling them from the command line. Hopefully these should be straightforward to edit to suit your needs. 

Finally you can cycle through the residues in this list with the toolbar buttons provided or with the "q" and "w" keys. (ensure the correct molecule is selected in the "Go To Atom" window.) 

Note: additional installation steps are required to get this to work. See instructions below.
## Next rotamer
This simply cycles through the rotamers similar to the "Rotamers..." button but quicker. The status bar displays information about the rotamer. The original orientation of the side chain is kept incase you wish to stick with it.
Click the buttons or use the "e" and "r" keys. 

## Real space refine zone
A hotkey to activate the real space refine zone mode for the current residue and for n residues either side. This avoids having to click the start and end residues. (Note: It is designed to stop at breaks in the chain).  

By default the z and x keys activate the current residue and 2 and 3 residues either side respectively. There is also an option to press Shift + number key to run the command with n set to 0-9. Note: you may need to edit the script to match your keyboard layout. 

## Notes

Key bindings can be adjusted by editing the top of each script.
Some additional small default settings are set in the plumage.py script. Comment out or edit these as appropriate.  
Note for Coot 1.x: the toolbar buttons show the same icons as in 0.9.x plus a text label. Set `TOOLBAR_LABELS = False` in plumage.py for icon only buttons (Coot 0.9.x buttons are always icon only).
Some inspiration for these scripts were taken from Oli Clarke's excellent repo [github.com/olibclarke/coot-trimmings](github.com/olibclarke/coot-trimmings) and Phenix's coot integration.  

## Installation
Coot:   
Download/clone this repository:
```commandline
git clone https://github.com/robertstass/coot_plumage.git
```
Go to the coot_plumage directory and edit the plumage.py file to:  
- replace the value of script_dir with the full path to this repository directory.  
- set COOT_VERSION to 0 (Coot 0.9.x and older) or 1 (Coot 1.x). Setting it to None makes the scripts try to detect the version automatically. A warning is printed in Coot's terminal if the value you set looks wrong.  

Then move the plumage.py file to the Coot preferences directory:  

| Coot version | Preferences directory |
|---|---|
| 0.9.x | `~/.coot-preferences` (`C:\Users\<username>\.coot-preferences` on Windows) |
| 1.x | `~/.config/COOT/Preferences` (`C:\Users\<username>\AppData\Local\COOT\config\Preferences` on Windows) |

```commandline
mv plumage.py ~/.coot-preferences
```
(If the XDG_CONFIG_HOME environment variable is set, Coot 1.x looks in `$XDG_CONFIG_HOME/Preferences` instead.)  
Feel free to edit default values or remove any unwanted lines in this file. 

## Supporting both Coot versions
Coot 1.x moved most functions into the `coot` module (e.g. `set_map_radius_em(20)` became `coot.set_map_radius_em(20)`), and changed how toolbar buttons and key bindings are added, so the scripts access Coot through a small shared module, `coot_bin/plumage_compat.py`.  
plumage.py sets the version once (`plumage_compat.init(COOT_VERSION)`) and each script in coot_bin simply does:
```python
import plumage_compat as pc
pc.COOT_VERSION                      # 0 or 1
pc.coot.set_map_radius_em(20)        # call any Coot function. Works in both versions.
pc.toolbar_button(label, function, icon=..., tooltip=...)  # icon: a Coot icon name e.g. "refine-1.svg" or the full path to your own svg/png
pc.add_key_binding(name, key, function)
```
Use these when writing new scripts so that they work in both versions. The molprobity_to_coot.py script runs outside of Coot and talks to it over XML-RPC, so it does not depend on the Coot version.  

Additional steps are required to use the molprobity_to_coot.py script:  
This script runs on an external python installation and has the following requirements:  
-pandas (tested on v1.5.3)  
-bs4 (tested on v4.11.1)  
The easiest way to get access to these is with an [Anaconda](https://www.anaconda.com/download) installation as these libraries should be installed already. If not, set up an environment with:  
conda env create -f coot_plumage.yml  
conda activate coot_plumage   

Add the following to your ~/.bashrc file: 
```
export PATH=<full_path_to>/coot_plumage/bin:$PATH  
```
Or if on Windows add <full_path_to>/coot_plumage/bin to your system PATH environment variable.  

Then it can be run using:
```
molprobity_to_coot.py  
```
(Note you may have to do "conda activate coot_plumage" first depending on how you set it up)






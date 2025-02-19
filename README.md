## Coot plumage - Adding a feathery flourish to Coot.

A small collection of mostly time saving add-ons for the model building software Coot.
Installation instructions can be found at the end of this file.

## Molprobity to Coot
Extract a list of residues from the Molprobity multi-criterion table produced by the web server and send them to coot. Buttons and hotkeys are provided to quickly cycle through residues in this list within coot to quickly fix issues without having to keep cross-referencing back to the table.  
To start, send the model to the molprobity server at [molprobity.biochem.duke.edu](molprobity.biochem.duke.edu).  
Click through to the results section named "Multi-criterion chart". This will display a table with all the residues and any validation issues associated with each. Save this webpage as a html file (Right click or File -> Save as...).
Then you can extract a subset of residues from this table and send them to Coot. For example, if you wanted to select all the Rotamer outliers, do:
```
python molprobity_to_coot.py --column Rotamer --filter_text OUTLIER <molprobity_html_file>
```
where <molprobity_html_file> is the downloaded html file from molprobity. The script finds cells in the table that contain the value set by --filter_text so you can set this to "Allowed" or any other text that will match whatever you want.  
Alternatively, there are some wrapper scripts that will find the most recent html file in the current directory so you can copy these to that directory and run them by double-clicking them or calling them from the command line. Hopefully these should be straightforward to edit to suit your needs. 

Finally you can cycle through the residues in this list with the toolbar buttons provided or with the "q" and "w" keys. 

Note: additional installation steps are required to get this to work. See instructions below.
## Next rotamer
This simply cycles through the rotamers similar to the "Rotamers..." button but quicker. The status bar displays information about the rotamer. The original orientation of the side chain is kept incase you wish to stick with it.
Click the buttons or use the "e" and "r" keys. 

## Real space refine zone
A hotkey to activate the real space refine zone mode for the current residue and for n residues either side. This avoids having to click the start and end residues. 

By default the z and x keys activate the current residue and 2 and 3 residues either side respectively. There is also an option to press Shift + number key to run the command with n set to 0-9. Note: you may need to edit the script to match your keyboard layout. 

## Notes

Key bindings can be adjusted by editing the top of each script.
Some additional small default settings are set in the plumage.py script. Comment out or edit these as appropriate.
Some inspiration for these scripts were taken from Oli Clarke's excellent repo [github.com/olibclarke/coot-trimmings](github.com/olibclarke/coot-trimmings) and Phenix's coot integration.  

## Installation
Coot:   
Download/clone this repository and edit the plumage.py file to replace the value of script_dir with the full path to this repository directory. Then move the plumage.py file to the ~/.coot-preferences directory (C:\Users\<username>\.coot-preferences on Windows). Feel free to edit default values or remove any unwanted lines in this file. 

Additional steps are required to use the molprobity_to_coot.py script:  
This script runs on an external python installation and has the following requirements:  
-pandas (tested on v1.5.3)  
-bs4 (tested on v4.11.1)  
The easiest way to have access to these is with an [Anaconda](https://www.anaconda.com/download) installation as these libraries should be installed already. If not, set up an environment with:  
conda env create -f coot_plumage.yml  
conda activate coot_plumage  
Then add the following to your ~/.bashrc file:  
export PATH=<full_path_to>/coot_plumage/bin:$PATH  
Or if on windows add <full_path_to>/coot_plumage/bin to your system PATH environment variable.

Then it can be run using:
molprobity_to_coot.py  
(Note you may have to do "conda activate coot_plumage" first depending on how you set it up)






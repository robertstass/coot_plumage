# -*- coding: utf-8 -*-
# Part of coot_plumage (github.com/robertstass/coot_plumage). Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)

###### Set to the full path of the Coot plumage repository
script_dir = r"<full_path_to>/coot_plumage"

###### Set to the version of Coot you are using
# 0 = Coot 0.9.x (python 2, the older versions)
# 1 = Coot 1.x   (python 3)
# None = try to detect it automatically
COOT_VERSION = None

# Coot 1 only: show the text label next to the icon on the toolbar buttons.
# False = icon only (hover for a tooltip). Coot 0.9 toolbar buttons are always icon only.
TOOLBAR_LABELS = True

# Move this script to the Coot preferences directory:
#   Coot 0.9.x:  ~/.coot-preferences                       (C:\Users\<username>\.coot-preferences on Windows)
#   Coot 1.x:    ~/.config/COOT/Preferences                (C:\Users\<username>\AppData\Local\COOT\config\Preferences on Windows)


import os
import sys

# Make the shared compatibility module importable. It holds COOT_VERSION so that all of the scripts below can see it.
sys.path.insert(0, os.path.join(script_dir, "coot_bin"))
import plumage_compat as pc
pc.init(COOT_VERSION, toolbar_labels=TOOLBAR_LABELS)


###### Additional defaults ######
# Edit / remove as appropriate
# (pc.coot.<function> works in both versions. In Coot 1 the functions must be accessed via the coot module.)
pc.coot.set_map_radius_em(20)  # The radius of the map that is rendered. Smaller values are quicker to render.
pc.coot.set_refine_auto_range_step(4) # Number of residues to refine when clicking a single residue and then hitting the "a" key.
pc.coot.set_matrix(20) # Default value for the "Weight matrix, Refinement weight" setting that can be adjusted in the Refinement and regularization settings panel.
pc.coot.set_refine_ramachandran_angles(1) # Include ramachandran constraints in the refinement.

###### Useful additional functions ######
pc.toolbar_button("Sphere Refine", pc.sphere_refine, icon="reset-view-32.svg", tooltip="RSR around active residue")

###### Load external scripts ######
# Each of these can read the version with: import plumage_compat as pc; pc.COOT_VERSION
pc_scripts = ["coot_refine_zone.py",
              "molprobity_to_coot_server.py",  # Then supply lists of residues with molprobity_to_coot.py
              "coot_rotamers.py"]
for pc_script in pc_scripts:
    pc.coot.run_script(os.path.join(script_dir, "coot_bin", pc_script))

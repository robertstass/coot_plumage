# Part of coot_plumage (github.com/robertstass/coot_plumage). Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)

###### Set to the full path of the Coot plumage repository
script_dir = r"<full_path_to>/coot_plumage"
#Move this script to the ~/.coot-preferences directory


###### Additional defaults ######
# Edit / remove as appropriate
set_map_radius_em(20)  # The radius of the map that is rendered. Smaller values are quicker to render.
set_refine_auto_range_step(4) # Number of residues to refine when clicking a single residue and then hitting the "a" key.
set_matrix(20) # Default value for the "Weight matrix, Refinement weight" setting that can be adjusted in the Refinement and regularization settings panel.
set_refine_ramachandran_angles(1) # Include ramachandran constraints in the refinement.

###### Useful additional functions ######
coot_toolbar_button("Sphere Refine", "sphere_refine()", icon_name="reset-view.svg", tooltip="RSR around active residue")

###### Load external scripts ######
run_script(os.path.join(script_dir,"coot_bin/coot_refine_zone.py"))
run_script(os.path.join(script_dir,"coot_bin/molprobity_to_coot_server.py")) # Then supply lists of residues with molprobity_to_coot.py
run_script(os.path.join(script_dir,"coot_bin/coot_rotamers.py"))
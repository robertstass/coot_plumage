# -*- coding: utf-8 -*-
# This is not a standalone script.
# It must be run in coot using the run_script(r"/path/to/coot_refine_zone.py")

############################################

default_number_of_residues_1 = 2
default_number_of_residues_2 = 3
key_1 = 'z'
key_2 = 'x'
do_shift_numbers = True # If True, you may have to edit the script below to match your keyboard layout.

############################################




aa_dict={'A':'ALA','R':'ARG','N':'ASN','D':'ASP','C':'CYS','E':'GLU','Q':'GLN','G':'GLY','H':'HIS','I':'ILE','L':'LEU','K':'LYS','M':'MET','F':'PHE','P':'PRO','S':'SER','T':'THR','W':'TRP','Y':'TYR','V':'VAL'}

# Real space refine zone with n residues either side of current residue.
def real_space_refine_zone_num_residues(residues=default_number_of_residues_1):
    imol = go_to_atom_molecule_number()
    chain_id = go_to_atom_chain_id()
    resnum = go_to_atom_residue_number()
    res_name = residue_name(imol, chain_id, resnum, "")
    residues_offset_list = [i-residues for i in range(0,residues*2+1)]
    residues_exist = []
    for residue_offset in residues_offset_list:
        n = resnum + residue_offset
        exists = False
        if does_residue_exist_p(imol,chain_id,n,""):
            name = residue_name(imol, chain_id, n, "")
            if name in aa_dict.values():
                exists = True
        residues_exist.append(exists)
    if not residues_exist[residues]: #central residue
        return
    # find a contiguous region that does not extend past breaks in the chain or ends.
    remove_end = False
    residues_keep = [True]*len(residues_offset_list)
    for i, exists in enumerate(residues_exist):
        if i < residues: # 2nd half only
            continue
        if not exists:
            remove_end = True
        if remove_end:
            residues_keep[i] = False
    remove_end = False
    for i, exists in enumerate(residues_exist[::-1]):
        if i < residues: # 1st half only
            continue
        if not exists:
            remove_end = True
        if remove_end:
            residues_keep[len(residues_offset_list)-i-1] = False
    residues_offset_list_contiguous = [offset for keep, offset in zip(residues_keep, residues_offset_list) if keep]
    min_resnum = resnum+residues_offset_list_contiguous[0]
    max_resnum = resnum+residues_offset_list_contiguous[-1]
    add_status_bar_text('Real space refine zone from residue %d to %d in chain %s of molecule %d.' % (min_resnum, max_resnum, chain_id, imol))
    refine_zone(imol, chain_id, min_resnum, max_resnum, "")


def refine_default_1():
    real_space_refine_zone_num_residues(default_number_of_residues_1)

def refine_default_2():
    real_space_refine_zone_num_residues(default_number_of_residues_2)



coot_toolbar_button("Real space refine zone", "refine_default_1()", "refine-1.svg", tooltip="Real space refine zone for current residue and %d residues either side. Hotkeys: %s(%d either side). %s(%d either side)." % (default_number_of_residues_1, key_1, default_number_of_residues_1, key_2, default_number_of_residues_2))
add_key_binding("Real space refine zone default 1",key_1, lambda: refine_default_1())
add_key_binding("Real space refine zone default 1",key_2, lambda: refine_default_2())

############ EDIT TO MATCH YOUR KEYBOARD LAYOUT ###########
if do_shift_numbers:
    add_key_binding("Real space refine zone zero",")", lambda: real_space_refine_zone_num_residues(0)) # shift + 0
    add_key_binding("Real space refine zone one","!", lambda: real_space_refine_zone_num_residues(1)) # shift + 1
    add_key_binding("Real space refine zone two",'\"', lambda: real_space_refine_zone_num_residues(2)) # shift + 2
    #Below didn't work due to not recognising the £ symbol so had to add the key code manually.
    # Press the key and look for "Key 163 not found in (python) key bindings" to get the number.
    #add_key_binding("Real space refine zone three",u"£", lambda: real_space_refine_zone_num_residues(3)) # shift + 3
    key_bindings.append([163, u"£", "Real space refine zone three", lambda: real_space_refine_zone_num_residues(3)])
    add_key_binding("Real space refine zone four","$", lambda: real_space_refine_zone_num_residues(4)) # shift + 4
    add_key_binding("Real space refine zone five","%", lambda: real_space_refine_zone_num_residues(5)) # shift + 5
    add_key_binding("Real space refine zone six","^", lambda: real_space_refine_zone_num_residues(6)) # shift + 6
    add_key_binding("Real space refine zone seven","&", lambda: real_space_refine_zone_num_residues(7)) # shift + 7
    add_key_binding("Real space refine zone eight","*", lambda: real_space_refine_zone_num_residues(8)) # shift + 8
    add_key_binding("Real space refine zone nine","(", lambda: real_space_refine_zone_num_residues(9)) # shift + 9



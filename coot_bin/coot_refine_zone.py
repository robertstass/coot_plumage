# -*- coding: utf-8 -*-
# This is not a standalone script.
# It must be run in coot using the run_script(r"/path/to/coot_refine_zone.py")
# (plumage.py does this for you, and must be run first as it sets up the plumage_compat module.)
# Part of coot_plumage (github.com/robertstass/coot_plumage). Written by Robert Stass, Bowden group, STRUBI/OPIC (2024)
############################################

default_number_of_residues_1 = 2
default_number_of_residues_2 = 3
key_1 = 'z'
key_2 = 'x'
do_shift_numbers = True # If True, you may have to edit the script below to match your keyboard layout.

############################################

import plumage_compat as pc  # holds COOT_VERSION (set in plumage.py) and the version-specific wrappers.


aa_dict={'A':'ALA','R':'ARG','N':'ASN','D':'ASP','C':'CYS','E':'GLU','Q':'GLN','G':'GLY','H':'HIS','I':'ILE','L':'LEU','K':'LYS','M':'MET','F':'PHE','P':'PRO','S':'SER','T':'THR','W':'TRP','Y':'TYR','V':'VAL'}
nt_list=['A','C','T','G','U', "I", "DA", "DC", "DG", "DI", "DT", "DU"]
# Real space refine zone with n residues either side of current residue.
def real_space_refine_zone_num_residues(residues=default_number_of_residues_1):
    imol = pc.coot.go_to_atom_molecule_number()
    chain_id = pc.coot.go_to_atom_chain_id()
    resnum = pc.coot.go_to_atom_residue_number()
    res_name = pc.coot.residue_name(imol, chain_id, resnum, "")
    residues_offset_list = [i-residues for i in range(0,residues*2+1)]
    residues_exist = []
    for residue_offset in residues_offset_list:
        n = resnum + residue_offset
        exists = False
        if pc.coot.does_residue_exist_p(imol,chain_id,n,""):
            name = pc.coot.residue_name(imol, chain_id, n, "")
            if name in aa_dict.values():
                exists = True
            elif name in nt_list:
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
    pc.coot.add_status_bar_text('Real space refine zone from residue %d to %d in chain %s of molecule %d.' % (min_resnum, max_resnum, chain_id, imol))
    pc.coot.refine_zone(imol, chain_id, min_resnum, max_resnum, "")


def refine_default_1():
    real_space_refine_zone_num_residues(default_number_of_residues_1)

def refine_default_2():
    real_space_refine_zone_num_residues(default_number_of_residues_2)



pc.toolbar_button("Real space refine zone", refine_default_1, icon="refine-1.svg", tooltip="Real space refine zone for current residue and %d residues either side. Part of the coot_plumage set of scripts. Hotkeys: %s(%d either side). %s(%d either side)." % (default_number_of_residues_1, key_1, default_number_of_residues_1, key_2, default_number_of_residues_2))
pc.add_key_binding("Real space refine zone default 1", key_1, lambda: refine_default_1())
pc.add_key_binding("Real space refine zone default 2", key_2, lambda: refine_default_2())

############ EDIT TO MATCH YOUR KEYBOARD LAYOUT ###########
# Each entry is: [name, key produced by shift + number, number of residues, optional numeric key code]
# The default below is for a UK keyboard layout.
# The pound sign can't be given as a plain ascii key so its numeric key code is supplied.
# (Press the key and look for "Key 163 not found in (python) key bindings" in Coot 0.9 to get a number for other keys.
# In Coot 1 the number is the GDK keyval, which is the unicode value for most printable characters.)
shift_number_keys = [
    ["zero",  ")",  0, None],  # shift + 0
    ["one",   "!",  1, None],  # shift + 1
    ["two",   '"',  2, None],  # shift + 2
    ["three", u"£", 3, 163],   # shift + 3
    ["four",  "$",  4, None],  # shift + 4
    ["five",  "%",  5, None],  # shift + 5
    ["six",   "^",  6, None],  # shift + 6
    ["seven", "&",  7, None],  # shift + 7
    ["eight", "*",  8, None],  # shift + 8
    ["nine",  "(",  9, None],  # shift + 9
]
if do_shift_numbers:
    for number_name, shift_key, number_of_residues, key_code in shift_number_keys:
        # n=number_of_residues in the lambda captures the value now rather than at the time of the key press.
        pc.add_key_binding("Real space refine zone " + number_name, shift_key,
                           lambda n=number_of_residues: real_space_refine_zone_num_residues(n), key_code=key_code)

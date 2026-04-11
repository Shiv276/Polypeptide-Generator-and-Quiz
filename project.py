from rdkit import Chem
from rdkit.Chem import rdDepictor
import random
Chem.rdDepictor.SetPreferCoordGen(False) #Turning off the linear branching method so that 2D molecule is more folded (***maybe turn later on for an easy mode)
###Main Peptide Generator. quiz_Construction.py (other file) uses these functions to construct a GUI for end users


def cheatMode(func):
    import pyperclip
    """
    Quick way for the answer (AA sequence) to be copied to clipboard upon molecule generation
    for rapid testing during development
    """
    def wrapper(length):
        seq, mol = func(length)
        pyperclip.copy(seq)
        return seq, mol
    return wrapper


#@cheatMode
def main(length):
     #Turning off the linear branching method so that 2D molecule is more folded (***maybe turn later on for an easy mode)

    while True: #Infinite loop to keep drawing molecules until one that has no collision is made
        keys = sequence_maker(length)
        mol = build_peptide(keys)
        seq = "".join(AA_names_dict[i] for i in keys)

        if has_collision(mol):
            print("Molecule has collision. Re-constructing...")
            continue 
        else:
            return seq, mol


AA_dict = {
    1: "N[C@@H](C)C(=O)O",
    2: "N[C@@H](CCCNC(=N)N)C(=O)O",
    3: "N[C@@H](CC(=O)N)C(=O)O",
    4: "N[C@@H](CC(=O)O)C(=O)O",
    5: "N[C@@H](CS)C(=O)O",
    6: "N[C@@H](CCC(=O)O)C(=O)O",
    7: "N[C@@H](CCC(=O)N)C(=O)O",
    8: "NCC(=O)O",
    9: "N[C@@H](CC1=CN=CN1)C(=O)O",
    10: "N[C@@H](C(C)CC)C(=O)O",
    11: "N[C@@H](CC(C)C)C(=O)O",
    12: "N[C@@H](CCCCN)C(=O)O",
    13: "N[C@@H](CCSC)C(=O)O",
    14: "N[C@@H](Cc1ccccc1)C(=O)O",
    15: "N1[C@@H](CCC1)C(=O)O",
    16: "N[C@@H](CO)C(=O)O",
    17: "N[C@@H](C(O)C)C(=O)O",
    18: "N[C@@H](Cc1c[nH]c2ccccc12)C(=O)O",
    19: "N[C@@H](Cc1ccc(O)cc1)C(=O)O",
    20: "N[C@@H](C(C)C)C(=O)O",
}
#Dict of all regular AAs for constructing the middle residues of peptides

AA_dict_Nterm_Protonated = {
    1: "[NH3+][C@@H](C)C(=O)O",
    2: "[NH3+][C@@H](CCCNC(=N)N)C(=O)O",
    3: "[NH3+][C@@H](CC(=O)N)C(=O)O",
    4: "[NH3+][C@@H](CC(=O)O)C(=O)O",
    5: "[NH3+][C@@H](CS)C(=O)O",
    6: "[NH3+][C@@H](CCC(=O)O)C(=O)O",
    7: "[NH3+][C@@H](CCC(=O)N)C(=O)O",
    8: "[NH3+]CC(=O)O",
    9: "[NH3+][C@@H](CC1=CN=CN1)C(=O)O",
    10: "[NH3+][C@@H](C(C)CC)C(=O)O",
    11: "[NH3+][C@@H](CC(C)C)C(=O)O",
    12: "[NH3+][C@@H](CCCCN)C(=O)O",
    13: "[NH3+][C@@H](CCSC)C(=O)O",
    14: "[NH3+][C@@H](Cc1ccccc1)C(=O)O",
    15: "[NH2+]1[C@@H](CCC1)C(=O)O",
    16: "[NH3+][C@@H](CO)C(=O)O",
    17: "[NH3+][C@@H](C(O)C)C(=O)O",
    18: "[NH3+][C@@H](Cc1c[nH]c2ccccc12)C(=O)O",
    19: "[NH3+][C@@H](Cc1ccc(O)cc1)C(=O)O",
    20: "[NH3+][C@@H](C(C)C)C(=O)O",
}
#Dict of AAs with a protonated N-term for constructing the first residue of a peptide

AA_dict_Cterm_Deprotonated = {
    1: "N[C@@H](C)C(=O)[O-]",
    2: "N[C@@H](CCCNC(=N)N)C(=O)[O-]",
    3: "N[C@@H](CC(=O)N)C(=O)[O-]",
    4: "N[C@@H](CC(=O)O)C(=O)[O-]",
    5: "N[C@@H](CS)C(=O)[O-]",
    6: "N[C@@H](CCC(=O)O)C(=O)[O-]",
    7: "N[C@@H](CCC(=O)N)C(=O)[O-]",
    8: "NCC(=O)[O-]",
    9: "N[C@@H](CC1=CN=CN1)C(=O)[O-]",
    10: "N[C@@H](C(C)CC)C(=O)[O-]",
    11: "N[C@@H](CC(C)C)C(=O)[O-]",
    12: "N[C@@H](CCCCN)C(=O)[O-]",
    13: "N[C@@H](CCSC)C(=O)[O-]",
    14: "N[C@@H](Cc1ccccc1)C(=O)[O-]",
    15: "N1[C@@H](CCC1)C(=O)[O-]",
    16: "N[C@@H](CO)C(=O)[O-]",
    17: "N[C@@H](C(O)C)C(=O)[O-]",
    18: "N[C@@H](Cc1c[nH]c2ccccc12)C(=O)[O-]",
    19: "N[C@@H](Cc1ccc(O)cc1)C(=O)[O-]",
    20: "N[C@@H](C(C)C)C(=O)[O-]",
}
#Dict of AAs with a deprotonated C-term for constructing the last residue of a peptide

AA_dict_CandN_term_ionised = {
    1: "[NH3+][C@@H](C)C(=O)[O-]",
    2: "[NH3+][C@@H](CCCNC(=N)N)C(=O)[O-]",
    3: "[NH3+][C@@H](CC(=O)N)C(=O)[O-]",
    4: "[NH3+][C@@H](CC(=O)O)C(=O)[O-]",
    5: "[NH3+][C@@H](CS)C(=O)[O-]",
    6: "[NH3+][C@@H](CCC(=O)O)C(=O)[O-]",
    7: "[NH3+][C@@H](CCC(=O)N)C(=O)[O-]",
    8: "[NH3+]CC(=O)[O-]",
    9: "[NH3+][C@@H](CC1=CN=CN1)C(=O)[O-]",
    10: "[NH3+][C@@H](C(C)CC)C(=O)[O-]",
    11: "[NH3+][C@@H](CC(C)C)C(=O)[O-]",
    12: "[NH3+][C@@H](CCCCN)C(=O)[O-]",
    13: "[NH3+][C@@H](CCSC)C(=O)[O-]",
    14: "[NH3+][C@@H](Cc1ccccc1)C(=O)[O-]",
    15: "[NH2+]1[C@@H](CCC1)C(=O)[O-]",
    16: "[NH3+][C@@H](CO)C(=O)[O-]",
    17: "[NH3+][C@@H](C(O)C)C(=O)[O-]",
    18: "[NH3+][C@@H](Cc1c[nH]c2ccccc12)C(=O)[O-]",
    19: "[NH3+][C@@H](Cc1ccc(O)cc1)C(=O)[O-]",
    20: "[NH3+][C@@H](C(C)C)C(=O)[O-]",
}
#Dict of AAs with both C and N term ionised for outputting single AAs in their zwitterionic form

AA_names_dict = {
    1: "A", 2: "R", 3: "N", 4: "D",
    5: "C", 6: "E", 7: "Q", 8: "G",
    9: "H", 10: "I", 11: "L", 12: "K",
    13: "M", 14: "F", 15: "P", 16: "S",
    17: "T", 18: "W", 19: "Y", 20: "V",
}
#Dict relating each AA to a number from 1-20 for random generation


def sequence_maker(size):
    seq_list = []
    for _ in range(size):
        seq_list.append(random.randint(1, 20))
    return seq_list

def get_backbone_atoms(mol):
    backbone = Chem.MolFromSmarts("[N:1]-[C:2]-[C:3](=[O:4])-[O:5]")
    match = mol.GetSubstructMatch(backbone)
    n_terminal = match[0]
    c_terminal = match[2]
    oh_terminal = match[4]
    return n_terminal, c_terminal, oh_terminal

def couple(res1, res2):
    _, c1, oh1 = get_backbone_atoms(res1)
    n2, _, _ = get_backbone_atoms(res2)

    res1_res2 = Chem.CombineMols(res1, res2)
    mutable_res = Chem.RWMol(res1_res2)

    offset = res1.GetNumAtoms()
    n2 += offset  # renumber for second residue

    mutable_res.AddBond(c1, n2, Chem.BondType.SINGLE)
    mutable_res.RemoveAtom(oh1)

    Chem.SanitizeMol(mutable_res)
    mol = mutable_res.GetMol()
    return mol

def build_peptide(keys):
    if len(keys) > 1:
        mol = Chem.MolFromSmiles(AA_dict_Nterm_Protonated[keys[0]])# First residue where N-term is protonated

        for k in keys[1:-1]:# Middle residues
            incoming = Chem.MolFromSmiles(AA_dict[k])
            mol = couple(mol, incoming)

        # Last residue where C-term is deprotonated
        last = Chem.MolFromSmiles(AA_dict_Cterm_Deprotonated[keys[-1]])
        mol = couple(mol, last)
    else:
        mol = Chem.MolFromSmiles(AA_dict_CandN_term_ionised[keys[0]])
    return mol


#Collision Detection
def rotation_sign(px, py, qx, qy, rx, ry):
    pqx, pqy = qx-px, qy-py
    prx, pry = rx-px, ry-py
    #Build vectors PQ and PR by translating atomic coordinates so that P is at the origin. So all vectors P->Q start from 0

    val = (pqx*pry) - (pqy*prx)
    #2D cross product z component -> sign represents the 'wise' of rotation

    if val > 0:
        return 1  #Positive z component means counterclockwise rotation
    elif val < 0:
        return -1 #Negative z component means clockwise rotation
    else:
        return 0  #0 indicates Colinearity.

def check_colinear_case(px, py, qx, qy, rx, ry): #In the case of colinearity, do the atoms collide on the SAME line or exist beyond the line?
    on_x_line = rx >= min(px, qx) and rx <= max(px, qx)
    on_y_line = ry >= min(py, qy) and ry <= max(py, qy)

    return on_x_line and on_y_line #Returns True if the atom exists within a bond segment

def intersection_check(p1, p2, q1, q2): #Returns True if there is a collision proven by four way endpoint comparison
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = q1
    x4, y4 = q2
    orientation1 = rotation_sign(x1, y1, x2, y2, x3, y3) #Testing P(x1, y1)---Q(x2, y2) with R(x3, y3)
    orientation2 = rotation_sign(x1, y1, x2, y2, x4, y4) #Testing P(x1, y1)---Q(x2, y2) with S(x4, y4)
    #Testing the 'wise' of line PQ to points R and S (opposites mean collision)

    orientation3 = rotation_sign(x3, y3, x4, y4, x1, y1) #Testing R(x1, y1)---S(x2, y2) with P(x1, y1)
    orientation4 = rotation_sign(x3, y3, x4, y4, x2, y2) #Testing R(x1, y1)---S(x2, y2) with Q(x2, y2)
    #Testing the 'wise; of line RS ti points P and Q (opposites mean collision)

    if orientation1 != orientation2 and orientation3 != orientation4: 
        return True
    #If the sign of the 2D Cross product of PQ to R and S are opposites AND the sign for RS to P and Q are opposites
    
    if orientation1 == 0 and check_colinear_case(x1, y1, x2, y2, x3, y3):
        return True
    if orientation2 == 0 and check_colinear_case(x1, y1, x2, y2, x4, y4):
        return True
    if orientation3 == 0 and check_colinear_case(x3, y3, x4, y4, x1, y1):
        return True
    if orientation4 == 0 and check_colinear_case(x3, y3, x4, y4, x2, y2):
        return True
    #In the case of colinearity, return True (collision) if the point(atom) lays on an existing line (bond)

    return False

def has_collision(molecule):
    rdDepictor.Compute2DCoords(molecule)
    conf = molecule.GetConformer() #Takes the one specifc conformer (2D spatial arrangement) of the molecule
    segments = []

    for bond in molecule.GetBonds():
        atomA = bond.GetBeginAtomIdx() 
        atomB = bond.GetEndAtomIdx()
        #Gives which atoms have bonds between them (ie. 1-2 or 4-6)

        pa = conf.GetAtomPosition(atomA)
        pb = conf.GetAtomPosition(atomB)
        p1 = (pa[0], pa[1])
        p2 = (pb[0], pb[1])
        #p1 is the (x, y) cords of atom A
        #p2 is the (x, y) cords of atom B
        segments.append((p1, p2, atomA, atomB)) #Store info on each atom as (x, y, BondPartner1, BondPartner2)

    for i in range(len(segments)):
        p1, p2, a, b = segments[i] #Loop through stored segments and unpack
        for j in range(i + 1, len(segments)): #Loop through all subsequent segments and unpack
            q1, q2, c, d = segments[j]

            if a == c or a == d or b == c or b == d: #Ignore bonds that share an atom since that isn't collision
                continue
            if intersection_check(p1, p2, q1, q2): #Check for coliision between one segment, and all subsequent segments
                return True
    return False
    
if __name__ == "__main__":
    main(10)
#为ligpargen生成的lmp文件的元素添加注释
import re
import sys
from collections import defaultdict

ELEMENTS = {
    'H': 1.008, 'He': 4.0026, 'Li': 6.94, 'Be': 9.0122, 'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180, 
    'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.06, 'Cl': 35.45, 'Ar': 39.948, 'K': 39.098, 'Ca': 40.078, 
    'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38, 
    'Ga': 69.723, 'Ge': 72.630, 'As': 74.922, 'Se': 78.971, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224, 
    'Nb': 92.906, 'Mo': 95.96, 'Tc': 98.0, 'Ru': 101.07, 'Rh': 102.91, 'Pd': 106.42, 'Ag': 107.87, 'Cd': 112.41, 'In': 114.82, 'Sn': 118.71, 
    'Sb': 121.76, 'Te': 127.60, 'I': 126.90, 'Xe': 131.29, 'Cs': 132.91, 'Ba': 137.33, 'La': 138.91, 'Ce': 140.12, 'Pr': 140.91, 'Nd': 144.24, 
    'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.96, 'Gd': 157.25, 'Tb': 158.93, 'Dy': 162.50, 'Ho': 164.93, 'Er': 167.26, 'Tm': 168.93, 'Yb': 173.05, 
    'Lu': 174.97, 'Hf': 178.49, 'Ta': 180.95, 'W': 183.84, 'Re': 186.21, 'Os': 190.23, 'Ir': 192.22, 'Pt': 195.08, 'Au': 196.97, 'Hg': 200.59, 
    'Tl': 204.38, 'Pb': 207.2, 'Bi': 208.98, 'Po': 209.0, 'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0, 'Ac': 227.0, 'Th': 232.04, 
    'Pa': 231.04, 'U': 238.03, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0, 'Cm': 247.0, 'Bk': 247.0, 'Cf': 251.0, 'Es': 252.0, 'Fm': 257.0, 
    'Md': 258.0, 'No': 259.0, 'Lr': 262.0, 'Rf': 267.0, 'Db': 268.0, 'Sg': 271.0, 'Bh': 272.0, 'Hs': 270.0, 'Mt': 276.0, 'Ds': 281.0, 
    'Rg': 280.0, 'Cn': 285.0, 'Nh': 284.0, 'Fl': 289.0, 'Mc': 288.0, 'Lv': 293.0, 'Ts': 294.0, 'Og': 294.0
}

def identify_element(mass, tolerance=0.01):
    for symbol, atomic_mass in ELEMENTS.items():
        if abs(mass - atomic_mass) < tolerance:
            return symbol
    return None

def process_lmp_file(filepath):
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    processed_lines = []
    in_masses_section = False
    element_counts = defaultdict(int)

    for line in lines:
        if 'Masses' in line:
            in_masses_section = True
            processed_lines.append(line)
            continue
        
        if in_masses_section:
            # If the line is blank, just append it and continue.
            # Don't change the state yet.
            if not line.strip():
                processed_lines.append(line)
                continue

            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit():
                try:
                    mass = float(parts[1])
                    atom_id = int(parts[0])
                    element = identify_element(mass)
                    if element:
                        comment = f"  # {element}{atom_id}"
                        processed_lines.append(line.rstrip() + comment + '\n')
                    else:
                        processed_lines.append(line)
                except (ValueError, IndexError):
                    processed_lines.append(line)
            else:
                # If we are in the section, but the line is not blank and not data,
                # then the section must be over.
                in_masses_section = False
                processed_lines.append(line)
        else:
            processed_lines.append(line)

    try:
        with open(filepath, 'w') as f:
            f.writelines(processed_lines)
        print(f"Successfully processed {filepath}")
    except IOError:
        print(f"Error: Could not write to {filepath}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            process_lmp_file(filepath)
    else:
        print("Usage: python process_lmp.py <file1.lmp> <file2.lmp> ...")

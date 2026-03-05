import sys
import os
import re
from collections import defaultdict

def process_lmp_file(filepath):
    try:
        base_name = os.path.basename(filepath)
        filename = os.path.splitext(base_name)[0].replace(' ', '_')
        with open(filepath, 'r', encoding='gbk') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return

    atom_map = {}
    data_sections = defaultdict(list)
    current_section = None
    SECTIONS = ['Masses', 'Bonds', 'Angles', 'Dihedrals', 'Impropers']

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped in SECTIONS:
            current_section = stripped
            continue
        
        if 'Coeffs' in stripped or 'Atoms' in stripped:
            current_section = None
            continue

        if current_section:
            parts = stripped.split()
            if not parts or not parts[0].isdigit():
                continue

            if current_section == 'Masses':
                match = re.search(r'#\s*([A-Za-z]+\d+)', stripped)
                if match:
                    atom_id = parts[0]
                    atom_name = match.group(1)
                    atom_map[atom_id] = atom_name
            else:
                data_sections[current_section].append(parts)

    comments = defaultdict(list)
    
    for parts in data_sections['Bonds']:
        if len(parts) >= 4:
            ids = [parts[2], parts[3]]
            names = [atom_map.get(i) for i in ids]
            if all(names):
                comments['bond types'].append(f"# {filename}_{'_'.join(names)}")

    for parts in data_sections['Angles']:
        if len(parts) >= 5:
            ids = parts[-3:]
            names = [atom_map.get(i) for i in ids]
            if all(names):
                comments['angle types'].append(f"# {filename}_{'_'.join(names)}")

    for parts in data_sections['Dihedrals']:
        if len(parts) >= 6:
            ids = parts[-4:]
            names = [atom_map.get(i) for i in ids]
            if all(names):
                comments['dihedral types'].append(f"# {filename}_{'_'.join(names)}")

    for parts in data_sections['Impropers']:
        if len(parts) >= 6:
            ids = parts[-4:]
            names = [atom_map.get(i) for i in ids]
            if all(names):
                comments['improper types'].append(f"# {filename}_{'_'.join(names)}")

    output_lines = []
    comments_to_insert = comments.copy()

    for line in lines:
        output_lines.append(line)
        for type_key in list(comments_to_insert.keys()):
            if re.search(r'^\s*\d+\s+' + re.escape(type_key), line):
                if not any(c in output_lines[-2] for c in comments_to_insert[type_key]):
                    output_lines.append('\n')
                    output_lines.extend([f"{c}\n" for c in comments_to_insert[type_key]])
                    output_lines.append('\n')
                del comments_to_insert[type_key]
                break
    
    try:
        with open(filepath, 'w', encoding='gbk') as f:
            f.writelines(output_lines)
        print(f"Successfully processed and added all comments to {filepath}")
    except IOError as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = ' '.join(sys.argv[1:])
        process_lmp_file(filepath)
    else:
        print("Usage: python generate_all_comments.py \"<path_to_your_file.lmp>\"")

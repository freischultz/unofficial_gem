import json
import os
import difflib

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "characters.json")

# User provided lists
STOCK_CHARS = ["Retiff", "Canabel", "Echella", "Tikanile", "Ganazu"]

REBOLDOUEX = {
    "normal": ["Andre", "Angie", "Brunie", "Claude", "Falso", "Idge", "Jack", "Panfilo", "Ramiro", "Sharif", "Verita", "Yeganeh", "Henik", "Nix", "Nolette", "Rakib", "Roizia"],
    "rare": ["Scavenger Yeganeh", "Battle Cook Panfilo", "Battle Smith Idge", "Battlefield Claude"]
}

COIMBRA = {
    "normal": ["Adelina", "Alejandro", "Bernelli", "Calyce", "Cortasar", "Reckless Emilia", "Emilia", "Gracielo", "Irawan", "Lisa", "Mboma", "Soho", "Vinar"],
    "rare": ["Sniper Bernelli", "Sage Emilia", "Pirate Adelina", "Soho the Wind", "Mercenary Calyce", "Roht", "Loreta", "Bane", "Vanessa", "Becky"]
}

AUCH = {
    "normal": ["Baek Ho", "Catherine", "Catherine Torsche", "Claire", "Gurtrude", "Hellena", "Karjalainen", "Keuen", "Lorch", "Mary", "Rio", "Trina", "Valleria", "Viki", "Tiburon"],
    "rare": ["Cannon Shooter Claire", "Designer Karjalainen", "Meister Lorch", "Conductor Rio", "Cutie Claire", "Jane", "Jaina", "Giltine", "Valeria Vendetta", "Bianca"]
}

USTIUR = {
    "normal": ["Grenmah", "Rescue Knight", "Serth", "Romina"],
    "rare": ["Rescue Officer Romina", "P. Queen Grenmah", "Miho", "Miha", "Chungha", "Wanida", "Marcelino", "Elizabeth", "Ivy"]
}

BAHAMAR = {
    "normal": ["Nena", "Sharon", "Sierra"],
    "rare": ["Jin", "Asoka", "Sage Sharon", "Psyche", "Seolhwa", "Laval"]
}

LOS_TOLDOS = {
    "normal": ["Kurt", "Edward"],
    "rare": []
}

KATOVIC = {
    "normal": ["Garcia", "Natalie", "Selva Norte"],
    "rare": ["Banshee Natalie", "Mertis", "Selane", "Cold Hearted Ganazu", "Cold Hearted Ganuzu"]
}

# Mapping for tricky names or missing icons
NAME_MAPPING = {
    "Baek Ho": "Backho",
    "Edward": "Eduardo",
    "Grenmah": "Grandma",
    "P. Queen Grenmah": "Grandma2", # Likely mapped to Grandma2
    "Rescue Officer Romina": "Romina2",
    "Battle Cook Panfilo": "Panfilo2",
    "Battle Smith Idge": "Idge2",
    "Battlefield Claude": "Claude2",
    "Scavenger Yeganeh": "Yeganeh2",
    "Sniper Bernelli": "Berneli2", # Note spelling Berneli vs Bernelli
    "Sage Emilia": "Emilia2",
    "Pirate Adelina": "Adelina2",
    "Mercenary Calyce": "Calyce2",
    "Cannon Shooter Claire": "Clair2", # Claire vs Clair
    "Cutie Claire": "Clair3",
    "Designer Karjalainen": "Karjalainen2",
    "Meister Lorch": "Lorch2",
    "Conductor Rio": "Rio2",
    "Valeria Vendetta": "Valleria2", # Valleria vs Valeria
    "Sage Sharon": "Sharon2",
    "Banshee Natalie": "Natalie2",
    "Cold Hearted Ganazu": "Ganazu2",
    "Cold Hearted Ganuzu": "Ganazu2", # User typo handling
    "Reckless Emilia": "Emilia3", 
    "Selva Norte": "Selva",
    "Catherine Torsche": "Catherine2", # Fixed from Torshe
    "Rescue Knight": "Rescue", 
}

def normalize_key(name):
    """
    Tries to find the character key in the json based on the name.
    """
    # 1. Check explicit mapping
    target_name = NAME_MAPPING.get(name, name)
    
    # 2. Try to find key containing this name (case insensitive)
    # The keys are like "spr-icon-pc-name-01"
    
    # Clean target name for search (remove spaces, lowercase)
    clean_target = target_name.lower().replace(" ", "")
    
    best_match = None
    
    for key in CHAR_DATA.keys():
        # Key format: spr-icon-pc-name-01
        key_parts = key.split("-")
        if len(key_parts) >= 4:
            key_name = key_parts[3] # spr-icon-pc-[NAME]-01
            
            # Direct match of name part
            if key_name == clean_target:
                return key
            
            # Check if key_name is in target (e.g. "clair" in "clair2") - wait, no.
            # Check if target is in key_name?
            
    # 3. Fuzzy match if no direct match
    # We search against the "name" field in the json values
    for key, data in CHAR_DATA.items():
        if data['name'].lower() == target_name.lower():
            return key
            
    # 4. Fuzzy match against keys
    # ...
    
    return None

def find_key_by_name_fuzzy(name, char_data):
    # 1. Explicit mapping
    mapped_name = NAME_MAPPING.get(name, name)
    
    # 2. Direct Name Match in JSON values
    for key, data in char_data.items():
        if data['name'].lower() == mapped_name.lower():
            return key
            
    # 3. Key Match (e.g. "Backho" -> "spr-icon-pc-backho-01")
    # We construct a potential key pattern or search for it
    # simplify mapped_name: "Grandma2" -> "grandma2"
    simple_name = mapped_name.lower().replace(" ", "")
    
    for key in char_data.keys():
        if f"-{simple_name}-" in key:
            return key
            
    # 4. If still not found, try fuzzy match on names
    all_names = [d['name'] for d in char_data.values()]
    matches = difflib.get_close_matches(name, all_names, n=1, cutoff=0.6)
    if matches:
        for key, data in char_data.items():
            if data['name'] == matches[0]:
                return key
                
    return None

def update_group(group_name, char_list, is_rare=False):
    print(f"Processing {group_name} ({'Rare' if is_rare else 'Normal'})...")
    for name in char_list:
        key = find_key_by_name_fuzzy(name, CHAR_DATA)
        if key:
            CHAR_DATA[key]['group'] = group_name
            CHAR_DATA[key]['classification'] = "Recruit" if is_rare else "Stock"
            CHAR_DATA[key]['is_rare'] = is_rare # Keep this for backward compat if needed
            CHAR_DATA[key]['hidden'] = False # Ensure character is visible
            
            # Update name to match user input if it's a mapped name or just to be clean
            # But be careful not to overwrite "Ganazu (Rare)" with "Cold Hearted Ganuzu" if that's what we want.
            # The user requested "Cold Hearted Ganuzu", so we should use that name.
            CHAR_DATA[key]['name'] = name
            
            print(f"  [OK] {name} -> {key}")
        else:
            print(f"  [MISSING] Could not find character: {name}")

# --- MAIN ---
if __name__ == "__main__":
    print("Loading characters.json...")
    with open(JSON_PATH, 'r') as f:
        CHAR_DATA = json.load(f)
        
    # Reset all
    print("Resetting all characters...")
    for key in CHAR_DATA:
        CHAR_DATA[key]['group'] = "Unreleased"
        CHAR_DATA[key]['classification'] = "Stock"
        CHAR_DATA[key]['is_rare'] = False

    # Update Groups
    update_group("Stock Characters", STOCK_CHARS)
    
    update_group("Cite Of Reboldouex", REBOLDOUEX['normal'])
    update_group("Cite Of Reboldouex", REBOLDOUEX['rare'], is_rare=True)
    
    update_group("Port Of Coimbra", COIMBRA['normal'])
    update_group("Port Of Coimbra", COIMBRA['rare'], is_rare=True)
    
    update_group("City of Auch", AUCH['normal'])
    update_group("City of Auch", AUCH['rare'], is_rare=True)
    
    update_group("Ustiur", USTIUR['normal'])
    update_group("Ustiur", USTIUR['rare'], is_rare=True)
    
    update_group("Bahamar", BAHAMAR['normal'])
    update_group("Bahamar", BAHAMAR['rare'], is_rare=True)
    
    update_group("Los Toldos", LOS_TOLDOS['normal'])
    update_group("Los Toldos", LOS_TOLDOS['rare'], is_rare=True)
    
    update_group("Katovic", KATOVIC['normal'])
    update_group("Katovic", KATOVIC['rare'], is_rare=True)

    print("Saving characters.json...")
    with open(JSON_PATH, 'w') as f:
        json.dump(CHAR_DATA, f, indent=4)
    print("Done.")

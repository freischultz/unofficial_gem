import json
import os
import re

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "characters.json")
WIKI_PATH = os.path.join(BASE_DIR, "wiki.html")

CHARACTER_GROUPS = [
    "Stock Characters", "Cite Of Reboldouex", "Port Of Coimbra", "City of Auch",
    "Ustiur", "Bahamar", "Los Toldos", "Katovic", "Gigante", "Unreleased", "Unknown"
]

# --- TEMPLATES ---
COMMON_HEAD = """
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Poppins', 'sans-serif'],
                        mono: ['Rajdhani', 'monospace'],
                    },
                    colors: {
                        glass: {
                            100: 'rgba(255, 255, 255, 0.1)',
                            200: 'rgba(255, 255, 255, 0.2)',
                            dark: 'rgba(15, 23, 42, 0.6)',
                            darker: 'rgba(10, 15, 30, 0.8)',
                        },
                        accent: {
                            gold: '#fbbf24',
                            blue: '#38bdf8',
                            green: '#4ade80',
                            red: '#f87171'
                        }
                    }
                }
            }
        }
    </script>
    <style>
        body {
            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            position: relative;
            transition: background-image 0.8s ease-in-out;
            min-height: 100vh;
            color: #e2e8f0;
        }
        body::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to bottom, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.7));
            z-index: -1;
        }
        .glass-panel {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }
        .glass-card {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.2s ease, background-color 0.2s ease;
        }
        .glass-card:hover {
            transform: translateY(-2px);
            background-color: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
        }
        /* Rarity Borders */
        .border-stock { border-color: rgba(255, 255, 255, 0.2); }
        .border-scout { border-color: #4ade80; box-shadow: 0 0 10px rgba(74, 222, 128, 0.2); }
        .border-recruit { border-color: #fbbf24; box-shadow: 0 0 10px rgba(251, 191, 36, 0.2); }
    </style>
"""

WIKI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Granado Espada M - Wiki</title>
    {common_head}
</head>
<body class="antialiased p-4 sm:p-6">
    <div class="max-w-[1600px] mx-auto">
        <header class="flex flex-col md:flex-row items-center justify-between gap-6 mb-8 glass-panel rounded-2xl p-4 md:px-8">
            <div class="flex items-center gap-4">
                <img src="https://gem.playpark.com/wp-content/uploads/2024/11/1-gem-logo.png" alt="Granado Espada M" class="h-16 object-contain drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]" onerror="this.onerror=null;this.src='https://i.imgur.com/kSTiS9s.png';">
                <div class="hidden sm:block border-l border-white/10 pl-4">
                    <h1 class="text-xl font-bold text-white tracking-wide">CHARACTER WIKI</h1>
                    <p class="text-xs text-accent-blue font-medium tracking-wider uppercase">Database & Stats</p>
                </div>
            </div>
            <a href="https://freischultz.github.io/unofficial_gem/index.html" class="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/20 text-white px-5 py-2 rounded-lg text-sm font-bold uppercase tracking-wide transition-all group">
                <i class="ph-bold ph-arrow-u-up-left group-hover:-translate-x-1 transition-transform"></i>
                Back to Tracker
            </a>
        </header>

        <div class="glass-panel rounded-2xl p-6 md:p-8 min-h-screen">
            <div class="mb-8 flex items-center gap-4 pb-6 border-b border-white/5">
                <div class="relative w-full max-w-md">
                    <i class="ph-bold ph-magnifying-glass absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"></i>
                    <input type="text" placeholder="Search characters..." class="w-full bg-black/20 border border-white/10 rounded-lg py-2 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-accent-blue transition-colors placeholder-gray-500">
                </div>
                <div class="text-xs text-gray-500 font-mono uppercase tracking-widest ml-auto">
                    Database Version 1.0
                </div>
            </div>

            <div class="space-y-10">
                {character_sections}
            </div>
        </div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            const backgrounds = ['https://gem.hanbiton.com/Brand2E/src/images/new-contents/event/bg.jpg'];
            document.body.style.backgroundImage = `url(${{backgrounds[0]}})`;
        }});
    </script>
</body>
</html>
"""

def generate_wiki():
    print("Loading characters.json...")
    with open(JSON_PATH, 'r') as f:
        characters = json.load(f)

    all_sections_html = ""
    classification_map = {
        "Stock": "border-stock",
        "Scout": "border-scout",
        "Recruit": "border-recruit"
    }
    
    icon_map = {
        "Stock Characters": "ph-users-three",
        "Cite Of Reboldouex": "ph-buildings",
        "Port Of Coimbra": "ph-anchor",
        "City of Auch": "ph-city",
        "Ustiur": "ph-tree-palm",
        "Bahamar": "ph-plant",
        "Los Toldos": "ph-skull",
        "Katovic": "ph-snowflake",
        "Gigante": "ph-island",
        "Unreleased": "ph-lock-key",
        "Unknown": "ph-question"
    }
    
    color_map = {
        "Stock Characters": "text-accent-gold",
        "Unreleased": "text-accent-red",
        "Unknown": "text-gray-500"
    }

    print("Generating sections...")
    for group_name in CHARACTER_GROUPS:
        chars_in_group = [c for c in characters.values() if c.get('group') == group_name and not c.get('hidden', False)]
        
        # Always show Katovic even if empty (per user preference in previous turn, but here we just follow data)
        # Actually, if empty, we might want to skip or show "No characters".
        # The user's list for Katovic is NOT empty, so it should be fine.
        
        if not chars_in_group and group_name != "Katovic": 
            continue

        icon_class = icon_map.get(group_name, "ph-caret-right")
        color_class = color_map.get(group_name, "text-accent-blue")

        section_html = f"""
        <section>
            <h2 class="text-lg font-bold {color_class} uppercase tracking-widest mb-4 flex items-center gap-2">
                <i class="ph-fill {icon_class}"></i> {group_name}
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 xl:grid-cols-10 gap-4">
        """
        
        links_html = ""
        # Sort by name for now, or use sort_order if available (which we didn't set in update_data.py, so default sort)
        # We can sort by name.
        sorted_chars = sorted(chars_in_group, key=lambda x: x['name'])

        if not sorted_chars:
             links_html += """
                <div class="col-span-full text-center py-8 text-gray-500 text-sm italic">
                    No characters added yet.
                </div>
            """
        else:
            for char_data in sorted_chars:
                border_class = classification_map.get(char_data.get("classification", "Stock"))
                char_id = os.path.splitext(char_data['icon'])[0].lower().replace('_', '-')
                clean_id = char_id.replace("spr-icon-pc-", "")
                
                extra_classes = "opacity-70 hover:opacity-100" if group_name == "Unreleased" else ""
                img_classes = "grayscale group-hover:grayscale-0 transition-all" if group_name == "Unreleased" else "group-hover:scale-110 transition-transform"
                text_classes = "text-gray-400" if group_name == "Unreleased" else "text-gray-300"

                links_html += f"""
                    <a href="characters/{clean_id}.html" class="glass-card p-3 rounded-xl flex flex-col items-center gap-3 group text-center {extra_classes}">
                        <img src="images/icons/{char_data['icon']}" class="w-16 h-16 rounded-lg border-2 {border_class} {img_classes}">
                        <span class="text-xs font-semibold {text_classes} group-hover:text-white truncate w-full">{char_data['name']}</span>
                    </a>
                """
        links_html += '</div></section>'
        all_sections_html += section_html + links_html

    final_html = WIKI_TEMPLATE.format(
        common_head=COMMON_HEAD,
        character_sections=all_sections_html
    )

    print(f"Writing to {WIKI_PATH}...")
    with open(WIKI_PATH, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print("Done.")

if __name__ == "__main__":
    generate_wiki()

import sys
import os
import re
import json
import base64
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QTextEdit, QLabel, QListWidget, QListWidgetItem,
    QCheckBox, QAbstractItemView, QScrollArea, QGridLayout, QListView,
    QDialog, QDialogButtonBox, QComboBox, QFileDialog, QLineEdit,
    QMessageBox
)
from PySide6.QtCore import Qt, QSize, QBuffer, QIODevice
from PySide6.QtGui import QIcon, QPixmap, QBrush

# --- CONFIGURATION ---
CHARACTER_GROUPS = [
    "Stock Characters", "Cite Of Reboldouex", "Port Of Coimbra", "City of Auch",
    "Ustiur", "Bahamar", "Los Toldos", "Katovic", "Gigante", "Unreleased", "Unknown"
]
CLASSIFICATIONS = ["Stock", "Scout", "Recruit"]

# --- HTML TEMPLATES ---

# 1. Shared Head Section (Tailwind Config & CSS for Glassmorphism)
# FIX: Uses single braces { } because this string is NOT formatted by Python.
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

# 2. Main Wiki Page Template
# FIX: Uses double braces {{ }} for JS because this string IS formatted by Python.
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

# 3. Individual Character Page Template
# FIX: Uses double braces {{ }} for JS because this string IS formatted by Python.
CHARACTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Granado Espada M - {name}</title>
    {common_head}
</head>
<body class="antialiased p-4 sm:p-6">
    <div class="max-w-6xl mx-auto">
        
        <header class="flex flex-col md:flex-row items-center justify-between gap-6 mb-8 glass-panel rounded-2xl p-4 md:px-8">
            <div class="flex items-center gap-4">
                <img src="https://gem.playpark.com/wp-content/uploads/2024/11/1-gem-logo.png" alt="Granado Espada M" class="h-16 object-contain drop-shadow-[0_0_10px_rgba(255,255,255,0.2)]" onerror="this.onerror=null;this.src='https://i.imgur.com/kSTiS9s.png';">
            </div>
            <a href="https://freischultz.github.io/unofficial_gem/wiki.html" class="flex items-center gap-2 bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/20 text-white px-5 py-2 rounded-lg text-sm font-bold uppercase tracking-wide transition-all group">
                <i class="ph-bold ph-arrow-u-up-left group-hover:-translate-x-1 transition-transform"></i>
                Back to Wiki
            </a>
        </header>

        <div class="glass-panel rounded-2xl p-8">
            <div class="flex flex-col md:flex-row gap-8 items-start">
                
                <!-- Portrait Card -->
                <div class="w-full md:w-1/3 flex flex-col items-center glass-card p-4 rounded-2xl">
                    <img src="{image_path}" alt="{name}" class="w-full h-auto rounded-xl border-2 {border_class} shadow-lg mb-4">
                    <h1 class="text-2xl font-bold text-white text-center">{name}</h1>
                    <div class="mt-2 px-3 py-1 rounded-full bg-white/10 text-xs font-mono uppercase tracking-widest text-accent-blue">
                        Character Profile
                    </div>
                </div>

                <!-- Info Panel -->
                <div class="w-full md:w-2/3">
                    <h2 class="text-xl font-bold text-accent-gold uppercase tracking-widest mb-6 border-b border-white/10 pb-2">
                        <i class="ph-fill ph-chart-bar"></i> Combat Statistics
                    </h2>
                    
                    <div class="glass-card rounded-xl p-6">
                        <!-- STATS_GO_HERE -->
                        <div class="flex flex-col items-center justify-center py-12 text-center">
                            <i class="ph-duotone ph-scroll text-4xl text-gray-500 mb-4"></i>
                            <h3 class="text-lg font-semibold text-white">No Data Available</h3>
                            <p class="text-sm text-gray-400 max-w-md mt-2">
                                Detailed stats, stances, and recruitment data for {name} have not been uploaded yet. Use the admin tool to analyze screenshots.
                            </p>
                        </div>
                    </div>
                </div>
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

# --- STYLESHEET FOR THE GUI ---
STYLESHEET = """
QWidget { font-family: 'Poppins', sans-serif; color: #E5E7EB; }
QMainWindow, QDialog { background-color: #1a1b26; }
QLabel { background: transparent; }
QTextEdit, QListWidget, QLineEdit, QComboBox { background-color: rgba(42, 44, 61, 0.8); border: 1px solid #414558; border-radius: 8px; }
QPushButton { background-color: #5c95c4; border: 1px solid #6e9cc4; padding: 10px; border-radius: 8px; font-weight: bold; }
QPushButton:hover { background-color: #6e9cc4; }
QPushButton:disabled { background-color: #414558; }
QCheckBox { font-size: 14px; }
QScrollArea { border: none; background: transparent; }
QWidget#scroll-content { background: transparent; }
QListWidget { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(92, 149, 196, 0.5), stop:1 rgba(60, 123, 169, 0.5)); border: 1px solid rgba(110, 156, 196, 0.5); border-radius: 8px; }
QListWidget::item { color: #FFFFFF; padding: 5px; border-radius: 5px; background-color: transparent; }
QListWidget::item:hover { background-color: rgba(255, 255, 255, 0.1); }
"""

class SortDialog(QDialog):
    def __init__(self, group_name, characters, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Sort Characters in {group_name}")
        self.setMinimumSize(400, 500)
        
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        
        sorted_chars = sorted(characters, key=lambda c: c.get('sort_order', float('inf')))
        self.text_edit.setText("\n".join([c['name'] for c in sorted_chars]))
        
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_ordered_names(self):
        return self.text_edit.toPlainText().splitlines()

class CharacterEditDialog(QDialog):
    def __init__(self, char_id, char_data, api_key, parent=None):
        super().__init__(parent)
        self.char_id = char_id
        self.char_data = char_data
        self.api_key = api_key
        self.parent_window = parent
        self.setWindowTitle(f"Edit Character: {self.char_data['name']}")
        self.setGeometry(250, 250, 700, 500)
        self.setStyleSheet(STYLESHEET)
        self.selected_files = []

        main_layout = QVBoxLayout(self)
        
        settings_layout = QGridLayout()
        settings_layout.addWidget(QLabel("Classification:"), 0, 0)
        self.class_combo = QComboBox()
        self.class_combo.addItems(CLASSIFICATIONS)
        self.class_combo.setCurrentText(self.char_data.get("classification", "Stock"))
        settings_layout.addWidget(self.class_combo, 0, 1)
        main_layout.addLayout(settings_layout)

        ai_label = QLabel("AI Stat Updater")
        ai_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
        main_layout.addWidget(ai_label)
        
        self.file_list = QListWidget()
        self.file_list.setFixedHeight(80)
        main_layout.addWidget(self.file_list)

        upload_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Stat Images")
        self.upload_button.clicked.connect(self.open_file_dialog)
        self.paste_button = QPushButton("Paste Image from Clipboard")
        self.paste_button.clicked.connect(self.paste_image)
        upload_layout.addWidget(self.upload_button)
        upload_layout.addWidget(self.paste_button)
        main_layout.addLayout(upload_layout)

        self.update_button = QPushButton("Run AI Update")
        self.update_button.clicked.connect(self.run_ai_update)
        main_layout.addWidget(self.update_button)
        
        self.toggle_visibility_button = QPushButton()
        is_hidden = self.char_data.get("hidden", False)
        self.toggle_visibility_button.setText("Show Character" if is_hidden else "Hide Character")
        self.toggle_visibility_button.setStyleSheet("background-color: #ef4444;" if not is_hidden else "background-color: #22c55e;")
        self.toggle_visibility_button.clicked.connect(self.toggle_visibility)
        main_layout.addWidget(self.toggle_visibility_button)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Stat Images", "", "Images (*.png *.jpg *.jpeg)")
        if files:
            self.selected_files.extend(files)
            self.update_file_list()
            self.parent_window.log(f"Selected {len(files)} images.")

    def paste_image(self):
        clipboard = QApplication.clipboard()
        if not clipboard.mimeData().hasImage():
            self.parent_window.log("No image found on clipboard.")
            return

        pixmap = QPixmap(clipboard.image())
        # Use absolute path for temp file to avoid location issues
        temp_path = os.path.join(self.parent_window.base_dir, "temp_clipboard_image.png")
        pixmap.save(temp_path, "PNG")
        
        self.selected_files.append(temp_path)
        self.update_file_list()
        self.parent_window.log("Pasted image from clipboard.")

    def update_file_list(self):
        self.file_list.clear()
        self.file_list.addItems([os.path.basename(f) for f in self.selected_files])

    def get_updated_data(self):
        self.char_data['classification'] = self.class_combo.currentText()
        return self.char_data

    def toggle_visibility(self):
        is_hidden = self.char_data.get("hidden", False)
        action = "show" if is_hidden else "hide"
        reply = QMessageBox.question(self, f'Confirm {action.capitalize()}', 
            f"Are you sure you want to {action} {self.char_data['name']}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.parent_window.handle_toggle_visibility(self.char_id)
            self.accept()

    def run_ai_update(self):
        parent = self.parent_window
        if not self.api_key:
            parent.log("Error: API Key is required. Set it in the main window.")
            return
        if not self.selected_files:
            parent.log("Error: Please upload or paste at least one image.")
            return

        parent.log(f"Starting AI update for {self.char_data['name']}...")
        self.update_button.setEnabled(False)

        try:
            image_parts = []
            for file_path in self.selected_files:
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                    image_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_string}})

            prompt = "Analyze the attached image(s) of a character's stats from Granado Espada M. Extract all Basic Stats and Stance Information. Format the output as a clean, well-structured HTML snippet using TailwindCSS classes. The final output should be ONLY the HTML code, without any markdown formatting. Use a structure like this: <div class='space-y-4'><div><h3 class='text-lg font-semibold text-amber-200'>Basic Stats</h3>...</div><div><h3 class='text-lg font-semibold text-amber-200'>Stance Information</h3>...</div></div>"

            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={self.api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}] + image_parts}]}
            headers = {"Content-Type": "application/json"}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            ai_generated_html = result['candidates'][0]['content']['parts'][0]['text']
            
            parent.log("AI analysis complete. Updating HTML file...")

            # Use site_root to find characters folder
            clean_id = self.char_id.replace("spr-icon-pc-", "")
            char_html_path = os.path.join(parent.site_root, "characters", f"{clean_id}.html")
            
            if os.path.exists(char_html_path):
                with open(char_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                updated_content = re.sub(r'<!-- STATS_GO_HERE -->.*', f'<!-- STATS_GO_HERE -->{ai_generated_html}', html_content, flags=re.DOTALL)
                
                with open(char_html_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                parent.log(f"Successfully updated {char_html_path}")
            else:
                parent.log(f"Error: Could not find HTML file: {char_html_path}")

        except Exception as e:
            parent.log(f"An error occurred: {e}")
        finally:
            self.update_button.setEnabled(True)
            for file_path in self.selected_files:
                if "temp_clipboard_image.png" in file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Granado Espada M - Wiki Page Generator")
        self.setGeometry(100, 100, 1400, 900)
        self.characters = {}
        self.group_lists = {}
        self.sort_buttons = {}
        self.config = {}
        
        # --- DYNAMIC PATH RESOLUTION ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Attempt to detect site root (where 'http' folder content is)
        # 1. Check if 'http' folder exists in current dir (script is in root)
        path_sub_http = os.path.join(self.base_dir, "http")
        # 2. Check if we are already inside the http folder (fallback)
        path_direct = self.base_dir

        if os.path.exists(os.path.join(path_sub_http, "images")):
            self.site_root = path_sub_http
            self.has_http_subfolder = True
            print(f"Mode: Script in root, assets in ./http/")
        else:
            self.site_root = path_direct
            self.has_http_subfolder = False
            print(f"Mode: Script inside http folder or flat structure.")
        # -------------------------------

        self.setStyleSheet(STYLESHEET)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(300)
        
        title_label = QLabel("Wiki Generator")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 10px;")
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter Google AI API Key...")
        self.api_key_input.textChanged.connect(self.save_config)

        self.edit_mode_checkbox = QCheckBox("Enable Edit Mode")
        self.edit_mode_checkbox.toggled.connect(self.toggle_edit_mode)
        
        self.save_button = QPushButton("Save Character Data")
        self.save_button.clicked.connect(self.save_character_data)
        self.save_button.hide()
        
        self.generate_button = QPushButton("Generate HTML Pages")
        self.generate_button.clicked.connect(self.run_generation_process)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(QLabel("Global API Key:"))
        left_layout.addWidget(self.api_key_input)
        left_layout.addWidget(self.edit_mode_checkbox)
        left_layout.addWidget(self.save_button)
        left_layout.addWidget(self.generate_button)
        left_layout.addWidget(QLabel("Logs:"))
        left_layout.addWidget(self.log_display)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_content.setObjectName("scroll-content")
        self.groups_layout = QGridLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        
        num_columns = 3
        row, col = 0, 0

        for group_name in CHARACTER_GROUPS:
            header_layout = QHBoxLayout()
            group_label = QLabel(group_name)
            group_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
            
            sort_button = QPushButton("Sort")
            sort_button.setFixedWidth(60)
            sort_button.clicked.connect(lambda checked, g=group_name: self.open_sort_dialog(g))
            self.sort_buttons[group_name] = sort_button
            
            header_layout.addWidget(group_label)
            header_layout.addStretch()
            header_layout.addWidget(sort_button)

            list_widget = QListWidget()
            list_widget.setDragDropMode(QAbstractItemView.DragDrop)
            list_widget.setDefaultDropAction(Qt.MoveAction)
            list_widget.setAcceptDrops(True)
            list_widget.setIconSize(QSize(64, 64))
            list_widget.setMinimumHeight(200)
            list_widget.itemChanged.connect(self.handle_item_rename)
            list_widget.itemDoubleClicked.connect(self.open_edit_dialog)

            list_widget.setViewMode(QListWidget.IconMode)
            list_widget.setFlow(QListWidget.LeftToRight)
            list_widget.setWrapping(True)
            list_widget.setResizeMode(QListWidget.Adjust)
            list_widget.setMovement(QListView.Snap)
            list_widget.setSpacing(10)
            
            group_container = QWidget()
            group_layout = QVBoxLayout(group_container)
            group_layout.addLayout(header_layout)
            group_layout.addWidget(list_widget)

            self.group_lists[group_name] = list_widget
            self.groups_layout.addWidget(group_container, row, col)

            col += 1
            if col >= num_columns:
                col = 0
                row += 1

        right_layout.addWidget(scroll_area)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)

        self.load_config()
        self.load_character_data()
        self.populate_lists()
        self.toggle_edit_mode(False)

    def log(self, message):
        self.log_display.append(message)
        QApplication.processEvents()

    def load_config(self):
        config_path = os.path.join(self.base_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.api_key_input.setText(self.config.get("api_key", ""))
            self.log("Loaded config.")
        else:
            self.log(f"Config not found at {config_path}")

    def save_config(self):
        self.config['api_key'] = self.api_key_input.text()
        config_path = os.path.join(self.base_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def parse_filename(self, filename):
        match = re.match(r"SPR_Icon_PC_(\w+?)(\d*)_01\.png", filename)
        if not match: return None
        name_part, rarity_part = match.groups()
        name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name_part) # Add spaces for camelCase
        is_rare = bool(rarity_part)
        if is_rare: name += " (Rare)"
        return {"name": name, "is_rare": is_rare}

    def load_character_data(self):
        self.log(f"Script running in: {self.base_dir}")
        self.log(f"Site Assets Root: {self.site_root}")
        
        # JSON is in base_dir
        char_json_path = os.path.join(self.base_dir, "characters.json")
        if os.path.exists(char_json_path):
            with open(char_json_path, 'r') as f:
                self.characters = json.load(f)
            self.log(f"Loaded existing data from characters.json")
        
        # Icons are in site_root/images/icons
        icon_dir = os.path.join(self.site_root, "images", "icons")
        
        if not os.path.exists(icon_dir):
            self.log(f"Warning: '{icon_dir}' not found. No characters will be loaded.")
            return
            
        new_chars_found = False
        for filename in os.listdir(icon_dir):
            if not filename.endswith('.png'): continue
            
            char_id = os.path.splitext(filename)[0].lower().replace('_', '-')
            if char_id not in self.characters:
                new_chars_found = True
                parsed_info = self.parse_filename(filename)
                if not parsed_info:
                    self.log(f"Skipping unrecognized icon: {filename}")
                    continue
                
                self.log(f"New character found: {parsed_info['name']}")
                self.characters[char_id] = {
                    "name": parsed_info['name'],
                    "icon": filename,
                    "group": "Unknown",
                    "is_rare": parsed_info['is_rare'],
                    "sort_order": 999,
                    "classification": "Stock",
                    "hidden": False
                }
        if new_chars_found:
            self.save_character_data()

    def save_character_data(self):
        self.log("Saving changes to characters.json...")
        for group_name, list_widget in self.group_lists.items():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                char_id = item.data(Qt.UserRole)
                if char_id in self.characters:
                    self.characters[char_id]['group'] = group_name
        
        char_json_path = os.path.join(self.base_dir, "characters.json")
        with open(char_json_path, 'w') as f:
            json.dump(self.characters, f, indent=4)
        self.log("Save complete.")

    def populate_lists(self):
        for list_widget in self.group_lists.values():
            list_widget.clear()
        
        for char_id, data in self.characters.items():
            group = data.get("group", "Unknown")
            if group in self.group_lists:
                # Load icon from site_root/images/icons
                icon_path = os.path.join(self.site_root, "images", "icons", data['icon'])
                
                if os.path.exists(icon_path):
                    item = QListWidgetItem(QIcon(icon_path), data['name'])
                else:
                    item = QListWidgetItem(data['name'])
                    
                item.setData(Qt.UserRole, char_id)
                item.setData(Qt.UserRole + 1, data.get('sort_order', 999))

                if data.get('hidden', False):
                    brush = QBrush(Qt.gray)
                    item.setForeground(brush)
                
                self.group_lists[group].addItem(item)
        
        for list_widget in self.group_lists.values():
            list_widget.sortItems()


    def toggle_edit_mode(self, checked):
        self.log(f"Edit mode {'enabled' if checked else 'disabled'}.")
        self.save_button.setVisible(checked)
        for button in self.sort_buttons.values():
            button.setVisible(checked)
            
        for list_widget in self.group_lists.values():
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                if checked:
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def handle_item_rename(self, item):
        if not self.edit_mode_checkbox.isChecked(): return
        char_id = item.data(Qt.UserRole)
        new_name = item.text()
        if char_id in self.characters and self.characters[char_id]['name'] != new_name:
            self.log(f"Renamed '{self.characters[char_id]['name']}' to '{new_name}'")
            self.characters[char_id]['name'] = new_name
            
    def open_sort_dialog(self, group_name):
        chars_in_group = [data for data in self.characters.values() if data.get('group') == group_name]
        dialog = SortDialog(group_name, chars_in_group, self)
        
        if dialog.exec():
            ordered_names = dialog.get_ordered_names()
            name_to_id_map = {data['name']: char_id for char_id, data in self.characters.items()}
            
            for i, name in enumerate(ordered_names):
                char_id = name_to_id_map.get(name)
                if char_id:
                    self.characters[char_id]['sort_order'] = i
            
            self.log(f"Updated sort order for group '{group_name}'.")
            self.populate_lists()
            
    def open_edit_dialog(self, item):
        char_id = item.data(Qt.UserRole)
        char_data = self.characters.get(char_id)
        if not char_data: return
        
        dialog = CharacterEditDialog(char_id, char_data, self.api_key_input.text(), self)
        if dialog.exec():
            # This block now only runs if Save is clicked, not after visibility toggle
            self.characters[char_id] = dialog.get_updated_data()
            self.save_character_data()
            self.populate_lists()
            self.log(f"Updated settings for {char_data['name']}.")

    def handle_toggle_visibility(self, char_id):
        if char_id in self.characters:
            char_data = self.characters[char_id]
            is_hidden = char_data.get('hidden', False)
            char_data['hidden'] = not is_hidden
            
            action = "shown" if is_hidden else "hidden"
            self.log(f"Character '{char_data['name']}' is now {action}.")
            
            self.save_character_data()
            self.populate_lists()
            self.generate_main_wiki_page()

    def generate_main_wiki_page(self):
        """Generates only the main wiki.html file."""
        self.log("Generating main wiki page...")
        all_sections_html = ""
        classification_map = {
            "Stock": "border-stock",
            "Scout": "border-scout",
            "Recruit": "border-recruit"
        }
        
        # Icon mapping for headers
        icon_map = {
            "Stock Characters": "ph-users-three",
            "Cite Of Reboldouex": "ph-buildings",
            "Port Of Coimbra": "ph-anchor",
            "City of Auch": "ph-city",
            "Ustiur": "ph-tree-palm",
            "Bahamar": "ph-mountains",
            "Los Toldos": "ph-skull",
            "Katovic": "ph-snowflake",
            "Gigante": "ph-island",
            "Unreleased": "ph-lock-key",
            "Unknown": "ph-question"
        }
        
        # Color mapping for headers
        color_map = {
            "Stock Characters": "text-accent-gold",
            "Unreleased": "text-accent-red",
            "Unknown": "text-gray-500"
        }

        for group_name in CHARACTER_GROUPS:
            # Filter out hidden characters
            chars_in_group = [c for c in self.characters.values() if c['group'] == group_name and not c.get('hidden', False)]
            if not chars_in_group: continue

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
            sorted_chars = sorted(chars_in_group, key=lambda x: x.get('sort_order', 999))

            for char_data in sorted_chars:
                border_class = classification_map.get(char_data.get("classification", "Stock"))
                char_id = os.path.splitext(char_data['icon'])[0].lower().replace('_', '-')
                clean_id = char_id.replace("spr-icon-pc-", "")
                
                # Add opacity for unreleased
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

        wiki_content = WIKI_TEMPLATE.format(
            common_head=COMMON_HEAD,
            character_sections=all_sections_html
        )
        with open(os.path.join(self.site_root, "wiki.html"), 'w', encoding='utf-8') as f:
            f.write(wiki_content)
        self.log("Main wiki page generation complete.")

    def run_generation_process(self):
        """Generates all individual character pages."""
        self.log("--- Starting HTML Generation ---")
        self.generate_button.setEnabled(False)
        
        # Output folder is site_root/characters
        char_dir = os.path.join(self.site_root, "characters")
        if not os.path.exists(char_dir):
            os.makedirs(char_dir)
        
        classification_map = {
            "Stock": "border-stock",
            "Scout": "border-scout",
            "Recruit": "border-recruit"
        }

        count = 0
        for char_id, data in self.characters.items():
            self.log(f"Generating page for {data['name']}...")
            portrait_filename = data['icon'].replace("SPR_Icon", "IMG_Portrait")
            
            # Check for portrait in site_root/images/portrait
            full_portrait_path = os.path.join(self.site_root, "images", "portrait", portrait_filename)
            
            # HTML path remains relative for browser
            image_path = f"../images/portrait/{portrait_filename}" if os.path.exists(full_portrait_path) else f"../images/icons/{data['icon']}"
            
            border_class = classification_map.get(data.get("classification", "Stock"))
            
            content = CHARACTER_TEMPLATE.format(
                common_head=COMMON_HEAD,
                name=data['name'],
                image_path=image_path,
                border_class=border_class
            )
            
            clean_id = char_id.replace("spr-icon-pc-", "")
            with open(os.path.join(char_dir, f"{clean_id}.html"), 'w', encoding='utf-8') as f:
                f.write(content)
            count += 1
            
        self.generate_main_wiki_page()

        self.log(f"--- HTML Generation Complete ({count} pages) ---")
        self.generate_button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

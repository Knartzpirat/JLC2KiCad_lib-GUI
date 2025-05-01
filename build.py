import subprocess
import os

basedir = os.path.dirname(__file__)
ui_file = os.path.join("UI", "JLC2KiCad-GUI.ui")
icon_file = os.path.join("UI", "icon.ico")

cmd = [
    "pyinstaller",
    "gui_main.py",                 # <-- Hauptskript
    "--noconsole",
    "--onefile",
    "--name", "JLC2KiCadGUI",
    "--icon", icon_file,
    "--distpath", "dist",         # <-- Zielordner
    "--workpath", "build/temp",   # <-- Temporärer Build-Ordner
    "--add-data", f"{ui_file};UI" # <-- Ressourcen einbinden
]

subprocess.run(cmd)
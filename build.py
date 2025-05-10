import subprocess, os, sys

basedir = os.path.dirname(os.path.abspath(__file__))
ui_file     = os.path.join(basedir, "UI", "JLC2KiCad-GUI.ui")
icon_file   = os.path.join(basedir, "UI", "icon.ico")
pixmap_file = os.path.join(basedir, "UI", "icon.png")
pkg_folder  = os.path.join(basedir, "JLC2KiCadLib")

cmd = [
    "pyinstaller",
    "gui_main.py",
    "--onefile",
    "--noconsole",
    "--name", "JLC2KiCadGUI",
    "--version", "version_info.txt",
    "--icon", icon_file,
    "--distpath", os.path.join(basedir, "dist"),
    "--workpath", os.path.join(basedir, "build", "temp"),
    "--add-data", f"{ui_file};UI",
    "--add-data", f"{pixmap_file};UI",
    # "--add-data", f"{pkg_folder};JLC2KiCadLib",
    "--collect-all", "JLC2KiCadLib"
]

# Starte den Build
result = subprocess.run(cmd, shell=(sys.platform == "win32"))
if result.returncode != 0:
    print("Fehler beim Erstellen der EXE:", result.stderr)
else:
    print("Build erfolgreich! EXE liegt in:", os.path.join(basedir, "dist"))

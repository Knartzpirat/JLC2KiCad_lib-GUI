import subprocess, os, sys

basedir     = os.path.dirname(os.path.abspath(__file__))
version_fn  = os.path.join(basedir, "version_info.txt")
ui_file     = os.path.join(basedir, "UI", "JLC2KiCad-GUI.ui")
icon_file   = os.path.join(basedir, "UI", "icon.ico")
pixmap_file = os.path.join(basedir, "UI", "icon.png")
pkg_folder  = os.path.join(basedir, "JLC2KiCadLib")

cmd = [
    "pyinstaller",
    "--clean",
    "--log-level=DEBUG",
    "gui_main.py",
    "--onefile",
    "--noconsole",
    "--name", "JLC2KiCadGUI",
    "--version-file", version_fn,
    "--icon", icon_file,
    "--distpath", os.path.join(basedir, "dist"),
    "--workpath", os.path.join(basedir, "build", "temp"),
    "--add-data", f"{ui_file};UI",
    "--add-data", f"{pixmap_file};UI",
    "--add-data", f"{pkg_folder};JLC2KiCadLib",
    "--collect-all", "JLC2KiCadLib"
]

print("\nBuild-Command:", " ".join(cmd))

# start build
result = subprocess.run(
    cmd,
    #shell=False,  # Avoid using shell=True for security reasons
    # " ".join(cmd), 
    shell=(sys.platform == "win32"), 
    text=True,  # Ensure output is returned as text instead of bytes
    capture_output=True,
)

# Print the output
print("stdout:", result.stdout)
print("stderr:", result.stderr)

if result.returncode != 0:
    print("Fehler beim Erstellen der EXE:", result.stderr)
else:
    exe_path = os.path.join(basedir, "dist", "JLC2KiCadGUI.exe")
    print("Done. EXE hier:", exe_path, "Exists?", os.path.exists(exe_path))

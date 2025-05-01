import sys
import os
import subprocess
from typing import Optional
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QFile, QIODevice, QCoreApplication, QSettings
from PySide6.QtWidgets import (
    QApplication, QDialog,
    QLineEdit, QPushButton, QDialogButtonBox, QComboBox, QCheckBox,
    QFileDialog, QMessageBox, QWidget
)
from PySide6.QtUiTools import QUiLoader

# Stelle Organisation und App-Name für QSettings ein
QCoreApplication.setOrganizationName("Knartz Software Bude")
QCoreApplication.setApplicationName("JLC2KiCadGUI")

class CommandBuilder:
    def __init__(
        self,
        part_number: str,
        output_dir: str,
        symbol_lib: str,
        use_log_file: bool,
        logging_level: str,
        skip_existing: bool
    ):
        self.part_number = part_number
        self.output_dir = output_dir
        self.symbol_lib = symbol_lib
        self.use_log_file = use_log_file
        self.logging_level = logging_level
        self.skip_existing = skip_existing

    def build(self) -> str:
        # Basisbefehl und Part-Nummer
        cmd = ["JLC2KiCadLib", self.part_number]
        # Ausgabeordner
        cmd += ["-dir", self.output_dir]
        # Symbolbibliothek
        cmd += ["-symbol_lib", self.symbol_lib]
        # Log-Optionen
        if self.use_log_file:
            cmd.append("--log_file")
        cmd += ["-logging_level", self.logging_level]
        # Skip-existing-Flag
        if self.skip_existing:
            cmd.append("--skip_existing")
        return " ".join(cmd)

class Widget(QDialog):
    def __init__(self, ui_filename: str, parent: Optional[QWidget] = None):
        super(Widget, self).__init__(parent)
        self.setWindowTitle("JLC2KiCad GUI")
        my_pixmap = QPixmap("UI/icon.png")
        my_icon = QIcon(my_pixmap)

        self.setWindowIcon(my_icon)
        # QSettings für persistenten Speicher
        self.settings = QSettings()

        # UI laden
        ui_path = os.path.join(os.path.dirname(__file__), ui_filename)
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise IOError(f"Cannot open UI file {ui_path}: {ui_file.errorString()}")
        loader = QUiLoader()
        try:
            loaded_ui = loader.load(ui_file, self)
        except Exception as e:
            raise RuntimeError(f"Failed to load UI: {e}")
        finally:
            ui_file.close()
        layout = loaded_ui.layout()
        if layout is not None:
            self.setLayout(layout)

        # Widgets referenzieren
        self.part_input = self.findChild(QLineEdit, 'lineEdit_PartNumber')
        self.output_dir_input = self.findChild(QLineEdit, 'lineEdit_outputDir')
        self.symbol_bib_input = self.findChild(QLineEdit, 'lineEdit_SymbolBib')
        self.dir_button = self.findChild(QPushButton, 'pushButton_DirChoice')
        self.logfile_checkbox = self.findChild(QCheckBox, 'checkBox_LogFile')
        self.loglevel_combo = self.findChild(QComboBox, 'comboBox_LogLevel')
        self.skip_existing_checkbox = self.findChild(QCheckBox, 'checkBox_SkipExisting')
        self.button_box = self.findChild(QDialogButtonBox, 'buttonBox_Process')

        # Lade gespeicherten Ausgabeordner, falls vorhanden
        last_dir = str(self.settings.value("output_dir", type=str))
        if last_dir and os.path.isdir(last_dir) and self.output_dir_input:
            self.output_dir_input.setText(last_dir)
            self._load_symbol_bib(last_dir)

        # Signale verbinden
        if self.dir_button:
            self.dir_button.clicked.connect(self.choose_output_dir)
        if self.button_box:
            self.button_box.accepted.connect(self.process)
            self.button_box.rejected.connect(self.reject)

    def choose_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select output directory", os.getcwd())
        if directory and self.output_dir_input:
            self.output_dir_input.setText(directory)
            # Speichere Auswahl
            self.settings.setValue("output_dir", directory)
            self._load_symbol_bib(directory)

    def _load_symbol_bib(self, directory: str) -> None:
        symbol_folder = os.path.join(directory, 'symbol')
        if os.path.isdir(symbol_folder) and self.symbol_bib_input:
                sym_files = [f for f in os.listdir(symbol_folder) if f.lower().endswith('.kicad_sym')]
                if sym_files:
                    self.symbol_bib_input.setText(os.path.splitext(sym_files[0])[0])

    def process(self):
        part = (self.part_input.text().strip() if self.part_input else '')
        out_dir = (self.output_dir_input.text().strip() if self.output_dir_input else '')
        symbol = (self.symbol_bib_input.text().strip() if self.symbol_bib_input else '')
        use_log = (self.logfile_checkbox.isChecked() if self.logfile_checkbox else False)
        level = (self.loglevel_combo.currentText() if self.loglevel_combo else 'INFO')
        skip = (self.skip_existing_checkbox.isChecked() if self.skip_existing_checkbox else False)

        # Erzeuge CLI-Argumente
        builder = CommandBuilder(
            part_number=part,
            output_dir=out_dir,
            symbol_lib=symbol,
            use_log_file=use_log,
            logging_level=level,
            skip_existing=skip
        )
        cmd = builder.build()
        print("Generated command:", cmd)
        # CLI-Skript aus dem Fork aufrufen
        
        try:
            # Prozess starten und Ausgaben abfangen
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            # Warten & Ausgaben lesen
            stdout, stderr = proc.communicate()
            retcode = proc.returncode

            # Ausgabe zusammenfassen (z.B. erst 5 Zeilen stdout)
            out_lines = stdout.splitlines()
            summary = "\n".join(out_lines[:5] + (["..."] if len(out_lines)>5 else []))

            if retcode == 0:
                QMessageBox.information(
                    self, "Erfolg",
                    f"Komponente {part} verarbeitet.\n\n"
                    f"Ausgabe (erste 5 Zeilen):\n{summary}"
                )
            else:
                err_lines = stderr.splitlines()
                err_summary = "\n".join(err_lines[-5:])
                QMessageBox.critical(
                    self, "Fehler",
                    f"Prozess abgebrochen mit Exit-Code {retcode}.\n\n"
                    f"Letzte 5 Fehler-Zeilen:\n{err_summary}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Fehler",
                f"Start fehlgeschlagen:\n{e}"
            )
        finally:
            self.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = Widget(ui_filename="UI/JLC2KiCad-GUI.ui")
    dialog.exec()
    sys.exit(0)

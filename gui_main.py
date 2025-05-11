import sys
import os
from typing import Optional
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import QFile, QIODevice, QCoreApplication, QSettings
from PySide6.QtWidgets import (
    QApplication, QDialog,
    QLineEdit, QPushButton, QDialogButtonBox, QComboBox, QCheckBox,
    QFileDialog, QMessageBox, QWidget, QTabWidget, QListWidget, QRadioButton, QListWidgetItem
)
from PySide6.QtUiTools import QUiLoader

# Importiere main direct from project
from JLC2KiCadLib.JLC2KiCadLib import main as jlc_main

# set application and organization name 
QCoreApplication.setOrganizationName("Knartz Software Bude")
QCoreApplication.setApplicationName("JLC2KiCadGUI")

class CommandBuilder:
    def __init__(
        self,
        part_number: str,
        output_dir: str,
        symbol_lib: str,
        symbol_dir: str,
        footprint_dir: str,
        model_dir: str,
        model_var: str,
        model_type: str,
        use_log_file: bool,
        logging_level: str,
        skip_existing: bool,
        download_symbols: bool,
        download_footprint: bool
    ):
        self.part_number = part_number
        self.output_dir = output_dir
        self.symbol_lib = symbol_lib
        self.symbol_dir = symbol_dir
        self.footprint_dir = footprint_dir
        self.model_dir = model_dir
        self.model_var = model_var
        self.model_type = model_type
        self.use_log_file = use_log_file
        self.logging_level = logging_level
        self.skip_existing = skip_existing
        self.download_symbols = download_symbols
        self.download_footprint = download_footprint

    def build(self) -> list[str]:
        cmd = ["JLC2KiCadLib", self.part_number]
        cmd += ["-dir", self.output_dir]
        if self.symbol_lib:
            cmd += ["-symbol_lib", self.symbol_lib]
        if self.symbol_dir:
            cmd += ["-symbol_lib_dir", self.symbol_dir]
        if not self.download_symbols:
            cmd.append("--no_symbol")

        if not self.download_footprint:
            cmd.append("--no_footprint")
        else:
            cmd += ["-footprint_lib", self.footprint_dir]
            if self.model_type == "NO":
                cmd.append("--models")
            else:
                cmd += ["-models", self.model_type]
            cmd += ["-model_dir", self.model_dir]
            cmd += ["-model_base_variable", self.model_var]

        if self.use_log_file:
            cmd.append("--log_file")
            cmd += ["-logging_level", self.logging_level]
        
        if self.skip_existing:
            cmd.append("--skip_existing")
        
        
        
        
        

        return cmd

class Widget(QDialog):
    def __init__(self, ui_filename: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("JLC2KiCad GUI")

        # Ressourcen-Pfad (bei frozen mode)
        if getattr(sys, 'frozen', False):
            basedir = getattr(sys, '_MEIPASS', "") or ""
        else:
            basedir = os.path.dirname(__file__) or ""

        icon_path = os.path.join(basedir, "UI", "icon.png")
        self.setWindowIcon(QIcon(QPixmap(icon_path)))

        # QSettings für persistenten Speicher
        self.settings = QSettings()

        # UI laden
        ui_path = os.path.join(os.path.dirname(__file__), ui_filename)
        ui_file = QFile(ui_path)
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise IOError(f"Cannot open UI file {ui_path}: {ui_file.errorString()}")
        loader = QUiLoader()
        loaded_ui = loader.load(ui_file, self)
        ui_file.close()
        layout = loaded_ui.layout()
        if layout is not None:
            self.setLayout(layout)

        # Widgets referenzieren
        self.part_input             = self.findChild(QLineEdit,         'lineEdit_PartNumber_Input')
        self.output_dir_input       = self.findChild(QLineEdit,         'lineEdit_Browse_Output')
        self.symbol_lib_input       = self.findChild(QLineEdit,         'lineEdit_SymbolLIB_Input')
        self.symbol_dir_input       = self.findChild(QLineEdit,         'lineEdit_SymbolDIR_Input')
        self.footprint_dir_input    = self.findChild(QLineEdit,         'lineEdit_FootprintDIR_Input')
        self.model_dir_input        = self.findChild(QLineEdit,         'lineEdit_ModelDIR_Input')
        self.model_var_input        = self.findChild(QLineEdit,         'lineEdit_ModelVAR_Input')
        self.browse_button          = self.findChild(QPushButton,       'pushButton_Browse_Output')
        self.logfile_checkbox       = self.findChild(QCheckBox,         'checkBox_LogFile')
        self.loglevel_combo         = self.findChild(QComboBox,         'comboBox_LogLevel')
        self.skip_existing_checkbox = self.findChild(QCheckBox,         'checkBox_SkipExisting')
        self.button_box             = self.findChild(QDialogButtonBox,  'buttonBox_Process')
        self.download_symbol        = self.findChild(QCheckBox,         'checkBox_Symbol')
        self.download_footprint     = self.findChild(QCheckBox,         'checkBox_Footprint')
        self.model_step_rb          = self.findChild(QRadioButton,      'radioButton_Model_step')
        self.model_any_rb           = self.findChild(QRadioButton,      'radioButton_Model_any')
        self.model_wrl_rb           = self.findChild(QRadioButton,      'radioButton_Model_wrl')
        self.tab_widget             = self.findChild(QTabWidget,        'tabWidget')
        self.list_widget            = self.findChild(QListWidget,       'listWidget')
        # Initiales Füllen des output-Dir-Felds
        start_dir = self._get_start_dir()
        if self.output_dir_input:
            self.output_dir_input.setText(start_dir)
        # und die Symbol-Lib ggf. laden
        
        libs = self._load_symbol_lib(start_dir)
        if libs > 0:
            footprint_dir = self._load_footprint_dir(start_dir)
            self._load_model_dir(start_dir, footprint_dir)
        
        model_var = str(self.settings.value("model_var", type=str))
        if self.model_var_input:
            self.model_var_input.setText(model_var)

        # ── Lade gespeicherte Checkbox- und Radiobutton-Einstellungen ──
        if self.logfile_checkbox:
            self.logfile_checkbox.setChecked(bool(self.settings.value("use_log_file", True)))
        if self.loglevel_combo:
            level = self.settings.value("logging_level", "INFO", type=str)
            index = self.loglevel_combo.findText(str(level))
            if index >= 0:
                self.loglevel_combo.setCurrentIndex(index)
        if self.skip_existing_checkbox:
            self.skip_existing_checkbox.setChecked(bool(self.settings.value("skip_existing", True)))
        if self.download_symbol:
            self.download_symbol.setChecked(bool(self.settings.value("download_symbols", True)))
        if self.download_footprint:
            self.download_footprint.setChecked(bool(self.settings.value("download_footprint", True)))

        # Model-Type RadioButtons
        stored_type = self.settings.value("model_type", "STEP", type=str)
        if stored_type == "STEP" and self.model_step_rb:
            self.model_step_rb.setChecked(True)
        elif stored_type == "NO" and self.model_any_rb:
            self.model_any_rb.setChecked(True)
        elif stored_type == "WRL" and self.model_wrl_rb:
            self.model_wrl_rb.setChecked(True)

        # Signale verbinden
        if self.browse_button:
            self.browse_button.clicked.connect(self.choose_output_dir)
        if self.button_box:
            self.button_box.accepted.connect(self.process)
            self.button_box.rejected.connect(self.reject)

        if self.list_widget and self.symbol_lib_input:
        # Wenn der Nutzer eine Zeile anklickt
            self.list_widget.currentItemChanged.connect(self._on_symbol_selected)


    def choose_output_dir(self) -> None:
        """
        Öffnet den Verzeichniswahl-Dialog. Wenn kein start_dir übergeben
        wird, wird _get_start_dir() als Default benutzt.
        """
        
        start_dir = self._get_start_dir()

        directory = QFileDialog.getExistingDirectory(
            parent=self,
            caption="Select output directory",
            dir=start_dir,
            options=QFileDialog.Option.ShowDirsOnly
        )

        if directory and self.output_dir_input:
            self.output_dir_input.setText(directory)
            self.settings.setValue("output_dir", directory)
            
            libs = self._load_symbol_lib(directory)
            if libs > 0:
                footprint_dir = self._load_footprint_dir(directory)
                self._load_model_dir(directory, footprint_dir)
            

    def _on_symbol_selected(self, current: Optional[QListWidgetItem], previous: Optional[QListWidgetItem]) -> None:
        """
        Wird aufgerufen, wenn der Nutzer im QListWidget einen Eintrag auswählt.
        Schreibt den Text des aktuellen Items in das symbol_lib_input.
        """
        if current and self.symbol_lib_input:
            self.symbol_lib_input.setText(current.text())


    def _get_start_dir(self) -> str:
        """
        Gibt entweder den zuletzt gespeicherten output_dir_input zurück,
        oder [falls dieser ungültig ist] das Dokumente-Verzeichnis.
        """
        # Versuch, gespeicherten Pfad zu laden
        last_dir = str(self.settings.value("output_dir", type=str))
        if last_dir and os.path.isdir(last_dir):
            return last_dir
        else:
            # Fallback: Dokumente-Ordner
            if sys.platform == 'win32':
                return os.path.join(os.environ.get("USERPROFILE", ""), "Documents")
            else:
                return os.path.expanduser("~/Documents")


    def _load_symbol_lib(self, directory: str) -> int:
        symbol_dir = self._load_symbol_dir(directory)
        symbol_folder = os.path.join(directory, symbol_dir)
        if self.list_widget:
            self.list_widget.clear()
        count = 0
        if os.path.isdir(symbol_folder) and self.symbol_lib_input:
            sym_files = [f for f in os.listdir(symbol_folder) if f.lower().endswith('.kicad_sym')]
            count = int(len(sym_files))
            if sym_files:
                self.symbol_lib_input.setText(os.path.splitext(sym_files[0])[0])
                for fname in sym_files:
                    if self.list_widget:
                        self.list_widget.addItem(os.path.splitext(fname)[0])
        else:
            if self.symbol_lib_input:
                self.symbol_lib_input.clear()
            if self.symbol_dir_input:
                self.symbol_dir_input.clear()
            if self.footprint_dir_input:
                self.footprint_dir_input.clear()
            if self.model_dir_input:
                self.model_dir_input.clear()

        tab_widget = self.findChild(QTabWidget, 'tabWidget')
        if tab_widget:
            new_title = f"({count}) Symbol Libs found"
            tab_widget.setTabText(1, new_title)
        return count

    
    def _load_symbol_dir(self, directory: str) -> str:
        """
        Ermittelt ein Verzeichnis mit 'symbol' im Namen im Ordner `directory`.
        Falls keines existiert, wird geprüft, ob in den QSettings unter 'symbol_dir'
        ein gültiger Pfad steht. Andernfalls wird 'symbol' als Default benutzt.
        """
        candidates = [
            name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))
            and 'symbol' in name.lower()
        ]
        if candidates:
            chosen = candidates[0]
            path = chosen
        else:
            saved = self.settings.value("symbol_dir", type=str)
            if saved:
                path = saved
            else:
                path = ''
        # Trage das Ergebnis in dein QLineEdit ein
        if self.symbol_dir_input:
            self.symbol_dir_input.setText(str(path))
        # Speichere den tatsächlichen Pfad für später
        self.settings.setValue("symbol_dir", path)
        return str(path)


    def _load_footprint_dir(self, directory: str) -> str:
        """
        Ermittelt ein Verzeichnis mit 'footprint' im Namen im Ordner `directory`.
        Falls keines existiert, wird geprüft, ob in den QSettings unter 'footprint_dir'
        ein gültiger Pfad steht. Andernfalls wird 'footprint' als Default benutzt.
        """
        candidates = [
            name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))
            and 'footprint' in name.lower()
        ]
        if candidates:
            chosen = candidates[0]
            path = chosen
        else:
            saved = self.settings.value("footprint_dir", type=str)
            if saved:
                path = saved
            else:
                path = ''
        # Trage das Ergebnis in dein QLineEdit ein
        if self.footprint_dir_input:
            self.footprint_dir_input.setText(str(path))
        # Speichere den tatsächlichen Pfad für später
        self.settings.setValue("footprint_dir", path)
        return str(path)
        


    def _load_model_dir(self, directory: str, footprint_dir: str) -> None:
        """
        Ermittelt ein Verzeichnis mit '3D' oder 'model' im Namen im Ordner `directory`.
        Falls keines existiert, wird geprüft, ob in den QSettings unter 'footprint_dir'
        ein gültiger Pfad steht. Andernfalls wird 'footprint' als Default benutzt.
        """
        footprint_dir = os.path.join(directory, footprint_dir)
        if not os.path.exists(footprint_dir):
            if self.footprint_dir_input:
                self.footprint_dir_input.clear()
            if self.model_dir_input:
                self.model_dir_input.clear()
            return
        
        candidates = [
            name for name in os.listdir(footprint_dir)
            if os.path.isdir(os.path.join(footprint_dir, name))
            and ('3d' in name.lower() or 'model' in name.lower())
        ]
        if candidates:
            chosen = candidates[0]
            path = chosen
        else:
            saved = self.settings.value("model_dir", type=str)
            if saved:
                path = saved
            else:
                path = ''

        # Trage das Ergebnis in dein QLineEdit ein
        if self.model_dir_input:
            self.model_dir_input.setText(str(path))
        # Speichere den tatsächlichen Pfad für später
        self.settings.setValue("model_dir", path)


    def _get_model_type(self) -> str:
        if self.model_step_rb and self.model_step_rb.isChecked():
            return 'STEP'
        elif self.model_any_rb and self.model_any_rb.isChecked():
            return 'NO'
        elif self.model_wrl_rb and self.model_wrl_rb.isChecked():
            return 'WRL'
        else:
            return 'STEP'


    def process(self):
        part    = (self.part_input.text().strip() if self.part_input else '')
        out     = (self.output_dir_input.text().strip() if self.output_dir_input else '')

            # Überprüfen, ob part und out nicht leer sind
        if not part:
            QMessageBox.warning(self, "Error", "Part Number cannot be empty.")
            return  # Abbruch, Fenster bleibt offen
        if not out:
            QMessageBox.warning(self, "Error", "Output Directory cannot be empty.")
            return  # Abbruch, Fenster bleibt offen

        lib     = (self.symbol_lib_input.text().strip() if self.symbol_lib_input else '')
        sym     = (self.symbol_dir_input.text().strip() if self.symbol_dir_input else '')
        ftp     = (self.footprint_dir_input.text().strip() if self.footprint_dir_input else '')
        mod     = (self.model_dir_input.text().strip() if self.model_dir_input else '')
        mod_var = (self.model_var_input.text().strip() if self.model_var_input else '')
        mod_type = self._get_model_type()
        use     = (self.logfile_checkbox.isChecked() if self.logfile_checkbox else False)
        lvl     = (self.loglevel_combo.currentText() if self.loglevel_combo else 'INFO')
        skip    = (self.skip_existing_checkbox.isChecked() if self.skip_existing_checkbox else False)
        dwn_sym = (self.download_symbol.isChecked() if self.download_symbol else False)
        dwn_ftp = (self.download_footprint.isChecked() if self.download_footprint else False)

        if self.output_dir_input:
            self.settings.setValue("output_dir", self.output_dir_input.text().strip())
        if self.symbol_dir_input:
            self.settings.setValue("symbol_dir", self.symbol_dir_input.text().strip())
        if self.footprint_dir_input:
            self.settings.setValue("footprint_dir", self.footprint_dir_input.text().strip())
        if self.model_dir_input:
            self.settings.setValue("model_dir", self.model_dir_input.text().strip())
        if self.model_var_input:
            self.settings.setValue("model_var", self.model_var_input.text().strip())

        # Checkboxen und Radiobuttons
        if self.logfile_checkbox:
            self.settings.setValue("use_log_file", self.logfile_checkbox.isChecked())
        if self.loglevel_combo:
            self.settings.setValue("logging_level",     self.loglevel_combo.currentText())
        if self.skip_existing_checkbox:
            self.settings.setValue("skip_existing",     self.skip_existing_checkbox.isChecked())
        if self.download_symbol:
            self.settings.setValue("download_symbols",  self.download_symbol.isChecked())
        if self.download_footprint:
            self.settings.setValue("download_footprint", self.download_footprint.isChecked())
        if self.model_step_rb:
            self.settings.setValue("model_type",        self._get_model_type())

        cmd = CommandBuilder(part, out, lib, sym, ftp, mod, mod_var, mod_type, use, lvl, skip, dwn_sym, dwn_ftp).build()
        print(f"\nGenerated command: {cmd}\n" )

        old_argv = sys.argv.copy()
        try:
            sys.argv = cmd
            jlc_main()
            QMessageBox.information(self, "Complete", f"Component {part} has been processed.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Processing failed:\n{e}")
        finally:
            sys.argv = old_argv
            self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = Widget(ui_filename="UI/JLC2KiCad-GUI.ui")
    dlg.exec()
    sys.exit(0)

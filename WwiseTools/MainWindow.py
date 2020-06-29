import sys
import traceback
from waapi import WaapiClient, CannotConnectToWaapiException
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from QtDesign.MainWindow_ui import Ui_MainWindow
from SelectionCommands.CreateBanks import create_banks
from SelectionCommands.GetBankSize import get_bank_size
from SelectionCommands.ApplySourceEdit import apply_source_edit



if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.client = None
        self.selectedObjects = []

    def connect_to_wwise(self):
        url = "ws://127.0.0.1:" + str(self.spbWaapiPort.value()) + "/waapi"
        try:
            self.client = WaapiClient(url=url)
            self.lblWaapiStatus.setText("Wwise connected successfully")
        except CannotConnectToWaapiException:
            self.lblWaapiStatus.setText("Wwise fails to connect...")

    def get_selected_objects(self):
        self.selectedObjects = self.client.call("ak.wwise.ui.getSelectedObjects")['objects']

    def create_bank_per_object(self):
        if not self.client:
            return
        self.get_selected_objects()
        create_banks(self.client, self.selectedObjects)

    def calculate_bank_size(self):
        if not self.client:
            return
        self.get_selected_objects()
        get_bank_size(self.client, self.selectedObjects)

    def apply_source_edits(self):
        if not self.client:
            return
        self.get_selected_objects()
        apply_source_edit(self.client, self.selectedObjects)


sys.excepthook = traceback.print_exception


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

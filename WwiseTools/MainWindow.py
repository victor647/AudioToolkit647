import sys
import traceback
from waapi import WaapiClient, CannotConnectToWaapiException
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow
from QtDesign.MainWindow_ui import Ui_MainWindow
from SelectionCommands.CreateBanks import create_banks
from SelectionCommands.GetBankSize import get_bank_size
from SelectionCommands.ApplySourceEdit import apply_source_edit
from SelectionCommands.AutoAssignSwitch import auto_assign_switch
from SelectionCommands.ApplyNamingConvention import rename_to_camel_case, rename_to_lower_case
import ScriptingTools

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.client = None
        self.activeObjects = []
        self.statusbar.showMessage('未连接到Wwise...')
        self.cbbDescendantType.addItems(['ActorMixer', 'AudioSource', 'BlendContainer', 'Folder',
                                         'MusicPlaylistContainer', 'MusicSegment', 'MusicSwitchContainer', 'MusicTrack',
                                         'Sound', 'SwitchContainer', 'WorkUnit'])

    # 通过指定的端口连接到Wwise
    def connect_to_wwise(self):
        url = 'ws://127.0.0.1:' + str(self.spbWaapiPort.value()) + '/waapi'
        try:
            self.client = WaapiClient(url=url)
            self.statusbar.showMessage('已成功连接Wwise！')
        except CannotConnectToWaapiException:
            self.statusbar.showMessage('无法连接到Wwise...')

    # 获取Wwise中选中的对象
    def get_selected_objects(self):
        self.activeObjects = ScriptingTools.get_selected_objects(self.client)
        self.update_object_list()

    # 清空操作对象列表
    def clear_object_list(self):
        self.activeObjects = []
        self.lstActiveObjects.clear()

    def update_object_list(self):
        self.lstActiveObjects.clear()
        for obj in self.activeObjects:
            self.lstActiveObjects.addItem(obj['path'])

    def open_in_multi_editor(self):
        if self.client:
            ScriptingTools.open_in_multi_editor(self.client, self.activeObjects)

    def create_bank_per_object(self):
        if self.client:
            create_banks(self.client, self.activeObjects)

    def calculate_bank_size(self):
        if self.client:
            get_bank_size(self.client, self.activeObjects)

    def apply_source_edits(self):
        if self.client:
            apply_source_edit(self.client, self.activeObjects)

    def assign_switch_container(self):
        if self.client:
            auto_assign_switch(self.client, self.activeObjects)

    def filter_selection(self):
        if self.client:
            self.activeObjects = ScriptingTools.filter_objects_by_name(self.activeObjects, self.iptSelectionFilter.text(), self.cbxCaseSensitive.isChecked())
            ScriptingTools.select_objects(self.client, self.activeObjects)
            self.update_object_list()

    def select_descendants_by_type(self):
        if self.client:
            all_descendants = []
            for obj in self.activeObjects:
                for descendant in ScriptingTools.get_all_descendant_objects(self.client, obj):
                    all_descendants.append(descendant)
            self.activeObjects = ScriptingTools.filter_objects_by_type(all_descendants, self.cbbDescendantType.currentText())
            ScriptingTools.select_objects(self.client, self.activeObjects)
            self.update_object_list()

    def apply_naming_convention(self):
        if self.client:
            if self.rbnAllLowerCase.isChecked():
                rename_to_lower_case(self.client)
            elif self.rbnTitleCase.isChecked():
                rename_to_camel_case(self.client)


sys.excepthook = traceback.print_exception


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

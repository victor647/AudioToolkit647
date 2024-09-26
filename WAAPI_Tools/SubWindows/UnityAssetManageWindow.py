import os.path
from PyQt6.QtWidgets import QDialog, QFileDialog, QTableWidgetItem
from Libraries import WAAPI
from QtDesign.UnityAssetManager_ui import Ui_UnityAssetManager


# 管理Unity中的Asset文件
class UnityAssetManager(QDialog, Ui_UnityAssetManager):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__workDir = ''
        self.tblFileList.resizeColumnsToContents()

    def setup_triggers(self):
        self.btnSelectAssetFolder.clicked.connect(self.select_folder)
        self.btnDeleteSelected.clicked.connect(self.delete_selection)

    # 设置Unity Wwise资源文件夹
    def select_folder(self):
        self.__workDir = QFileDialog.getExistingDirectory()
        if self.__workDir is None:
            return
        for subfolder in os.listdir(self.__workDir):
            if '.' not in subfolder:
                subfolder_path = os.path.join(self.__workDir, subfolder)
                for file in os.listdir(subfolder_path):
                    if file.endswith('.asset'):
                        self.add_file(file, subfolder)

    # 在表中添加文件
    def add_file(self, file_path: str, asset_type: str):
        row = self.tblFileList.rowCount()
        self.tblFileList.setRowCount(row + 1)
        file_guid = file_path.rstrip('.asset')
        obj = WAAPI.get_full_info_from_obj_id('{' + file_guid + '}')
        if obj:
            obj_name = obj['name']
            status = '正常'
        else:
            full_path = os.path.join(self.__workDir, asset_type, file_path)
            with open(full_path) as text:
                obj_name = text.readlines()[13].lstrip('  objectName: ').rstrip()
            status = '多余'
        self.tblFileList.setItem(row, 0, QTableWidgetItem(obj_name))
        self.tblFileList.setItem(row, 1, QTableWidgetItem(asset_type))
        self.tblFileList.setItem(row, 2, QTableWidgetItem(status))
        self.tblFileList.setItem(row, 3, QTableWidgetItem(file_guid))

    # 删除选中的文件
    def delete_selection(self):
        for item in self.tblFileList.selectedItems():
            row = item.row()
            subfolder = self.tblFileList.item(row, 1).text()
            file_name = self.tblFileList.item(row, 3).text()
            file = os.path.join(self.__workDir, subfolder, file_name + '.asset')
            os.remove(file)
            os.remove(file + '.meta')
            self.tblFileList.removeRow(row)
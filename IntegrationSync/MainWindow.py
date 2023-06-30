import os.path
import sys, traceback
import json
import mimetypes
import subprocess
import win32api
import filecmp
from shutil import copyfile
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView, QTableWidgetItem

from QtDesign.MainWindow_ui import Ui_MainWindow

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow, Ui_MainWindow):
    __projects = []
    __sourceProject = None
    __targetProject = None

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tblFileList.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setup_triggers()
        self.read_config()

    def setup_triggers(self):
        self.btnMoveAllToTarget.clicked.connect(self.move_all_to_target)
        self.btnSearchForDifference.clicked.connect(self.search_for_difference)
        self.tblFileList.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.cbxSelectAll.stateChanged.connect(self.on_all_checkbox_checked)
        self.cbxNewerFiles.stateChanged.connect(self.on_newer_checkbox_checked)
        self.cbxLargerFiles.stateChanged.connect(self.on_larger_checkbox_checked)
        self.cbxNewFiles.stateChanged.connect(self.on_new_checkbox_checked)

    # 全选勾选框
    def on_all_checkbox_checked(self, state: int):
        self.cbxNewFiles.setChecked(state)
        self.cbxNewerFiles.setChecked(state)
        self.cbxLargerFiles.setChecked(state)
        for row in range(self.tblFileList.rowCount()):
            self.tblFileList.item(row, 0).setCheckState(Qt.Checked if state == 2 else Qt.Unchecked)

    # 更新勾选框
    def on_newer_checkbox_checked(self, state: int):
        for row in range(self.tblFileList.rowCount()):
            source_date = QDateTime.fromString(self.tblFileList.item(row, 3).text(), 'yyyy-MM-dd')
            if self.tblFileList.item(row, 4) is None:
                continue
            else:
                target_date = QDateTime.fromString(self.tblFileList.item(row, 4).text(), 'yyyy-MM-dd')
                if source_date > target_date:
                    self.tblFileList.item(row, 0).setCheckState(Qt.Checked if state == 2 else Qt.Unchecked)

    # 更大勾选框
    def on_larger_checkbox_checked(self, state: int):
        for row in range(self.tblFileList.rowCount()):
            size_text = self.tblFileList.item(row, 2).text()
            if size_text.isnumeric():
                if int(size_text) > 0:
                    self.tblFileList.item(row, 0).setCheckState(Qt.Checked if state == 2 else Qt.Unchecked)

    # 新增勾选框
    def on_new_checkbox_checked(self, state: int):
        for row in range(self.tblFileList.rowCount()):
            status = self.tblFileList.item(row, 2).text()
            if status == '新增':
                self.tblFileList.item(row, 0).setCheckState(Qt.Checked if state == 2 else Qt.Unchecked)

    # 从Projects.json读取项目信息
    def read_config(self):
        file_path = os.path.join(os.path.dirname(__file__), 'Projects.json')
        with open(file_path, 'r') as file:
            config = json.load(fp=file)
            self.__projects = config['Projects']
            for project in self.__projects:
                name_str = f"{project['Name']} ({project['Version']}-{project['Engine']})"
                self.cbbSourceProject.addItems([name_str])
                self.cbbTargetProject.addItems([name_str])
        if len(self.__projects) > 1:
            self.cbbTargetProject.setCurrentIndex(1)

    # 查找差异比对
    def search_for_difference(self):
        self.tblFileList.setRowCount(0)
        self.__sourceProject = self.__projects[self.cbbSourceProject.currentIndex()]
        self.__targetProject = self.__projects[self.cbbTargetProject.currentIndex()]
        row = 0
        for root, dirs, files in os.walk(self.__sourceProject['Path']):
            for file in files:
                mime = mimetypes.guess_type(file)
                if mime[0] == 'text/plain':
                    source_file = os.path.join(root, file)
                    if not self.check_platform_available(source_file):
                        continue

                    target_file = source_file.replace(self.__sourceProject['Path'], self.__targetProject['Path'])
                    target_file_exists = os.path.exists(target_file)

                    self.tblFileList.setRowCount(row + 1)
                    check_item = QTableWidgetItem()
                    check_item.setCheckState(Qt.Checked)
                    self.tblFileList.setItem(row, 0, check_item)
                    self.tblFileList.setItem(row, 1, QTableWidgetItem(source_file.replace(self.__sourceProject['Path'], '')))
                    source_size = os.path.getsize(source_file)
                    if target_file_exists:
                        target_size = os.path.getsize(target_file)
                        size_difference = source_size - target_size
                        if size_difference == 0 and filecmp.cmp(source_file, target_file):
                            self.tblFileList.setItem(row, 2, QTableWidgetItem('一致'))
                        else:
                            self.tblFileList.setItem(row, 2, QTableWidgetItem(str(size_difference)))
                    else:
                        self.tblFileList.setItem(row, 2, QTableWidgetItem('新增'))

                    source_date = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(source_file)))
                    self.tblFileList.setItem(row, 3, QTableWidgetItem(source_date.toString('yyyy-MM-dd')))
                    if target_file_exists:
                        target_date = QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(target_file)))
                        self.tblFileList.setItem(row, 4, QTableWidgetItem(target_date.toString('yyyy-MM-dd')))
                        
                    row += 1

    # 判断是否是区分平台的文件
    def check_platform_available(self, file_path):
        for platform in self.__sourceProject['Platforms']:
            if platform in file_path:
                return platform in self.__targetProject['Platforms']
        return True

    # 将全部选中的文件覆盖到目标工程中
    def move_all_to_target(self):
        count = 0
        for row in range(self.tblFileList.rowCount()):
            if self.tblFileList.item(row, 0).checkState() == Qt.Checked:
                if self.tblFileList.item(row, 2).text() != '一致':
                    count += 1
                    path = self.tblFileList.item(row, 1).text()
                    source_file = os.path.join(self.__sourceProject['Path'], path)
                    target_file = os.path.join(self.__targetProject['Path'], path)
                    copyfile(source_file, target_file)
        win32api.MessageBox(0, '替换了' + str(count) + '个文件', '成功!')

    # 双击文件名进行比对
    def on_item_double_clicked(self, item: QTableWidgetItem):
        if item.column() != 1:
            return
        source_file = os.path.join(self.__sourceProject['Path'], item.text())
        target_file = os.path.join(self.__targetProject['Path'], item.text())
        if not os.path.exists(target_file):
            return
        p = subprocess.Popen('TortoiseMerge.exe ' + source_file + ' ' + target_file,
                             stdout=subprocess.PIPE, shell=True)
        p.communicate()

sys.excepthook = traceback.print_exception

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

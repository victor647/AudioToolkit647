from QtDesign.RenameByTable_ui import Ui_RenameByTable
from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from PyQt6.QtGui import QColor
from Threading.BatchProcessor import BatchProcessor
from Libraries import WAAPI, FileTools, ScriptingHelper
from ObjectTools import EventTools


# 通过读表批量重命名工具
class TableRenamer(QDialog, Ui_RenameByTable):

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__csvData = []
        self.__objects = []
        self.__renamedCount = 0
        self.__removedCount = 0

    def setup_triggers(self):
        self.btnChooseConfig.clicked.connect(self.read_from_table)
        self.btnDoRename.clicked.connect(self.start_renaming)
        self.tblConfigItems.itemDoubleClicked.connect(self.show_object_in_wwise)

    # 读取CSV文件，必须为3列
    def read_from_table(self):
        self.tblConfigItems.setRowCount(0)
        self.__csvData = FileTools.import_from_csv()
        self.__objects = []
        # 带有表头则不读第一行
        if self.cbxHasHeaderRow.isChecked():
            self.__csvData = self.__csvData[1:]

        batch_processor = BatchProcessor(self.__csvData, self.parse_csv_line, '读取表格', self.on_read_finished)
        batch_processor.start()

    # 读表完成后自动设置宽度
    def on_read_finished(self, message: str):
        self.tblConfigItems.resizeColumnsToContents()

    # 逐行读表
    def parse_csv_line(self, data):
        obj_type = self.cbbObjectType.currentText()
        exact_match = self.cbxExactMatch.isChecked()
        if len(data) < 2:
            return
        old_name = data[0]
        new_name = data[1]
        if old_name is None or old_name == '':
            return
        if new_name is None or new_name == '':
            return
        current_row = self.tblConfigItems.rowCount()
        self.tblConfigItems.insertRow(current_row)
        self.tblConfigItems.setItem(current_row, 0, QTableWidgetItem(old_name))
        self.tblConfigItems.setItem(current_row, 1, QTableWidgetItem(new_name))
        old_obj = WAAPI.find_object_by_name_and_type(old_name, obj_type, exact_match)
        new_obj = WAAPI.find_object_by_name_and_type(new_name, obj_type, exact_match)
        if old_obj:
            if new_obj:
                status_item = QTableWidgetItem('新旧都存在')
                status_item.setForeground(QColor(200, 100, 0))
            else:
                status_item = QTableWidgetItem('仅存在旧的')
                status_item.setForeground(QColor(0, 0, 200))
        else:
            if new_obj:
                status_item = QTableWidgetItem('仅存在新的')
                status_item.setForeground(QColor(0, 200, 0))
            else:
                status_item = QTableWidgetItem('都不存在')
                status_item.setForeground(QColor(200, 0, 0))
        self.tblConfigItems.setItem(current_row, 2, status_item)
        self.__objects.append([old_obj, new_obj, old_name, new_name])

    def start_renaming(self):
        self.__renamedCount = 0
        self.__removedCount = 0
        batch_processor = BatchProcessor(self.__objects, self.rename_entry, '进行重命名', self.on_rename_finished)
        batch_processor.start()

    # 对单个进行重命名或删除
    def rename_entry(self, entry):
        old_obj = entry[0]
        new_obj = entry[1]
        old_name = entry[2]
        new_name = entry[3]
        exact_match = self.cbxExactMatch.isChecked()
        if old_obj:
            # 新旧对象都存在，仅删除旧的
            if new_obj:
                WAAPI.delete_object(old_obj)
                self.__removedCount += 1
            # 仅存在旧的事件，重命名成新的
            else:
                WAAPI.rename_object(old_obj, new_name if exact_match else old_obj['name'].replace(old_name, new_name))
                self.__renamedCount += 1

    # 重命名结束回调
    def on_rename_finished(self, message: str):
        ScriptingHelper.show_message_box('重命名完毕', f'共进行{self.__renamedCount}次重命名，删除{self.__removedCount}次旧资源。')

    # 在Wwise中选中列表中双击的对象
    def show_object_in_wwise(self, item: QTableWidgetItem):
        new_obj = WAAPI.find_object_by_name_and_type(item.text(), self.cbbObjectType.currentText(), self.cbxExactMatch.isChecked())
        WAAPI.select_objects_in_wwise([new_obj])




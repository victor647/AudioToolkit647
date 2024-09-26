from QtDesign.RenameByTable_ui import Ui_RenameByTable
from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from Threading.BatchProcessor import BatchProcessor
from Libraries import WAAPI, FileTools, ProjectConventions, ScriptingHelper
from ObjectTools import EventTools


# 通过读表批量重命名工具
class TableRenamer(QDialog, Ui_RenameByTable):

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__data = []
        self.__renamedCount = 0
        self.__removedCount = 0

    def setup_triggers(self):
        self.btnChooseConfig.clicked.connect(self.read_from_table)
        self.btnDoRename.clicked.connect(self.do_rename)

    # 读取CSV文件，必须为3列
    def read_from_table(self):
        self.__data = FileTools.import_from_csv()
        # 带有表头则不读第一行
        if self.cbxHasHeaderRow.isChecked():
            self.__data = self.__data[1:]

        entry_count = len(self.__data)
        self.tblConfigItems.setRowCount(entry_count)
        for i in range(entry_count):
            entry = self.__data[i]
            for j in range(len(entry)):
                self.tblConfigItems.setItem(i - 1, j, QTableWidgetItem(entry[j]))

    def do_rename(self):
        self.__renamedCount = 0
        self.__removedCount = 0
        batch_processor = BatchProcessor(self.__data, self.rename_entry, '读表重命名', self.on_rename_finished)
        batch_processor.start()

    # 对单个进行重命名或删除
    def rename_entry(self, entry):
        old_name = entry[0]
        if old_name == '':
            return
        new_name = entry[1]
        if new_name == '':
            return
        if old_name == new_name:
            return
        # 带有Play前缀则需要加上
        if self.cbxPlayPrefix.isChecked():
            old_name = 'Play_' + old_name
            new_name = 'Play_' + new_name
        if self.cbxHasRoleSuffix.isChecked():
            suffix_1p = ProjectConventions.get_net_role_suffix('1P')
            self.process_object(old_name + suffix_1p, new_name + suffix_1p)
            suffix_3p = ProjectConventions.get_net_role_suffix('3P')
            self.process_object(old_name + suffix_3p, new_name + suffix_3p)
        else:
            self.process_object(old_name, new_name)

    # 处理过名字之后执行操作
    def process_object(self, old_name, new_name):
        old_event = WAAPI.find_object_by_name_and_type(old_name, 'Event')
        new_event = WAAPI.find_object_by_name_and_type(new_name, 'Event')
        if old_event:
            target = EventTools.get_event_targets(old_event)[0]
            # 新旧事件都存在，仅删除旧的
            if new_event:
                WAAPI.delete_object(target)
                WAAPI.delete_object(old_event)
                self.__removedCount += 1
            # 仅存在旧的事件，重命名成新的
            else:
                WAAPI.rename_object(old_event, new_name)
                WAAPI.rename_object(target, target['name'].replace(old_name, new_name))
                self.__renamedCount += 1

    # 重命名结束回调
    def on_rename_finished(self):
        ScriptingHelper.show_message_box('重命名完毕', f'共进行{self.__renamedCount}次重命名，删除{self.__removedCount}次旧资源。')




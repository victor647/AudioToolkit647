import sys, traceback
from waapi import WaapiClient, CannotConnectToWaapiException
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from QtDesign.MainWindow_ui import Ui_MainWindow
from ObjectTools.CommonTools import *
from ObjectTools.AudioSourceTools import *
from ObjectTools.LogicContainerTools import *
from ObjectTools.EventTools import *
from ObjectTools.SoundBankTools import *
from Threading.BatchProcessor import BatchProcessor
from Libraries import ScriptingTools, WaapiTools

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.activeObjects = []
        self.statusbar.showMessage('Wwise not Connected...')
        self.cbbDescendantType.addItems(['All', 'Action', 'ActorMixer', 'AudioFileSource', 'AuxBus', 'BlendContainer', 'Bus', 'Event', 'Folder',
                                         'GameParameter', 'MusicPlaylistContainer', 'MusicSegment', 'MusicSwitchContainer', 'MusicTrack',
                                         'RandomSequenceContainer', 'Sound', 'SoundBank', 'State', 'Switch', 'SwitchContainer', 'WorkUnit'])
        self.cbbDescendantType.setCurrentText('Sound')
        self.tblActiveObjects.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 初始化默认尝试连接wwise
        self.connect_to_wwise()

    def setup_triggers(self):
        self.tblActiveObjects.itemDoubleClicked.connect(self.show_object_in_wwise)

        self.btnWaapiConnect.clicked.connect(self.connect_to_wwise)
        self.btnGetSelectedObjects.clicked.connect(self.get_selected_objects)
        self.btnRemoveSelection.clicked.connect(self.remove_table_selection)
        self.btnClearObjects.clicked.connect(self.clear_object_list)
        self.btnMultiEditor.clicked.connect(self.open_in_multi_editor)
        self.btnBatchRename.clicked.connect(self.open_in_batch_rename)

        self.actConvertToWorkUnit.triggered.connect(lambda: self.convert_to_type('WorkUnit'))
        self.actConvertToActorMixer.triggered.connect(lambda: self.convert_to_type('ActorMixer'))
        self.actConvertToVirtualFolder.triggered.connect(lambda: self.convert_to_type('Folder'))
        self.actConvertToBlendContainer.triggered.connect(lambda: self.convert_to_type('BlendContainer'))
        self.actConvertToRandomSequenceContainer.triggered.connect(lambda: self.convert_to_type('RandomSequenceContainer'))
        self.actConvertToSwitchContainer.triggered.connect(lambda: self.convert_to_type('SwitchContainer'))

        self.btnFindParent.clicked.connect(self.find_parent)
        self.btnFindChildren.clicked.connect(self.find_children)
        self.btnFilterByType.clicked.connect(self.filter_by_type)
        self.btnExcludeByType.clicked.connect(self.exclude_by_type)
        self.btnFilterByName.clicked.connect(self.filter_by_name)
        self.btnExcludeByName.clicked.connect(self.exclude_by_name)

        self.actUndo.triggered.connect(WaapiTools.undo)
        self.actRedo.triggered.connect(WaapiTools.redo)
        self.actDeleteObjects.triggered.connect(self.delete_all_objects)
        self.actMoveToSelection.triggered.connect(self.move_to_selection)
        self.actChangeToLowerCase.triggered.connect(lambda: self.apply_naming_convention(0))
        self.actChangeToTitleCase.triggered.connect(lambda: self.apply_naming_convention(1))
        self.actChangeToUpperCase.triggered.connect(lambda: self.apply_naming_convention(2))

        self.actApplyEditsToOriginal.triggered.connect(self.apply_source_edits)
        self.actResetSourceEdits.triggered.connect(self.reset_source_editor)
        self.actReplaceSourceFiles.triggered.connect(self.replace_source_files)
        self.actRenameOriginalToWwise.triggered.connect(self.rename_original_to_wwise)
        self.actDeleteUnusedAKDFiles.triggered.connect(delete_unused_akd_files)

        self.actBreakContainer.triggered.connect(self.break_container)
        self.actAssignSwitchMappings.triggered.connect(self.assign_switch_mappings)
        self.actRemoveAllSwitchAssignments.triggered.connect(self.remove_all_switch_mappings)
        self.actApplyFaderEditsDownstream.triggered.connect(self.apply_fader_edits_downstream)
        self.actCreatePlayEvent.triggered.connect(self.create_play_event)

        self.actCalculateBankSize.triggered.connect(self.calculate_bank_total_size)
        self.actCreateOrAddToBank.triggered.connect(self.create_or_add_to_bank)
        self.actAddToSelectedBank.triggered.connect(self.add_to_selected_bank)
        self.actClearInclusions.triggered.connect(self.clear_bank_inclusions)
        self.actIncludeMediaOnly.triggered.connect(lambda: self.set_bank_inclusion_type(['media']))
        self.actIncludeEventsAndStructures.triggered.connect(lambda: self.set_bank_inclusion_type(['events', 'structures']))
        self.actIncludeAll.triggered.connect(lambda: self.set_bank_inclusion_type(['events', 'structures', 'media']))
        self.actBankAssignmentMatrix.triggered.connect(self.bank_assignment_matrix)

    # 通过指定的端口连接到Wwise
    def connect_to_wwise(self):
        url = 'ws://127.0.0.1:' + str(self.spbWaapiPort.value()) + '/waapi'
        try:
            WaapiTools.Client = WaapiClient(url=url)
            WaapiTools.Client.subscribe('ak.wwise.core.project.postClosed', self.on_wwise_closed)
            self.statusbar.showMessage('Wwise Connected to ' + WaapiTools.get_project_directory())
            self.btnWaapiConnect.setEnabled(False)
        except CannotConnectToWaapiException:
            self.statusbar.showMessage('Cannot Connect to Wwise...')

    # Wwise关闭时的回调
    def on_wwise_closed(self):
        self.statusbar.showMessage('Wwise not Connected...')
        self.btnWaapiConnect.setEnabled(True)
        WaapiTools.Client = None

    # 获取Wwise中选中的对象
    def get_selected_objects(self):
        if WaapiTools.Client is None:
            return
        self.activeObjects = WaapiTools.get_selected_objects()
        self.update_object_list()

    # 删去表格中选中的对象
    def remove_table_selection(self):
        for item in self.tblActiveObjects.selectedItems():
            self.activeObjects.pop(item.row())
            self.tblActiveObjects.removeRow(item.row())

    # 清空操作对象列表
    def clear_object_list(self):
        self.activeObjects = []
        self.tblActiveObjects.setRowCount(0)

    def update_object_list(self):
        self.tblActiveObjects.setRowCount(0)
        for obj in self.activeObjects:
            row_count = self.tblActiveObjects.rowCount()
            self.tblActiveObjects.insertRow(row_count)
            self.tblActiveObjects.setItem(row_count, 0, QTableWidgetItem(obj['name']))
            self.tblActiveObjects.setItem(row_count, 1, QTableWidgetItem(obj['type']))
            self.tblActiveObjects.setItem(row_count, 2, QTableWidgetItem(obj['path']))

    # 查找和筛选操作
    def find_parent(self):
        if WaapiTools.Client is None:
            return
        if self.cbxKeepSelf.isChecked():
            all_parents = self.activeObjects
        else:
            all_parents = []
        for obj in self.activeObjects:
            for parent in WaapiTools.get_parent_objects(obj, self.cbxRecursiveFind.isChecked()):
                all_parents.append(parent)
        self.activeObjects = all_parents
        self.update_object_list()

    def find_children(self):
        if WaapiTools.Client is None:
            return
        if self.cbxKeepSelf.isChecked():
            all_children = self.activeObjects
        else:
            all_children = []
        for obj in self.activeObjects:
            for child in WaapiTools.get_children_objects(obj, self.cbxRecursiveFind.isChecked()):
                all_children.append(child)
        self.activeObjects = all_children
        self.update_object_list()

    def filter_by_name(self):
        self.activeObjects = ScriptingTools.filter_objects_by_name(self.activeObjects, self.iptSelectionFilter.text(), self.cbxCaseSensitive.isChecked())
        self.update_object_list()

    def exclude_by_name(self):
        self.activeObjects = ScriptingTools.exclude_objects_by_name(self.activeObjects, self.iptSelectionFilter.text(), self.cbxCaseSensitive.isChecked())
        self.update_object_list()

    def filter_by_type(self):
        self.activeObjects = ScriptingTools.filter_objects_by_type(self.activeObjects, self.cbbDescendantType.currentText())
        self.update_object_list()

    def exclude_by_type(self):
        self.activeObjects = ScriptingTools.exclude_objects_by_type(self.activeObjects, self.cbbDescendantType.currentText())
        self.update_object_list()

    def show_object_in_wwise(self, item: QTableWidgetItem):
        if WaapiTools.Client is None:
            return
        if item.column() != 2:
            item = self.tblActiveObjects.item(item.row(), 2)
            WaapiTools.open_item_in_wwise_by_path(item.text())

    # 通用操作
    def convert_to_type(self, target_type: str):
        processor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.convert_to_type(obj, target_type))
        processor.start()

    def delete_all_objects(self):
        processor = BatchProcessor(self.activeObjects, WaapiTools.delete_object)
        processor.start()
        self.clear_object_list()

    def apply_naming_convention(self, naming_rule: int):
        if naming_rule == 0:
            processor = BatchProcessor(self.activeObjects, rename_to_lower_case)
        elif naming_rule == 1:
            processor = BatchProcessor(self.activeObjects, rename_to_title_case)
        else:
            processor = BatchProcessor(self.activeObjects, rename_to_upper_case)
        processor.start()

    def move_to_selection(self):
        if WaapiTools.Client is None:
            return
        selection = WaapiTools.get_selected_objects()
        if len(selection) > 0:
            processor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.move_object(obj, selection[0]))
            processor.start()

    def break_container(self):
        processor = BatchProcessor(self.activeObjects, break_container)
        processor.start()

    def open_in_multi_editor(self):
        if WaapiTools.Client is None:
            return
        WaapiTools.execute_ui_command(self.activeObjects, 'ShowMultiEditor')

    def open_in_batch_rename(self):
        if WaapiTools.Client is None:
            return
        WaapiTools.execute_ui_command(self.activeObjects, 'ShowBatchRename')

    # 音频文件操作
    def apply_source_edits(self):
        processor = BatchProcessor(self.activeObjects, apply_source_edit)
        processor.start()

    def reset_source_editor(self):
        processor = BatchProcessor(self.activeObjects, reset_source_editor)
        processor.start()

    def replace_source_files(self):
        if WaapiTools.Client is None:
            return
        replace_window = ReplaceSourceFile(self.activeObjects)
        replace_window.show()
        replace_window.exec_()

    def rename_original_to_wwise(self):
        if WaapiTools.Client is None:
            return
        processor = BatchProcessor(self.activeObjects, rename_original_to_wwise)
        processor.start()

    # LogicContainer操作
    def assign_switch_mappings(self):
        processor = BatchProcessor(self.activeObjects, assign_switch_mappings)
        processor.start()

    def remove_all_switch_mappings(self):
        processor = BatchProcessor(self.activeObjects, remove_all_switch_assignments)
        processor.start()

    def apply_fader_edits_downstream(self):
        processor = BatchProcessor(self.activeObjects, apply_fader_edits_downstream)
        processor.start()

    # Event操作
    def create_play_event(self):
        processor = BatchProcessor(self.activeObjects, create_play_event)
        processor.start()

    # SoundBank操作
    def create_or_add_to_bank(self):
        processor = BatchProcessor(self.activeObjects, create_or_add_to_bank)
        processor.start()

    def calculate_bank_total_size(self):
        if WaapiTools.Client is None:
            return
        get_bank_size(self.activeObjects)

    def add_to_selected_bank(self):
        if WaapiTools.Client is None:
            return
        add_media_to_selected_bank(self.activeObjects)

    def clear_bank_inclusions(self):
        processor = BatchProcessor(self.activeObjects, clear_bank_inclusions)
        processor.start()

    def set_bank_inclusion_type(self, inclusion_type: list):
        processor = BatchProcessor(self.activeObjects, lambda obj: set_inclusion_type(obj, inclusion_type))
        processor.start()

    def bank_assignment_matrix(self):
        if WaapiTools.Client is None:
            return
        matrix_window = BankAssignmentMatrix()
        matrix_window.show()
        matrix_window.exec_()


sys.excepthook = traceback.print_exception


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

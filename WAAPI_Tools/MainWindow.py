import sys
import traceback
from waapi import WaapiClient, CannotConnectToWaapiException
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from QtDesign.MainWindow_ui import Ui_MainWindow
from ObjectTools.CommonTools import *
from ObjectTools.AudioSourceTools import *
from ObjectTools.LogicContainerTools import *
from ObjectTools.EventTools import *
from ObjectTools.SoundBankTools import *
from ObjectTools.BatchReplaceTool import *
from ObjectTools.TempTools import temp_tool
from ObjectTools.UnityResourceManager import UnityResourceManager
from Threading.BatchProcessor import BatchProcessor
from Libraries import ScriptingTools, WaapiTools, FileTools, LogTool, WwiseSilenceTool

if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        LogTool.init_log()
        self.setupUi(self)
        self.setup_triggers()
        self.cacheObjects = []  # 通过Get Seletion、Find Children等操作获得的obj列表
        self.activeObjects = []  # cacheObjects经过filter过滤后的obj列表
        self.batchProcessor = None
        self.statusbar.showMessage('Wwise无法连接...')
        self.tblActiveObjects.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # 初始化默认尝试连接wwise
        self.connect_to_wwise()

    def setup_triggers(self):
        self.tblActiveObjects.itemDoubleClicked.connect(self.show_object_in_wwise)

        self.btnWaapiConnect.clicked.connect(self.connect_to_wwise)
        self.btnGetSelectedObjects.clicked.connect(self.get_selected_objects)
        self.btnUpdateObjects.clicked.connect(self.update_list_objects)
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

        self.actCreateWorkUnit.triggered.connect(lambda: self.create_parent('WorkUnit'))
        self.actCreateActorMixer.triggered.connect(lambda: self.create_parent('ActorMixer'))
        self.actCreateVirtualFolder.triggered.connect(lambda: self.create_parent('Folder'))
        self.actCreateBlendContainer.triggered.connect(lambda: self.create_parent('BlendContainer'))
        self.actCreateRandomSequenceContainer.triggered.connect(lambda: self.create_parent('RandomSequenceContainer'))
        self.actCreateSwitchContainer.triggered.connect(lambda: self.create_parent('SwitchContainer'))

        self.btnFindParent.clicked.connect(self.find_parent)
        self.btnFindChildren.clicked.connect(self.find_children)

        self.reset_filter()

        self.actUndo.triggered.connect(WaapiTools.undo)
        self.actRedo.triggered.connect(WaapiTools.redo)
        self.actSetIncluded.triggered.connect(lambda: self.set_inclusion(True))
        self.actSetExcluded.triggered.connect(lambda: self.set_inclusion(False))
        self.actFilterIncluded.triggered.connect(lambda: self.filter_by_inclusion(True))
        self.actFilterExcluded.triggered.connect(lambda: self.filter_by_inclusion(False))
        self.actDeleteObjects.triggered.connect(self.delete_all_objects)

        self.actMoveListToSelection.triggered.connect(self.move_active_objects_to_selection)
        self.actCopySelectionToList.triggered.connect(self.copy_selection_to_active_objects)
        self.actChangeToLowerCase.triggered.connect(lambda: self.apply_naming_convention(0))
        self.actChangeToTitleCase.triggered.connect(lambda: self.apply_naming_convention(1))
        self.actChangeToUpperCase.triggered.connect(lambda: self.apply_naming_convention(2))
        # self.actWwiseSilenceAdd.triggered.connect(self.create_wwise_silence)
        # self.actWwiseSilenceRemove.triggered.connect(self.remove_wwise_silence)

        self.actImportFromFile.triggered.connect(self.import_from_file)
        self.actExportToFile.triggered.connect(self.export_to_file)

        self.actBatchReplaceTool.triggered.connect(self.batch_replace_tool)

        self.actApplyEditsToOriginal.triggered.connect(self.apply_source_edits)
        self.actResetSourceEdits.triggered.connect(self.reset_source_editor)
        self.actTrimTailSilence.triggered.connect(self.trim_tail_silence)
        self.actRenameOriginalToWwise.triggered.connect(self.rename_original_to_wwise)
        self.actDeleteUnusedAKDFiles.triggered.connect(delete_unused_akd_files)
        self.actLocalizeLanguages.triggered.connect(self.localize_languages)

        self.actBreakContainer.triggered.connect(self.break_container)
        self.actReplaceParent.triggered.connect(self.replace_parent)
        self.actAssignSwitchMappings.triggered.connect(self.assign_switch_mappings)
        self.actRemoveAllSwitchAssignments.triggered.connect(self.remove_all_switch_mappings)
        self.actSetGenericPath.triggered.connect(self.set_as_generic_path_obj)
        self.actSplitByNetRole.triggered.connect(self.split_by_net_role)
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

        self.actTempTool.triggered.connect(lambda: temp_tool(self.activeObjects))
        self.actUnityResourceManager.triggered.connect(self.manage_unity_resources)

    # 重置筛选条件
    def reset_filter(self):
        try:
            self.rbnFilterByName.toggled.disconnect(self.filter_and_show_list)
            self.rbnFilterByPath.toggled.disconnect(self.filter_and_show_list)
            self.rbnFilterByInclude.toggled.disconnect(self.filter_and_show_list)
            self.rbnFilterByExclude.toggled.disconnect(self.filter_and_show_list)
            self.cbxUseRegularExpression.toggled.disconnect(self.filter_and_show_list)
            self.cbxMatchWholeWord.toggled.disconnect(self.filter_and_show_list)
            self.cbxCaseSensitive.toggled.disconnect(self.filter_and_show_list)
            self.cbbDescendantType.currentIndexChanged.disconnect(self.filter_and_show_list)
            self.iptSelectionFilter.textChanged.disconnect(self.filter_and_show_list)
        except:
            print("filter toggle first disconnect fail")

        self.rbnFilterByName.setChecked(True)
        self.rbnFilterByInclude.setChecked(True)
        self.cbxUseRegularExpression.setChecked(False)
        self.cbxMatchWholeWord.setChecked(False)
        self.cbxCaseSensitive.setChecked(False)
        self.cbbDescendantType.setCurrentIndex(0)
        self.iptSelectionFilter.setText("")

        self.rbnFilterByName.toggled.connect(self.filter_and_show_list)
        self.rbnFilterByPath.toggled.connect(self.filter_and_show_list)
        self.rbnFilterByInclude.toggled.connect(self.filter_and_show_list)
        self.rbnFilterByExclude.toggled.connect(self.filter_and_show_list)
        self.cbxUseRegularExpression.toggled.connect(self.filter_and_show_list)
        self.cbxMatchWholeWord.toggled.connect(self.filter_and_show_list)
        self.cbxCaseSensitive.toggled.connect(self.filter_and_show_list)
        self.cbbDescendantType.currentIndexChanged.connect(self.filter_and_show_list)
        self.iptSelectionFilter.textChanged.connect(self.filter_and_show_list)

    # 通过指定的端口连接到Wwise
    def connect_to_wwise(self):
        url = 'ws://127.0.0.1:' + str(self.spbWaapiPort.value()) + '/waapi'
        try:
            WaapiTools.Client = WaapiClient(url=url)
            WaapiTools.Client.subscribe('ak.wwise.core.project.postClosed', self.on_wwise_closed)
            self.statusbar.showMessage('Wwise已连接到' + WaapiTools.get_project_directory())
            self.btnWaapiConnect.setEnabled(False)
        except CannotConnectToWaapiException:
            self.statusbar.showMessage('无法连接到Wwise工程...')

    # Wwise关闭时的回调
    def on_wwise_closed(self):
        self.statusbar.showMessage('Wwise未连接...')
        self.btnWaapiConnect.setEnabled(True)
        WaapiTools.Client = None

    # 获取Wwise中选中的对象
    def get_selected_objects(self):
        if WaapiTools.Client is None:
            return
        self.cacheObjects = WaapiTools.get_selected_objects()
        self.reset_filter()
        self.filter_and_show_list()

    # 根据filter刷新当前列表内容
    def update_list_objects(self):
        self.cacheObjects = self.activeObjects
        self.reset_filter()
        self.filter_and_show_list()

    # 删去表格中选中的对象
    def remove_table_selection(self):
        for item in self.tblActiveObjects.selectedItems():
            self.activeObjects.pop(item.row())
            self.tblActiveObjects.removeRow(item.row())

    # 清空操作对象列表
    def clear_object_list(self):
        self.cacheObjects = []
        self.activeObjects = []
        self.tblActiveObjects.setRowCount(0)

    # 实时筛选列表内容
    def filter_obj_list(self):
        self.activeObjects = ScriptingTools.filter_objects(self.cacheObjects,
                                                           self.iptSelectionFilter.text(),
                                                           self.cbxCaseSensitive.isChecked(),
                                                           self.cbxMatchWholeWord.isChecked(),
                                                           self.cbxUseRegularExpression.isChecked(),
                                                           self.cbbDescendantType.currentText(),
                                                           self.rbnFilterByName.isChecked(),
                                                           self.rbnFilterByInclude.isChecked()
                                                           )

    def show_obj_list(self):
        self.tblActiveObjects.setRowCount(0)
        for obj in self.activeObjects:
            row_count = self.tblActiveObjects.rowCount()
            self.tblActiveObjects.insertRow(row_count)
            self.tblActiveObjects.setItem(row_count, 0, QTableWidgetItem(obj['name']))
            self.tblActiveObjects.setItem(row_count, 1, QTableWidgetItem(obj['type']))
            self.tblActiveObjects.setItem(row_count, 2, QTableWidgetItem(obj['path']))

    # 在表中显示筛选过的对象
    def filter_and_show_list(self):
        self.filter_obj_list()
        self.show_obj_list()

    # 查找父级对象
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
        self.cacheObjects = all_parents
        self.reset_filter()
        self.filter_and_show_list()

    # 查找子级对象
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
        self.cacheObjects = all_children
        self.reset_filter()
        self.filter_and_show_list()

    def on_ui_executed(*args, **kwargs):
        # 获取对象类型
        obj_type = kwargs.get("object", {}).get("type")
        # 获取之前的名字
        old_name = kwargs.get("oldName")
        # 获取新名字
        new_name = kwargs.get("newName")

        # 使用 format 格式化函数进行输出信息（其中的{}代表 format() 函数中的对应变量），告知用户XXX类型的对象从 A 改名到了 B
        print("Object '{}' (of type '{}') was renamed to '{}'\n".format(old_name, obj_type, new_name))

    def show_object_in_wwise(self, item: QTableWidgetItem):
        if WaapiTools.Client is None:
            return
        if item.column() != 2:
            item = self.tblActiveObjects.item(item.row(), 2)
            WaapiTools.open_item_in_wwise_by_path(item.text())

    # 通用操作
    def convert_to_type(self, target_type: str):
        self.batchProcessor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.convert_to_type(obj, target_type), 'Convert Type')
        self.batchProcessor.start()

    def create_parent(self, target_type: str):
        self.batchProcessor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.create_parent(obj, target_type), 'Create Parent')
        self.batchProcessor.start()

    def set_inclusion(self, included: bool):
        self.batchProcessor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.set_object_property(obj, 'Inclusion', True if included else False), 'Set Inclusion')
        self.batchProcessor.start()

    def filter_by_inclusion(self, included: bool):
        self.cacheObjects = ScriptingTools.filter_objects_by_inclusion(self.activeObjects, True if included else False)
        self.reset_filter()
        self.filter_and_show_list()

    def delete_all_objects(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, WaapiTools.delete_object, 'Delete Objects')
        self.batchProcessor.start()
        self.clear_object_list()

    def apply_naming_convention(self, naming_rule: int):
        if naming_rule == 0:
            self.batchProcessor = BatchProcessor(self.activeObjects, rename_to_lower_case, 'Rename Lower Case')
        elif naming_rule == 1:
            self.batchProcessor = BatchProcessor(self.activeObjects, rename_to_title_case, 'Rename Title Case')
        else:
            self.batchProcessor = BatchProcessor(self.activeObjects, rename_to_upper_case, 'Rename Upper Case')
        self.batchProcessor.start()

    def create_wwise_silence(self):
        WwiseSilenceTool.WwiseSilenceInstance.Add()

    def remove_wwise_silence(self):
        WwiseSilenceTool.WwiseSilenceInstance.Remove()

    # 导出为文件
    def export_to_file(self):
        if WaapiTools.Client is None:
            return
        saveDict = {"selectObject": WaapiTools.get_selected_objects(),
                    "activeObjects": self.activeObjects,
                    "cacheObjects": self.cacheObjects,
                    "radioBtn_group_key_name": self.radioBtn_group_key_name.isChecked(),
                    "radioBtn_group_ope_include": self.radioBtn_group_ope_include.isChecked(),
                    "cbxUseRegularExpression": self.cbxUseRegularExpression.isChecked(),
                    "cbxMatchWholeWord": self.cbxMatchWholeWord.isChecked(),
                    "cbxCaseSensitive": self.cbxCaseSensitive.isChecked(),
                    "cbbDescendantType": self.cbbDescendantType.currentIndex(),
                    "iptSelectionFilter": self.iptSelectionFilter.text()
                    }
        FileTools.export_to_file(saveDict)

    # 从文件导入，并刷新UI
    def import_from_file(self):
        loadDict = FileTools.import_from_file()
        if loadDict:
            try:
                self.radioBtn_group_key_name.setChecked(loadDict["radioBtn_group_key_name"])
                self.radioBtn_group_ope_include.setChecked(loadDict["radioBtn_group_ope_include"])
                self.cbxUseRegularExpression.setChecked(loadDict["cbxUseRegularExpression"])
                self.cbxMatchWholeWord.setChecked(loadDict["cbxMatchWholeWord"])
                self.cbxCaseSensitive.setChecked(loadDict["cbxCaseSensitive"])
                self.cbbDescendantType.setCurrentIndex(loadDict["cbbDescendantType"])
                self.iptSelectionFilter.setText(loadDict["iptSelectionFilter"])
                self.activeObjects = loadDict["activeObjects"]
                self.cacheObjects = loadDict["cacheObjects"]
                self.show_obj_list()
            except:
                print("import from file failed")

    def move_active_objects_to_selection(self):
        if WaapiTools.Client is None:
            return
        selection = WaapiTools.get_selected_objects()
        if len(selection) > 0:
            self.batchProcessor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.move_object(obj, selection[0]), 'Move to Selection')
            self.batchProcessor.start()

    def copy_selection_to_active_objects(self):
        if WaapiTools.Client is None:
            return
        selection = WaapiTools.get_selected_objects()
        if len(selection) > 0:
            self.batchProcessor = BatchProcessor(self.activeObjects, lambda obj: WaapiTools.copy_object(selection[0], obj), 'Copy Selection')
            self.batchProcessor.start()

    def break_container(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, break_container, 'Break Container')
        self.batchProcessor.start()

    def replace_parent(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, replace_parent, 'Replace Parent')
        self.batchProcessor.start()

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
        self.batchProcessor = BatchProcessor(self.activeObjects, apply_source_edit, 'Apply Edit to Source')
        self.batchProcessor.start()

    def reset_source_editor(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, reset_source_editor, 'Reset Source Editor')
        self.batchProcessor.start()

    def trim_tail_silence(self):
        trim_window = AudioTailTrimmer(self.activeObjects)
        trim_window.show()
        trim_window.exec_()

    def batch_replace_tool(self):
        if WaapiTools.Client is None:
            return
        replace_window = BatchReplaceTool(self)
        replace_window.show()
        replace_window.exec_()

    def rename_original_to_wwise(self):
        if WaapiTools.Client is None:
            return
        self.batchProcessor = BatchProcessor(self.activeObjects, rename_original_to_wwise, 'Rename Source File')
        self.batchProcessor.start()

    def localize_languages(self):
        if WaapiTools.Client is None:
            return
        self.batchProcessor = BatchProcessor(self.activeObjects, localize_languages, 'Localization')
        self.batchProcessor.start()

    # LogicContainer操作
    def assign_switch_mappings(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, auto_assign_switch_mappings, 'Auto Assign Mapping')
        self.batchProcessor.start()

    def remove_all_switch_mappings(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, remove_all_switch_assignments, 'Clear Mappings')
        self.batchProcessor.start()

    def set_as_generic_path_obj(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, set_as_generic_path_obj, 'Set Generic Mapping')
        self.batchProcessor.start()

    def apply_fader_edits_downstream(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, apply_fader_edits_downstream, 'Apply Fader Edits')
        self.batchProcessor.start()

    def split_by_net_role(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, split_by_net_role, 'Split by Net Role')
        self.batchProcessor.start()

    # Event操作
    def create_play_event(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, create_play_event, 'Create Play Event')
        self.batchProcessor.start()

    # SoundBank操作
    def create_or_add_to_bank(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, create_or_add_to_bank, 'Create/Add Bank')
        self.batchProcessor.start()

    def calculate_bank_total_size(self):
        if WaapiTools.Client is None:
            return
        get_bank_size(self.activeObjects)

    def add_to_selected_bank(self):
        if WaapiTools.Client is None:
            return
        banks = WaapiTools.get_selected_objects()
        if len(banks) == 0 or banks[0]['type'] != 'SoundBank':
            return
        add_objects_to_bank(banks[0], self.activeObjects, ['media'])

    def clear_bank_inclusions(self):
        self.batchProcessor = BatchProcessor(self.activeObjects, clear_bank_inclusions, 'Clear Bank Inclusions')
        self.batchProcessor.start()

    def set_bank_inclusion_type(self, inclusion_type: list):
        self.batchProcessor = BatchProcessor(self.activeObjects, lambda obj: set_inclusion_type(obj, inclusion_type), 'Set Bank Inclusion Type')
        self.batchProcessor.start()

    def bank_assignment_matrix(self):
        if WaapiTools.Client is None:
            return
        matrix_window = BankAssignmentMatrix(self)
        matrix_window.show()
        matrix_window.exec_()

    # 其他操作
    def manage_unity_resources(self):
        resource_manager = UnityResourceManager()
        resource_manager.show()
        resource_manager.exec_()

    def closeEvent(self, close_event):
        self.batchProcessor = None


sys.excepthook = traceback.print_exception

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

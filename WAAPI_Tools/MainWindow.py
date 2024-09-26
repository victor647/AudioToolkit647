import sys
import traceback
from SubWindows.AudioTailTrimWindow import AudioTailTrimWindow as AudioTailTrimWindow
from SubWindows.TableRenameWindow import TableRenamer as TableRenamer
from SubWindows.TemplateReplaceWindow import TemplateReplacer as TemplateReplacer
from SubWindows.BankAssignmentMatrix import BankAssignmentMatrix as BankAssignmentMatrix
from SubWindows.ProjectValidationWindow import ProjectValidation as ProjectValidation
from SubWindows.UnityAssetManageWindow import UnityAssetManager as UnityAssetManager
from waapi import CannotConnectToWaapiException
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from QtDesign.MainWindow_ui import Ui_MainWindow
from ObjectTools import AudioSourceTools, CommonTools, EventTools, ImportTools, LogicContainerTools
from ObjectTools import LocalizationTools, MixingTools, SoundBankTools, TempTools, ProjectTools
from Threading.BatchProcessor import BatchProcessor
from Libraries import ScriptingHelper, WAAPI, FileTools, ProjectConventions


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.cacheObjects = []  # 通过Get Seletion、Find Children等操作获得的obj列表
        self.activeObjects = []  # cacheObjects经过filter过滤后的obj列表
        self.statusbar.showMessage('Wwise无法连接...')
        # 初始化默认尝试连接wwise
        self.connect_to_wwise()

    def setup_triggers(self):
        self.reset_filter()
        self.tblActiveObjects.itemDoubleClicked.connect(self.show_object_in_wwise)
        self.tblActiveObjects.setColumnWidth(2, 600)
        # 所有按键
        self.btnWaapiConnect.clicked.connect(self.connect_to_wwise)
        self.btnGetSelectedObjects.clicked.connect(self.get_selected_objects)
        self.btnUpdateObjects.clicked.connect(self.update_table_listed_objects)
        self.btnRemoveSelection.clicked.connect(self.remove_table_selection)
        self.btnKeepOnlySelection.clicked.connect(self.keep_table_selection_only)
        self.btnClearObjects.clicked.connect(self.clear_object_list)
        self.btnMultiEditor.clicked.connect(self.open_in_multi_editor)
        self.btnBatchRename.clicked.connect(self.open_in_batch_rename)
        self.btnFindParent.clicked.connect(self.find_parent)
        self.btnFindChildren.clicked.connect(self.find_children)
        # 文件菜单
        self.actImportCriterias.triggered.connect(self.import_criterias)
        self.actExportCriterias.triggered.connect(self.export_criterias)
        self.actImportObjects.triggered.connect(self.import_objects)
        self.actExportObjects.triggered.connect(self.export_objects)
        # 编辑菜单
        self.actUndo.triggered.connect(WAAPI.undo)
        self.actRedo.triggered.connect(WAAPI.redo)

        self.setup_batch_processor(self.actSetIncluded, CommonTools.set_included)
        self.setup_batch_processor(self.actSetExcluded, CommonTools.set_excluded)
        self.setup_batch_processor(self.actDeleteObjects, WAAPI.delete_object)
        self.actFilterIncluded.triggered.connect(lambda: self.filter_by_inclusion(True))
        self.actFilterExcluded.triggered.connect(lambda: self.filter_by_inclusion(False))
        # 通用菜单
        self.setup_batch_processor(self.actConvertToWorkUnit, lambda obj: CommonTools.convert_to_type(obj, 'WorkUnit'))
        self.setup_batch_processor(self.actConvertToActorMixer, lambda obj: CommonTools.convert_to_type(obj, 'ActorMixer'))
        self.setup_batch_processor(self.actConvertToVirtualFolder, lambda obj: CommonTools.convert_to_type(obj, 'Folder'))
        self.setup_batch_processor(self.actConvertToBlendContainer, lambda obj: CommonTools.convert_to_type(obj, 'BlendContainer'))
        self.setup_batch_processor(self.actConvertToRandomSequenceContainer, lambda obj: CommonTools.convert_to_type(obj, 'RandomSequenceContainer'))
        self.setup_batch_processor(self.actConvertToSwitchContainer, lambda obj: CommonTools.convert_to_type(obj, 'SwitchContainer'))

        self.setup_batch_processor(self.actCreateWorkUnit, lambda obj: CommonTools.create_parent(obj, 'WorkUnit'))
        self.setup_batch_processor(self.actCreateActorMixer, lambda obj: CommonTools.create_parent(obj, 'ActorMixer'))
        self.setup_batch_processor(self.actCreateVirtualFolder, lambda obj: CommonTools.create_parent(obj, 'Folder'))
        self.setup_batch_processor(self.actCreateBlendContainer, lambda obj: CommonTools.create_parent(obj, 'BlendContainer'))
        self.setup_batch_processor(self.actCreateRandomSequenceContainer, lambda obj: CommonTools.create_parent(obj, 'RandomSequenceContainer'))
        self.setup_batch_processor(self.actCreateSwitchContainer, lambda obj: CommonTools.create_parent(obj, 'SwitchContainer'))

        self.setup_batch_processor(self.actMoveToSelection, CommonTools.move_to_selection)
        self.setup_batch_processor(self.actCopyFromSelection, CommonTools.copy_from_selection)

        self.setup_batch_processor(self.actChangeToLowerCase, CommonTools.rename_to_lower_case)
        self.setup_batch_processor(self.actChangeToTitleCase, CommonTools.rename_to_title_case)
        self.setup_batch_processor(self.actChangeToUpperCase, CommonTools.rename_to_upper_case)
        self.setup_batch_processor(self.actOptimizeNameLength, CommonTools.optimize_name_length)
        self.setup_batch_processor(self.actRemoveNameSuffix, CommonTools.remove_name_suffix)
        self.setup_batch_processor(self.actUpdateNoteAndColor, CommonTools.update_notes_and_color)
        self.setup_batch_processor(self.actSplitUnderScore, CommonTools.split_underscore_to_folder)

        self.actReplaceByTemplate.triggered.connect(self.open_template_replace_window)
        self.actRenameByDataTable.triggered.connect(self.open_table_rename_window)
        # 源文件菜单
        self.actTrimTailSilence.triggered.connect(self.open_audio_tail_trimmer_window)
        self.setup_batch_processor(self.actApplyEditsToOriginal, AudioSourceTools.apply_source_edits)
        self.setup_batch_processor(self.actResetSourceEdits, AudioSourceTools.reset_source_editor)
        self.setup_batch_processor(self.actRenameOriginalToWwise, AudioSourceTools.rename_original_to_wwise)
        self.setup_batch_processor(self.actTidyOriginalFolders, AudioSourceTools.tidy_original_folders)
        self.actDeleteUnusedAKDFiles.triggered.connect(AudioSourceTools.delete_unused_akd_files)
        # 本地化菜单
        self.setup_batch_processor(self.actLocalizeLanguages, LocalizationTools.localize_languages)
        self.setup_batch_processor(self.actFillSilenceForRefLanguage, LocalizationTools.import_silence_for_ref_language)
        self.setup_batch_processor(self.actFillSilenceForAllLanguages, LocalizationTools.import_silence_for_all_languages)
        # 混音菜单
        self.setup_batch_processor(self.actDownMixFader, MixingTools.down_mix_fader)
        # Container菜单
        self.setup_batch_processor(self.actBreakContainer, LogicContainerTools.break_container)
        self.setup_batch_processor(self.actReplaceParent, LogicContainerTools.replace_parent)
        self.setup_batch_processor(self.actAssignSwitchMappings, LogicContainerTools.assign_switch_mappings)
        self.setup_batch_processor(self.actRemoveSwitchMappings, LogicContainerTools.remove_switch_mappings)
        self.setup_batch_processor(self.actAssignToGenericPath, LogicContainerTools.assign_to_generic_path)
        self.setup_batch_processor(self.actSplitTo1P3P, lambda obj: LogicContainerTools.split_by_net_role(obj, False))
        self.setup_batch_processor(self.actSplitTo1P2P3P, lambda obj: LogicContainerTools.split_by_net_role(obj, True))
        self.setup_batch_processor(self.actGroupAsRandom, LogicContainerTools.group_as_random)
        # Event菜单
        self.setup_batch_processor(self.actCreatePlayEvent, EventTools.create_play_event)
        self.setup_batch_processor(self.actRenameEventByTarget, EventTools.rename_event_by_target)
        # SoundBank菜单
        self.setup_batch_processor(self.actCreateSoundBank, SoundBankTools.create_bank_for_object)
        self.setup_batch_processor(self.actClearInclusions, WAAPI.clear_bank_inclusions)
        self.setup_batch_processor(self.actIncludeMediaOnly, lambda obj: SoundBankTools.set_inclusion_type(obj, ['media']))
        self.setup_batch_processor(self.actIncludeEventsAndStructures, lambda obj: SoundBankTools.set_inclusion_type(obj, ['events', 'structures']))
        self.setup_batch_processor(self.actIncludeAll, lambda obj: SoundBankTools.set_inclusion_type(obj, ['events', 'structures', 'media']))
        self.actCalculateBankSize.triggered.connect(self.calculate_bank_total_size)
        self.actAddToSelectedBank.triggered.connect(self.add_to_selected_bank)

        self.actBankAssignmentMatrix.triggered.connect(self.open_bank_assignment_matrix_window)
        self.actGenerateEventBankMap.triggered.connect(SoundBankTools.generate_event_bank_map)
        # 其他菜单
        self.actProjectValidation.triggered.connect(self.open_project_validation_window)
        self.actTempTool.triggered.connect(lambda: TempTools.temp_tool(self.activeObjects))
        self.actUnityAssetManager.triggered.connect(self.open_unity_asset_manager_window)
        self.actImportFMODEvent.triggered.connect(ImportTools.import_fmod_events)
        self.actImportFMODPreset.triggered.connect(ImportTools.import_fmod_presets)

    # 连接批处理器到操作
    def setup_batch_processor(self, action, obj_func):
        action.triggered.connect(lambda: BatchProcessor(self.activeObjects, obj_func, action.text()).start())

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
        except Exception as e:
            print(e)

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
        try:
            client = WAAPI.get_client()
            if client:
                client.subscribe('ak.wwise.core.project.postClosed', self.on_wwise_closed)
                project_path = ProjectTools.get_project_path()
                if project_path:
                    self.statusbar.showMessage(f'已连接到Wwise工程: {project_path}')
                    self.btnWaapiConnect.setEnabled(False)
                    ProjectConventions.init()
            else:
                self.statusbar.showMessage('无法连接到Wwise工程...')
        except CannotConnectToWaapiException:
            self.statusbar.showMessage('无法连接到Wwise工程...')

    # Wwise关闭时的回调
    def on_wwise_closed(self):
        self.statusbar.showMessage('Wwise未连接...')
        self.btnWaapiConnect.setEnabled(True)
        WAAPI.Client = None

    # 获取Wwise中选中的对象
    def get_selected_objects(self):
        self.cacheObjects = WAAPI.get_selected_objects()
        self.reset_filter()
        self.filter_and_show_list()

    # 根据filter刷新当前列表内容
    def update_table_listed_objects(self):
        self.cacheObjects = self.activeObjects
        self.reset_filter()
        self.filter_and_show_list()

    # 删去表格中选中的对象
    def remove_table_selection(self):
        for item in self.tblActiveObjects.selectedItems():
            self.activeObjects.pop(item.row())
            self.tblActiveObjects.removeRow(item.row())

    # 仅保留表格中选中的对象
    def keep_table_selection_only(self):
        keep_objects = []
        for item in self.tblActiveObjects.selectedItems():
            keep_objects.append(self.activeObjects[item.row()])
        self.activeObjects = keep_objects
        self.update_table_listed_objects()

    # 清空操作对象列表
    def clear_object_list(self):
        self.cacheObjects = []
        self.activeObjects = []
        self.tblActiveObjects.setRowCount(0)

    # 实时筛选列表内容
    def filter_obj_list(self):
        self.activeObjects = ScriptingHelper.filter_objects(self.cacheObjects,
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
        self.tblActiveObjects.resizeColumnsToContents()

    # 在表中显示筛选过的对象
    def filter_and_show_list(self):
        self.filter_obj_list()
        self.show_obj_list()

    # 查找父级对象
    def find_parent(self):
        ancestor_mode = self.cbxRecursiveFind.isChecked()
        found_objects = self.activeObjects if self.cbxKeepSelf.isChecked() else []
        for obj in self.activeObjects:
            if ancestor_mode:
                for ancestor in WAAPI.get_ancestor_objects(obj):
                    found_objects.append(ancestor)
            else:
                found_objects.append(WAAPI.get_parent_object(obj))
        self.cacheObjects = found_objects
        self.reset_filter()
        self.filter_and_show_list()

    # 查找子级对象
    def find_children(self):
        all_children = self.activeObjects.copy() if self.cbxKeepSelf.isChecked() else []
        for obj in self.activeObjects:
            for child in WAAPI.get_child_objects(obj, self.cbxRecursiveFind.isChecked()):
                all_children.append(child)
        self.cacheObjects = all_children
        self.reset_filter()
        self.filter_and_show_list()

    @staticmethod
    def on_ui_executed(**kwargs):
        # 获取对象类型
        obj_type = kwargs.get("object", {}).get("type")
        # 获取之前的名字
        old_name = kwargs.get("oldName")
        # 获取新名字
        new_name = kwargs.get("newName")

        # 使用 format 格式化函数进行输出信息（其中的{}代表 format() 函数中的对应变量），告知用户XXX类型的对象从 A 改名到了 B
        print("Object '{}' (of type '{}') was renamed to '{}'\n".format(old_name, obj_type, new_name))

    def show_object_in_wwise(self, item: QTableWidgetItem):
        if item.column() != 2:
            item = self.tblActiveObjects.item(item.row(), 2)
        obj = WAAPI.get_object_from_path(item.text())
        if obj:
            WAAPI.select_objects_in_wwise([obj])

    # 导出筛选条件
    def export_criterias(self):
        options = {
            self.rbnFilterByName.objectName(): self.rbnFilterByName.isChecked(),
            self.rbnFilterByPath.objectName(): self.rbnFilterByPath.isChecked(),
            self.rbnFilterByInclude.objectName(): self.rbnFilterByInclude.isChecked(),
            self.rbnFilterByExclude.objectName(): self.rbnFilterByExclude.isChecked(),
            self.cbxKeepSelf.objectName(): self.cbxKeepSelf.isChecked(),
            self.cbxRecursiveFind.objectName(): self.cbxRecursiveFind.isChecked(),
            self.cbxCaseSensitive.objectName(): self.cbxCaseSensitive.isChecked(),
            self.cbxMatchWholeWord.objectName(): self.cbxMatchWholeWord.isChecked(),
            self.cbxUseRegularExpression.objectName(): self.cbxUseRegularExpression.isChecked(),
            self.cbbDescendantType.objectName(): self.cbbDescendantType.currentIndex(),
            self.iptSelectionFilter.objectName(): self.iptSelectionFilter.text()
        }
        FileTools.export_to_json(options, 'WAAPI_Tools_Criteria')

    # 导入筛选条件
    def import_criterias(self):
        options = FileTools.import_from_json()
        if options:
            self.rbnFilterByName.setChecked(options[self.rbnFilterByName.objectName()])
            self.rbnFilterByPath.setChecked(options[self.rbnFilterByPath.objectName()])
            self.rbnFilterByInclude.setChecked(options[self.rbnFilterByInclude.objectName()])
            self.rbnFilterByExclude.setChecked(options[self.rbnFilterByExclude.objectName()])
            self.cbxKeepSelf.setChecked(options[self.cbxKeepSelf.objectName()])
            self.cbxRecursiveFind.setChecked(options[self.cbxRecursiveFind.objectName()])
            self.cbxCaseSensitive.setChecked(options[self.cbxCaseSensitive.objectName()])
            self.cbxMatchWholeWord.setChecked(options[self.cbxMatchWholeWord.objectName()])
            self.cbxUseRegularExpression.setChecked(options[self.cbxUseRegularExpression.objectName()])
            self.cbbDescendantType.setCurrentIndex(options[self.cbbDescendantType.objectName()])
            self.iptSelectionFilter.setText(options[self.iptSelectionFilter.objectName()])
        self.filter_and_show_list()

    # 导出对象列表
    def export_objects(self):
        FileTools.export_to_json(self.activeObjects, 'WAAPI_Tools_Objects')

    # 导入对象列表
    def import_objects(self):
        self.activeObjects = FileTools.import_from_json()
        self.show_obj_list()

    # 通用操作
    def filter_by_inclusion(self, included: bool):
        self.cacheObjects = ScriptingHelper.filter_objects_by_inclusion(self.activeObjects, included)
        self.reset_filter()
        self.filter_and_show_list()

    # 打开Wwise的多项编辑器
    def open_in_multi_editor(self):
        WAAPI.execute_ui_command(self.activeObjects, 'ShowMultiEditor')
        WAAPI.bring_wwise_to_foreground()

    # 打开Wwise的批量重命名工具
    def open_in_batch_rename(self):
        WAAPI.execute_ui_command(self.activeObjects, 'ShowBatchRename')
        WAAPI.bring_wwise_to_foreground()

    # 打开模板批量替换窗口
    def open_template_replace_window(self):
        replace_window = TemplateReplacer(self)
        replace_window.show()
        replace_window.exec()

    # 打开读表重命名窗口
    def open_table_rename_window(self):
        rename_window = TableRenamer(self)
        rename_window.show()
        rename_window.exec()

    # 打开音频末尾静音裁剪窗口
    def open_audio_tail_trimmer_window(self):
        trim_window = AudioTailTrimWindow(self.activeObjects)
        trim_window.show()
        trim_window.exec()

    # 计算列表中Bank的总大小
    def calculate_bank_total_size(self):
        total_wav_size, total_wem_size, total_files_count, unused_files = SoundBankTools.get_total_bank_size(self.activeObjects)
        text = f'原始Wav文件: {total_wav_size}MB\n压缩后的Wem: {total_files_count}个文件, 共{total_wem_size}MB'
        if len(unused_files) > 0:
            text += f'\n未使用或未生成到Bank中的文件:\n'
            for file in unused_files:
                text += f'{file}\n'
        ScriptingHelper.show_message_box('统计完毕', text)

    # 添加列表对象到选中的Bank中
    def add_to_selected_bank(self):
        banks = WAAPI.get_selected_objects()
        if len(banks) == 0 or banks[0]['type'] != 'SoundBank':
            return
        SoundBankTools.add_objects_to_bank(banks[0], self.activeObjects, ['media'])

    # 打开Bank的列表分配窗口
    def open_bank_assignment_matrix_window(self):
        matrix_window = BankAssignmentMatrix(self)
        matrix_window.show()
        matrix_window.exec()

    # 打开Unity资产管理器窗口
    @staticmethod
    def open_unity_asset_manager_window():
        asset_manager = UnityAssetManager()
        asset_manager.show()
        asset_manager.exec()

    # 打开工程检查窗口
    def open_project_validation_window(self):
        validate_window = ProjectValidation(self)
        validate_window.show()
        validate_window.exec()


sys.excepthook = traceback.print_exception

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

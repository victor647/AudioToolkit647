import re

from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from PyQt6.QtGui import QColor
from Libraries import WaapiTools
from ObjectTools import CommonTools, SoundBankTools, AudioSourceTools, EventTools, LocalizationTools, LogicContainerTools, MixingTools
from QtDesign.ProjectValidation_ui import Ui_ProjectValidation
from Threading.BatchProcessor import BatchProcessor


# Wwise工程检查工具
class ProjectValidationWindow(QDialog, Ui_ProjectValidation):

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__batchProcessor = None
        self.__mainWindow = main_window
        self.builtInRTPCs = []
        self.problematicObjects = []

    def setup_triggers(self):
        self.btnSelectAll.clicked.connect(self.select_all)
        self.btnDeselectAll.clicked.connect(self.deselect_all)
        self.btnValidateEntireProject.clicked.connect(self.validate_entire_project)
        self.btnValidateListEntries.clicked.connect(lambda: self.validate_objects(self.__mainWindow.activeObjects))
        self.btnValidateProjectSelection.clicked.connect(lambda: self.validate_objects(WaapiTools.get_selected_objects()))
        self.btnSendResultToMainWindow.clicked.connect(self.send_results_back)
        self.btnAutoFixSelection.clicked.connect(self.auto_fix_selection)

        self.tblValidationResults.itemDoubleClicked.connect(self.show_object_in_wwise)
        self.tblValidationResults.setColumnWidth(2, 600)

    # 每次运行前重置数据
    def reset_data(self):
        self.builtInRTPCs = []
        self.problematicObjects = []
        self.tblValidationResults.setRowCount(0)

    def select_all(self):
        self.cbxCamelCaseNaming.setChecked(True)
        self.cbxRepeatingNodeName.setChecked(True)
        self.cbxColorConvention.setChecked(True)
        self.cbxInconsistentSourcePath.setChecked(True)
        self.cbxEventNamingMismatch.setChecked(True)
        self.cbxUnnecessaryEvent.setChecked(True)
        self.cbxMissingEventNotes.setChecked(True)
        self.cbxSoundNotInEvent.setChecked(True)
        self.cbxEventNotInBank.setChecked(True)
        self.cbxAssignedToMasterBus.setChecked(True)
        self.cbxNestedWorkUnit.setChecked(True)
        self.cbxRedundantActorMixer.setChecked(True)
        self.cbxSingleChildContainer.setChecked(True)
        self.cbxEmptyObject.setChecked(True)
        self.cbxDuplicatedRTPC.setChecked(True)
        self.cbxTrimOutOfRange.setChecked(True)
        self.cbxSoundNotImported.setChecked(True)
        self.cbxSilentVoicePlaceholder.setChecked(True)
        self.cbxAbnormalBankSize.setChecked(True)

    def deselect_all(self):
        self.cbxCamelCaseNaming.setChecked(False)
        self.cbxRepeatingNodeName.setChecked(False)
        self.cbxColorConvention.setChecked(False)
        self.cbxInconsistentSourcePath.setChecked(False)
        self.cbxEventNamingMismatch.setChecked(False)
        self.cbxUnnecessaryEvent.setChecked(False)
        self.cbxMissingEventNotes.setChecked(False)
        self.cbxSoundNotInEvent.setChecked(False)
        self.cbxEventNotInBank.setChecked(False)
        self.cbxAssignedToMasterBus.setChecked(False)
        self.cbxNestedWorkUnit.setChecked(False)
        self.cbxRedundantActorMixer.setChecked(False)
        self.cbxSingleChildContainer.setChecked(False)
        self.cbxEmptyObject.setChecked(False)
        self.cbxDuplicatedRTPC.setChecked(False)
        self.cbxTrimOutOfRange.setChecked(False)
        self.cbxSoundNotImported.setChecked(False)
        self.cbxSilentVoicePlaceholder.setChecked(False)
        self.cbxAbnormalBankSize.setChecked(False)

    # 在Wwise中选中对象
    def show_object_in_wwise(self, item: QTableWidgetItem):
        if WaapiTools.Client is None:
            return
        if item.column() != 2:
            item = self.tblValidationResults.item(item.row(), 2)
        WaapiTools.open_item_in_wwise_by_path(item.text())

    # 将检查结果发送到主窗口
    def send_results_back(self):
        self.__mainWindow.activeObjects = self.problematicObjects
        self.__mainWindow.show_obj_list()

    # 开始一键修复列表选中内容
    def auto_fix_selection(self):
        items = self.tblValidationResults.selectedItems()
        batch_processor = BatchProcessor(items, self.auto_fix, '自动修复工程')
        batch_processor.start()

    # 自动修复列表选中内容
    def auto_fix(self, item: QTableWidgetItem):
        index = item.row()
        problem_item = self.tblValidationResults.item(index, 0)
        # 已经修复的跳过
        if problem_item.foreground() != QColor(200, 0, 0):
            return
        problem_type = problem_item.text()
        fixed = False
        obj = self.problematicObjects[index]
        if problem_type == self.cbxCamelCaseNaming.text():
            fixed = self.fix_camel_case_naming(obj)
        elif problem_type == self.cbxRepeatingNodeName.text():
            fixed = self.fix_repeating_path(obj)
        elif problem_type == self.cbxColorConvention.text():
            fixed = CommonTools.update_notes_and_color(obj)
        elif problem_type == self.cbxDuplicatedRTPC.text():
            fixed = self.remove_duplicated_rtpc(obj)
        elif problem_type == self.cbxEventNamingMismatch.text():
            fixed = EventTools.rename_by_target(obj)
        elif problem_type == self.cbxMissingEventNotes.text():
            fixed = CommonTools.update_notes_and_color(obj)
        elif problem_type == self.cbxUnnecessaryEvent.text():
            fixed = self.remove_unnecessary_event(obj)
        elif problem_type == self.cbxSoundNotInEvent.text():
            fixed = CommonTools.set_object_inclusion(obj, False)
        elif problem_type == self.cbxNestedWorkUnit.text():
            fixed = self.fix_nested_work_unit(obj)
        elif problem_type == self.cbxRedundantActorMixer.text():
            fixed = WaapiTools.convert_to_type(obj, 'Folder')
        elif problem_type == self.cbxSingleChildContainer.text():
            fixed = LogicContainerTools.break_container(obj)
        elif problem_type == self.cbxEmptyObject.text():
            fixed = self.delete_empty_object(obj)
        elif problem_type == self.cbxInconsistentSourcePath.text():
            fixed = AudioSourceTools.rename_original_to_wwise(obj)
        elif problem_type == self.cbxTrimOutOfRange.text():
            fixed = WaapiTools.set_object_property(obj, 'TrimEnd', -1)
        problem_item.setForeground(QColor(0, 200, 0) if fixed else QColor(200, 200, 0))

    # 检查整个Wwise工程
    def validate_entire_project(self):
        self.reset_data()
        global_objects = WaapiTools.get_global_objects()
        self.__batchProcessor = BatchProcessor(global_objects, self.validate_object, '工程检查',
                                               self.on_validate_finished)
        self.__batchProcessor.start()

    # 检查对象列表及其所有子对象
    def validate_objects(self, objects):
        self.reset_data()
        all_objects = []
        for obj in objects:
            all_objects.append(obj)
            descendants = WaapiTools.get_child_objects(obj, True)
            for descendant in descendants:
                if descendant['name'] != '':
                    all_objects.append(descendant)
        self.__batchProcessor = BatchProcessor(all_objects, self.validate_object, '工程检查',
                                               self.on_validate_finished)
        self.__batchProcessor.start()

    # 将检查结果写入json文件
    def on_validate_finished(self):
        self.tblValidationResults.resizeColumnsToContents()
        message = QMessageBox()
        message.setWindowTitle('检查完毕')
        problem_count = len(self.problematicObjects)
        if problem_count == 0:
            message.setText('在工程中未发现任何问题！')
        else:
            message.setText(f'共发现{problem_count}处不符合工程规范！')
        message.exec()

    # 检查单个对象
    def validate_object(self, obj: dict):
        if 'Unused' in obj['path'] or not CommonTools.is_object_included(obj):
            return
        obj_type = obj['type']
        if self.cbxCamelCaseNaming.isChecked() and CommonTools.is_not_camel_cased(obj):
            self.record_problematic_object(obj, self.cbxCamelCaseNaming.text())
        if self.cbxColorConvention.isChecked() and CommonTools.has_wrong_color(obj):
            self.record_problematic_object(obj, self.cbxColorConvention.text())
        if self.cbxRepeatingNodeName.isChecked() and self.contains_repeating_path(obj):
            self.record_problematic_object(obj, self.cbxRepeatingNodeName.text())
        if self.cbxEmptyObject.isChecked() and CommonTools.is_object_empty(obj):
            self.record_problematic_object(obj, self.cbxEmptyObject.text())
        if self.cbxAssignedToMasterBus.isChecked() and MixingTools.is_bus_unassigned(obj):
            self.record_problematic_object(obj, self.cbxAssignedToMasterBus.text())
        if self.cbxMissingEventNotes.isChecked() and CommonTools.is_note_missing(obj):
            self.record_problematic_object(obj, self.cbxMissingEventNotes.text())

        if obj_type == 'Sound':
            if self.cbxInconsistentSourcePath.isChecked() and AudioSourceTools.is_source_path_inconsistent(obj):
                self.record_problematic_object(obj, self.cbxInconsistentSourcePath.text())
            if self.cbxSoundNotInEvent.isChecked() and EventTools.is_sound_not_in_event(obj):
                self.record_problematic_object(obj, self.cbxSoundNotInEvent.text())
            if self.cbxSoundNotImported.isChecked() and LocalizationTools.sound_missing_or_not_localized(obj):
                self.record_problematic_object(obj, self.cbxSoundNotImported.text())
            if self.cbxSilentVoicePlaceholder.isChecked() and AudioSourceTools.is_audio_source_silent(obj):
                self.record_problematic_object(obj, self.cbxSilentVoicePlaceholder.text())
        elif obj_type == 'AudioFileSource':
            if self.cbxTrimOutOfRange.isChecked() and AudioSourceTools.trim_out_of_range(obj):
                self.record_problematic_object(obj, self.cbxTrimOutOfRange.text())
        elif obj_type == 'Event':
            if self.cbxEventNamingMismatch.isChecked() and EventTools.naming_mismatches_target(obj):
                self.record_problematic_object(obj, self.cbxEventNamingMismatch.text())
            if self.cbxUnnecessaryEvent.isChecked() and EventTools.is_event_unnecessary(obj):
                self.record_problematic_object(obj, self.cbxUnnecessaryEvent.text())
            if self.cbxEventNotInBank.isChecked() and EventTools.is_event_not_in_bank(obj):
                self.record_problematic_object(obj, self.cbxEventNotInBank.text())
        elif obj_type == 'WorkUnit':
            if self.cbxNestedWorkUnit.isChecked() and self.is_work_unit_nested(obj):
                self.record_problematic_object(obj, self.cbxNestedWorkUnit.text())
        elif obj_type == 'ActorMixer':
            if self.cbxRedundantActorMixer.isChecked() and self.is_actor_mixer_redundant(obj):
                self.record_problematic_object(obj, self.cbxRedundantActorMixer.text())
        elif obj_type == 'GameParameter':
            if self.cbxDuplicatedRTPC.isChecked() and self.is_duplicated_rtpc(obj):
                self.record_problematic_object(obj, self.cbxDuplicatedRTPC.text())
        elif obj_type == 'SoundBank':
            if self.cbxAbnormalBankSize.isChecked() and SoundBankTools.is_bank_size_abnormal(obj):
                self.record_problematic_object(obj, self.cbxAbnormalBankSize.text())
        elif 'Container' in obj_type:
            if self.cbxSingleChildContainer.isChecked() and LogicContainerTools.has_single_child(obj):
                self.record_problematic_object(obj, self.cbxSingleChildContainer.text())

    # 记录不符合规范的对象
    def record_problematic_object(self, obj: dict, problem_type: str):
        row_count = self.tblValidationResults.rowCount()
        self.tblValidationResults.insertRow(row_count)
        problem_item = QTableWidgetItem(problem_type)
        problem_item.setForeground(QColor(200, 0, 0))
        self.tblValidationResults.setItem(row_count, 0, problem_item)
        self.tblValidationResults.setItem(row_count, 1, QTableWidgetItem(obj['type']))
        self.tblValidationResults.setItem(row_count, 2, QTableWidgetItem(obj['path']))
        self.problematicObjects.append(obj)

    # 修复大小写命名规范
    @staticmethod
    def fix_camel_case_naming(obj: dict):
        obj_name = obj['name']
        split_char = '_'
        words = obj_name.split(split_char)
        if len(words) == 1:
            split_char = ' '
            words = obj_name.split(split_char)
        new_name = ''
        for word in words:
            if not re.match(r'^[A-Z\d][a-zA-Z\d]*$', word):
                word = word.title()
            new_name += word + split_char
        new_name = new_name[:-1]
        WaapiTools.rename_object(obj, new_name)
        return True

    # 检查是否包含上一级的重复命名，如Weapon/Weapon_AR/Weapon_AR_AK47
    @staticmethod
    def contains_repeating_path(obj: dict):
        obj_path = obj['path']
        if not obj_path.startswith('\\Actor-Mixer Hierarchy') and not obj_path.startswith('\\Interactive Music Hierarchy'):
            return False

        obj_name = obj['name']
        obj_type = obj['type']
        if obj_type == 'Sound' or obj_type == 'AudioFileSource':
            return False
        # 允许ActorMixer和上级WorkUnit同名
        elif obj_type == 'ActorMixer':
            parent = WaapiTools.get_parent_objects(obj, False)
            if parent['type'] == 'WorkUnit' and parent['name'] == obj_name:
                return False

        # 被Event直接播放的对象允许使用完整命名
        references = WaapiTools.get_references_to_object(obj)
        for reference in references:
            if reference['type'] == 'Action':
                return False

        path_splits = obj_path.split('\\')
        return len(path_splits) > 2 and path_splits[-2] in obj_name

    # 修复包含上级对象重复命名
    @staticmethod
    def fix_repeating_path(obj: dict):
        path_splits = obj['path'].split('\\')
        new_name = obj['name'].replace(path_splits[-2], '')
        if new_name.startswith('_'):
            new_name = new_name[1:]
        WaapiTools.rename_object(obj, new_name)
        return True

    # 删除非必要的Event
    @staticmethod
    def remove_unnecessary_event(event: dict):
        event_name = event['name']
        # 1P/3P后缀事件转换为播放上层SwitchContainer内容
        if event_name.endswith('_1P') or event_name.endswith('_3P'):
            new_event_name = event_name[:-3]
            existing_event = WaapiTools.find_object_by_name_and_type(new_event_name, 'Event')
            if existing_event:
                return True
            WaapiTools.rename_object(event, new_event_name)
            actions = WaapiTools.get_child_objects(event, False)
            for action in actions:
                target = WaapiTools.get_object_property(action, 'Target')
                if target and target['name'].endswith(event_name[-3:]):
                    target_parent = WaapiTools.get_parent_objects(target, False)
                    if target_parent['type'] == 'SwitchContainer':
                        return EventTools.set_action_target(action, target_parent)
        # Stop类型事件直接删除
        else:
            return WaapiTools.delete_object(event)

    # 检查WorkUnit是否只包含子级WorkUnit
    @staticmethod
    def is_work_unit_nested(work_unit: dict):
        # 物理文件夹会只有一个路径，故跳过
        path_splits = work_unit['path'].split('\\')
        if len(path_splits) <= 2:
            return False
        work_unit_type = WaapiTools.get_object_property(work_unit, 'workUnitType')
        if work_unit_type == 'folder':
            return False
        children = WaapiTools.get_child_objects(work_unit, False)
        # 空的占位WorkUnit可以接受
        if len(children) == 0:
            return False
        for child in children:
            if child['type'] != 'WorkUnit':
                return False
        return work_unit['name'] != 'Default Work Unit'

    # 将嵌套的WorkUnit改为Folder类型
    @staticmethod
    def fix_nested_work_unit(work_unit: dict):
        if len(work_unit['path'].split('\\')) > 3:
            return WaapiTools.convert_to_type(work_unit, 'Folder')
        return False

    # 检查ActorMixer是否包含有效信息
    @staticmethod
    def is_actor_mixer_redundant(actor_mixer: dict):
        parent = WaapiTools.get_parent_objects(actor_mixer, False)
        if parent['type'] == 'WorkUnit':
            return False
        effects = WaapiTools.get_object_property(actor_mixer, 'Effect')
        rtpcs = WaapiTools.get_object_property(actor_mixer, '@RTPC')
        if effects or rtpcs:
            return False
        return not MixingTools.has_fader_edits(actor_mixer)

    # 将没有实际内容的对象删除
    @staticmethod
    def delete_empty_object(obj: dict):
        obj_name = obj['name']
        print(f'已删除无实际内容的对象[{obj_name}]')
        return WaapiTools.delete_object(obj)

    # 检查是否存在重复绑定的RTPC
    def is_duplicated_rtpc(self, rtpc: dict):
        built_in = WaapiTools.get_object_property(rtpc, 'BindToBuiltInParam')
        if not built_in:
            return False
        if built_in in self.builtInRTPCs:
            return True
        self.builtInRTPCs.append(built_in)
        return False

    # 删除重复绑定的RTPC
    @staticmethod
    def remove_duplicated_rtpc(obj: dict):
        # todo - reassign reference to existing rtpc
        obj_name = obj['name']
        print(f'已删除重复绑定的RTPC[{obj_name}]')
        return WaapiTools.delete_object(obj)

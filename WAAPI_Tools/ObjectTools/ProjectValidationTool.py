import re

from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox

from Libraries import WaapiTools
from ObjectTools import SoundBankTools
from QtDesign.ProjectValidation_ui import Ui_ProjectValidation
from Threading.BatchProcessor import BatchProcessor


# Wwise工程检查工具
class ProjectValidation(QDialog, Ui_ProjectValidation):

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
        self.btnValidateListEntries.clicked.connect(self.validate_list_entries)
        self.btnValidateEntireProject.clicked.connect(self.validate_entire_project)
        self.btnSendResultToMainWindow.clicked.connect(self.send_results_back)

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
        self.cbxColorMismatch.setChecked(True)
        self.cbxInconsistentSourcePath.setChecked(True)
        self.cbxMismatchedEvent.setChecked(True)
        self.cbxUnnecessaryEvent.setChecked(True)
        self.cbxUnusedSound.setChecked(True)
        self.cbxAssignedToMasterBus.setChecked(True)
        self.cbxNestedWorkUnit.setChecked(True)
        self.cbxRedundantActorMixer.setChecked(True)
        self.cbxSingleChildContainer.setChecked(True)
        self.cbxEmptyObject.setChecked(True)
        self.cbxDuplicatedRTPC.setChecked(True)
        self.cbxAbnormalBankSize.setChecked(True)

    def deselect_all(self):
        self.cbxCamelCaseNaming.setChecked(False)
        self.cbxRepeatingNodeName.setChecked(False)
        self.cbxColorMismatch.setChecked(False)
        self.cbxInconsistentSourcePath.setChecked(False)
        self.cbxMismatchedEvent.setChecked(False)
        self.cbxUnnecessaryEvent.setChecked(False)
        self.cbxUnusedSound.setChecked(False)
        self.cbxAssignedToMasterBus.setChecked(False)
        self.cbxNestedWorkUnit.setChecked(False)
        self.cbxRedundantActorMixer.setChecked(False)
        self.cbxSingleChildContainer.setChecked(False)
        self.cbxEmptyObject.setChecked(False)
        self.cbxDuplicatedRTPC.setChecked(False)
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

    # 检查主窗口列表中的对象
    def validate_list_entries(self):
        self.reset_data()
        all_objects = []
        for obj in self.__mainWindow.activeObjects:
            all_objects.append(obj)
            descendants = WaapiTools.get_child_objects(obj, True)
            all_objects += descendants
        self.__batchProcessor = BatchProcessor(all_objects, self.validate_object, 'Validating objects',
                                               self.on_validate_finished)
        self.__batchProcessor.start()

    # 检查整个Wwise工程
    def validate_entire_project(self):
        self.reset_data()
        global_objects = WaapiTools.get_global_objects()
        self.__batchProcessor = BatchProcessor(global_objects, self.validate_object, 'Validating project',
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
    def validate_object(self, obj):
        obj_type = obj['type']
        if self.cbxCamelCaseNaming.isChecked() and self.is_not_camel_cased(obj):
            self.record_problematic_object(obj, self.cbxCamelCaseNaming.text())
        if self.cbxColorMismatch.isChecked() and self.is_color_mismatched(obj):
            self.record_problematic_object(obj, self.cbxColorMismatch.text())
        if self.cbxRepeatingNodeName.isChecked() and self.contains_repeating_path(obj):
            self.record_problematic_object(obj, self.cbxRepeatingNodeName.text())
        if self.cbxEmptyObject.isChecked() and self.is_object_empty(obj):
            self.record_problematic_object(obj, self.cbxEmptyObject.text())
        if self.cbxAssignedToMasterBus.isChecked() and self.is_bus_unassigned(obj):
            self.record_problematic_object(obj, self.cbxAssignedToMasterBus.text())

        if obj_type == 'Sound':
            if self.cbxInconsistentSourcePath.isChecked() and self.is_source_path_inconsistent(obj):
                self.record_problematic_object(obj, self.cbxInconsistentSourcePath.text())
            if self.cbxUnusedSound.isChecked() and self.is_sound_unused(obj):
                self.record_problematic_object(obj, self.cbxUnusedSound.text())
        elif obj_type == 'Event':
            if self.cbxMismatchedEvent.isChecked() and self.is_event_mismatched(obj):
                self.record_problematic_object(obj, self.cbxMismatchedEvent.text())
            if self.cbxUnnecessaryEvent.isChecked() and self.is_event_unnecessary(obj):
                self.record_problematic_object(obj, self.cbxUnnecessaryEvent.text())
        elif obj_type == 'WorkUnit':
            # 物理文件夹会只有一个路径，故跳过
            path_splits = obj['path'].split('\\')
            if len(path_splits) > 2 and self.cbxNestedWorkUnit.isChecked() and self.is_work_unit_nested(obj):
                self.record_problematic_object(obj, self.cbxNestedWorkUnit.text())
        elif obj_type == 'ActorMixer':
            if self.cbxRedundantActorMixer.isChecked() and self.is_actor_mixer_redundant(obj):
                self.record_problematic_object(obj, self.cbxRedundantActorMixer.text())
        elif obj_type == 'GameParameter':
            if self.cbxDuplicatedRTPC.isChecked() and self.is_duplicated_rtpc(obj):
                self.record_problematic_object(obj, self.cbxDuplicatedRTPC.text())
        elif obj_type == 'SoundBank':
            if self.cbxAbnormalBankSize.isChecked() and self.is_bank_size_abnormal(obj):
                self.record_problematic_object(obj, self.cbxAbnormalBankSize.text())
        elif 'Container' in obj_type:
            if self.cbxSingleChildContainer.isChecked() and self.container_has_single_child(obj):
                self.record_problematic_object(obj, self.cbxSingleChildContainer.text())

    # 记录不符合规范的对象
    def record_problematic_object(self, obj, problem_type: str):
        row_count = self.tblValidationResults.rowCount()
        self.tblValidationResults.insertRow(row_count)
        self.tblValidationResults.setItem(row_count, 0, QTableWidgetItem(problem_type))
        self.tblValidationResults.setItem(row_count, 1, QTableWidgetItem(obj['type']))
        self.tblValidationResults.setItem(row_count, 2, QTableWidgetItem(obj['path']))
        self.problematicObjects.append(obj)

    # 检查对象是否符合CamelCase命名规范
    @staticmethod
    def is_not_camel_cased(obj):
        if obj['type'] == 'WorkUnit' or obj['type'] == 'Folder':
            return False
        camel_case_pattern = r'^[A-Z\d][a-zA-Z\d]*$'
        words = obj['name'].split('_')
        if len(words) == 1:
            words = obj['name'].split(' ')
        for word in words:
            if not re.match(camel_case_pattern, word):
                return True
        return False

    # 检查是否包含上一级的重复命名，如Weapon/Weapon_AR/Weapon_AR_AK47
    @staticmethod
    def contains_repeating_path(obj):
        obj_path = obj['path']
        if not obj_path.startswith('\\Actor-Mixer Hierarchy') and not obj_path.startswith(
                '\\Interactive Music Hierarchy'):
            return False

        obj_name = obj['name']
        obj_type = obj['type']
        if obj_type == 'Sound':
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

    # 检查是否符合颜色规范
    @staticmethod
    def is_color_mismatched(obj):
        color = WaapiTools.get_object_property(obj, 'color')
        parent = WaapiTools.get_parent_objects(obj, False)
        if parent:
            parent_color = WaapiTools.get_object_property(parent, 'color')
            return parent_color != 0 and color != parent_color
        return False

    # 检查源文件是否与Sound命名一致
    @staticmethod
    def is_source_path_inconsistent(obj):
        result = []
        if obj['type'] != 'Sound':
            return False
        audio_source = WaapiTools.get_audio_source_from_sound(obj)
        if audio_source is None:
            return True
        else:
            return audio_source['name'] != obj['name']

    # 检查Event和播放的对象是否一致
    @staticmethod
    def is_event_mismatched(obj):
        event_name = obj['name']
        actions = WaapiTools.get_child_objects(obj, False)
        has_matching_target = False
        for action in actions:
            action_type = WaapiTools.get_object_property(action, 'ActionType')
            if action_type <= 10:
                target = WaapiTools.get_object_property(action, 'Target')
                if not target or 'name' not in target:
                    print(f'事件[{event_name}]不包含Action或包含了丢失的对象')
                    return True
                if target['name'] in event_name:
                    has_matching_target = True
        return not has_matching_target

    # 检查是否存在不必要的Event
    @staticmethod
    def is_event_unnecessary(obj):
        # todo - check stop events
        name = obj['name']
        return name.startswith('Stop_') or name.endswith('_1P') or name.endswith('_3P')

    # 检查声音是否被事件所引用
    def is_sound_unused(self, obj):
        if obj['type'] == 'ActorMixer' or obj['type'] == 'WorkUnit':
            return True
        references = WaapiTools.get_references_to_object(obj)
        if len(references) == 0:
            parent = WaapiTools.get_parent_objects(obj, False)
            return self.is_sound_unused(parent)
        return False

    # 检查是否分配了Bus
    @staticmethod
    def is_bus_unassigned(obj):
        bus = WaapiTools.get_object_property(obj, 'OutputBus')
        if bus is None:
            return False
        is_master = bus['name'] == 'Master Audio Bus'
        override = WaapiTools.get_object_property(obj, 'OverrideOutput')
        if override:
            return is_master
        # 非override的对象需要检查是否上级已经检查过了
        parent = WaapiTools.get_parent_objects(obj, False)
        if parent and not WaapiTools.get_object_property(parent, 'OutputBus'):
            return is_master
        return False

    # 检查WorkUnit是否只包含子级WorkUnit
    @staticmethod
    def is_work_unit_nested(obj):
        work_unit_type = WaapiTools.get_object_property(obj, 'workUnitType')
        if work_unit_type == 'folder':
            return False
        children = WaapiTools.get_child_objects(obj, False)
        # 空的占位WorkUnit可以接受
        if len(children) == 0:
            return False
        for child in children:
            if child['type'] != 'WorkUnit':
                return False
        return obj['name'] != 'Default Work Unit'

    # 检查ActorMixer是否包含有效信息
    @staticmethod
    def is_actor_mixer_redundant(obj):
        parent = WaapiTools.get_parent_objects(obj, False)
        if parent['type'] == 'WorkUnit':
            return False
        effects = WaapiTools.get_object_property(obj, 'Effect')
        rtpcs = WaapiTools.get_object_property(obj, 'RTPC')
        if effects or rtpcs:
            return False
        volume = WaapiTools.get_object_property(obj, 'Volume')
        pitch = WaapiTools.get_object_property(obj, 'Pitch')
        lowpass = WaapiTools.get_object_property(obj, 'Lowpass')
        highpass = WaapiTools.get_object_property(obj, 'Highpass')
        gain = WaapiTools.get_object_property(obj, 'MakeUpGain')
        return volume == pitch == lowpass == highpass == gain == 0

    # 检查是否存在不包含或仅包含一个子节点的Container
    @staticmethod
    def container_has_single_child(obj):
        # 音乐容器可以只包含一首
        if obj['type'] == 'MusicPlaylistContainer':
            return False
        children = WaapiTools.get_child_objects(obj, False)
        return len(children) == 1

    # 检查对象是否没有实际内容
    @staticmethod
    def is_object_empty(obj):
        obj_type = obj['type']
        if obj_type == 'AudioFileSource' or obj_type == 'SoundBank' or obj_type == 'GameParameter' or 'Bus' in obj_type:
            return False
        if obj['name'] == 'Default Work Unit':
            return False
        children = WaapiTools.get_child_objects(obj, False)
        return len(children) == 0

    # 检查是否存在重复绑定的RTPC
    def is_duplicated_rtpc(self, obj):
        built_in = WaapiTools.get_object_property(obj, 'BindToBuiltInParam')
        if not built_in:
            return False
        if built_in in self.builtInRTPCs:
            return True
        self.builtInRTPCs.append(built_in)
        return False

    # 检查Bank大小是否在1-10MB之间
    @staticmethod
    def is_bank_size_abnormal(obj):
        if obj['type'] != 'SoundBank':
            return None
        wav_size, wem_size, used_files_count, unused_files = SoundBankTools.get_bank_size(obj)
        abnormal = wem_size < 1 or wem_size > 10
        if abnormal:
            bank_name = obj['name']
            size_str = '过小' if wem_size < 1 else '过大'
            print(f'Bank[{bank_name}]大小为[{wem_size}]MB，{size_str}!')
        return abnormal

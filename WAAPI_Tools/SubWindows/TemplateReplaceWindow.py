from QtDesign.ReplaceByTemplate_ui import Ui_ReplaceByTemplate
from PyQt6.QtWidgets import QDialog
from Libraries import WAAPI
from ObjectTools import SoundBankTools, LocalizationTools, AudioSourceTools


# 批量替换内容工具
class TemplateReplacer(QDialog, Ui_ReplaceByTemplate):
    __oldName = ''
    __newName = ''

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.cbxObjectType.addItems(['AudioSource', 'Event', 'SoundBank'])
        self.setup_triggers()
        self.__mainWindow = main_window

    def setup_triggers(self):
        self.btnDoReplace.clicked.connect(self.start_replacing)

    # 开始进行替换
    def start_replacing(self):
        self.__oldName = self.iptFindName.text()
        self.__newName = self.iptReplaceName.text()
        WAAPI.begin_undo_group('Batch Replace')
        for obj in self.__mainWindow.activeObjects:
            self.iterate_child_objects(obj)
        WAAPI.end_undo_group('Batch Replace')

    # 遍历子对象
    def iterate_child_objects(self, obj: dict):
        if self.cbxObjectType.currentText() == 'AudioSource' and obj['type'] == 'Sound':
            if self.__oldName in obj['name']:
                self.replace_source_wave(obj)
        elif self.cbxObjectType.currentText() == 'Event' and obj['type'] == 'Event':
            if self.__oldName in obj['name']:
                self.replace_event(obj)
        elif self.cbxObjectType.currentText() == 'SoundBank' and obj['type'] == 'SoundBank':
            if self.__oldName in obj['name']:
                self.replace_bank(obj)
        else:
            if self.__oldName in obj['name']:
                new_object_name = obj['name'].replace(self.__oldName, self.__newName)
                # 音效不需要去除_01的后缀，事件和Bank需要
                if self.cbxObjectType.currentText() != 'AudioSource':
                    new_object_name = new_object_name.replace('_01', '')
                WAAPI.rename_object(obj, new_object_name)
            for child in WAAPI.get_child_objects(obj, False):
                self.iterate_child_objects(child)

    # 对声音文件进行替换
    def replace_source_wave(self, obj: dict):
        new_sound_name = obj['name'].replace(self.__oldName, self.__newName)
        WAAPI.rename_object(obj, new_sound_name)

        sources = WAAPI.get_child_objects(obj, False)
        for source in sources:
            original_path = AudioSourceTools.get_source_file_path(source)
            language = LocalizationTools.get_sound_language(source)
            new_wave_path = original_path.replace(self.__oldName, self.__newName)
            WAAPI.delete_object(source)
            WAAPI.import_audio_file(new_wave_path, obj, new_sound_name, language)

    # 对事件名和内容进行替换
    def replace_event(self, obj: dict):
        new_event_name = obj['name'].replace(self.__oldName, self.__newName).replace('_01', '')
        WAAPI.rename_object(obj, new_event_name)
        for action in WAAPI.get_child_objects(obj, False):
            target = WAAPI.get_object_property(action, 'Target')
            target_full = WAAPI.get_full_info_from_obj_id(target['id'])
            new_target_path = target_full['path'].replace(self.__oldName, self.__newName)
            new_target = WAAPI.get_object_from_path(new_target_path)
            if new_target:
                WAAPI.set_object_reference(action, 'Target', new_target)

    # 对bank内容进行替换
    def replace_bank(self, obj: dict):
        new_bank_name = obj['name'].replace(self.__oldName, self.__newName).replace('_01', '')
        WAAPI.rename_object(obj, new_bank_name)
        new_inclusion_objects = []
        for old_inclusion_obj in WAAPI.get_bank_inclusions(obj):
            target_full = WAAPI.get_full_info_from_obj_id(old_inclusion_obj['object'])
            new_target_path = target_full['path'].replace(self.__oldName, self.__newName)
            new_target = WAAPI.get_object_from_path(new_target_path)
            if new_target:
                inclusion = {
                    'object': new_target['id'],
                    'filter': old_inclusion_obj['filter']
                }
                new_inclusion_objects.append(inclusion)
        WAAPI.clear_bank_inclusions(obj)
        SoundBankTools.add_objects_to_bank_with_individual_inclusion(obj, new_inclusion_objects)

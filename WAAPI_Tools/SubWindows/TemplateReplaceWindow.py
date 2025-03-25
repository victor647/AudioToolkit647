from QtDesign.ReplaceByTemplate_ui import Ui_ReplaceByTemplate
from PyQt6.QtWidgets import QDialog
from Libraries import WAAPI
from ObjectTools import CommonTools, LocalizationTools, AudioSourceTools


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
            if self.__oldName in obj['name']:
                new_object_name = obj['name'].replace(self.__oldName, self.__newName).replace('_01', '')
                WAAPI.rename_object(obj, new_object_name)
            self.iterate_child_objects(obj)
        WAAPI.end_undo_group('Batch Replace')

    # 遍历子对象
    def iterate_child_objects(self, obj: dict):
        replace_type = self.cbxObjectType.currentText()
        obj_type = obj['type']
        if replace_type == 'AudioSource' and obj_type == 'Sound':
            if self.__oldName in obj['name']:
                self.replace_source_wave(obj)
        elif replace_type == 'Event' and obj_type == 'Event':
            if self.__oldName in obj['name']:
                self.replace_event(obj)
        elif replace_type == 'SoundBank' and obj_type == 'SoundBank':
            if self.__oldName in obj['name']:
                self.replace_bank(obj)
        else:
            for child in WAAPI.get_child_objects(obj):
                self.iterate_child_objects(child)

    # 对声音文件进行替换
    def replace_source_wave(self, obj: dict):
        new_sound_name = obj['name'].replace(self.__oldName, self.__newName)
        WAAPI.rename_object(obj, new_sound_name)

        sources = WAAPI.get_child_objects(obj)
        for source in sources:
            original_path = AudioSourceTools.get_source_file_path(source)
            language = LocalizationTools.get_sound_language(source)
            new_wave_path = original_path.replace(self.__oldName, self.__newName)
            WAAPI.delete_object(source)
            WAAPI.import_audio_file(new_wave_path, obj, language)

    # 对事件名和内容进行替换
    def replace_event(self, obj: dict):
        new_event_name = obj['name'].replace(self.__oldName, self.__newName).replace('_01', '')
        WAAPI.rename_object(obj, new_event_name)
        for action in WAAPI.get_child_objects(obj):
            target = WAAPI.get_object_property(action, 'Target')
            target_full = WAAPI.get_full_info_from_obj_id(target['id'])
            new_target_path = target_full['path'].replace(self.__oldName, self.__newName)
            new_target = WAAPI.find_object_by_path(new_target_path)
            if new_target:
                WAAPI.set_object_reference(action, 'Target', new_target)
                CommonTools.update_notes_and_color(obj)

    # 对bank内容进行替换
    def replace_bank(self, bank: dict):
        new_bank_name = bank['name'].replace(self.__oldName, self.__newName).replace('_01', '')
        WAAPI.rename_object(bank, new_bank_name)
        old_inclusions = WAAPI.get_bank_inclusions(bank)
        WAAPI.clear_bank_inclusions(bank)
        for old_inclusion_obj in old_inclusions:
            target_full = WAAPI.get_full_info_from_obj_id(old_inclusion_obj['object'])
            new_target_path = target_full['path'].replace(self.__oldName, self.__newName)
            new_target = WAAPI.find_object_by_path(new_target_path)
            WAAPI.set_bank_inclusion(bank, new_target, False, old_inclusion_obj['filter'])
        return True

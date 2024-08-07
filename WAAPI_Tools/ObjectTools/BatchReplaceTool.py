from QtDesign.BatchReplaceTool_ui import Ui_BatchReplaceTool
from PyQt5.QtWidgets import QDialog
from Libraries import WaapiTools
from ObjectTools import SoundBankTools


# 批量替换内容工具
class BatchReplaceTool(QDialog, Ui_BatchReplaceTool):
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
        WaapiTools.begin_undo_group()
        for obj in self.__mainWindow.activeObjects:
            self.iterate_child_objects(obj)
        WaapiTools.end_undo_group('Batch Replace')

    # 遍历子对象
    def iterate_child_objects(self, obj):
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
                WaapiTools.rename_object(obj, new_object_name)
            for child in WaapiTools.get_child_objects(obj, False):
                self.iterate_child_objects(child)

    # 对声音文件进行替换
    def replace_source_wave(self, sound_obj):
        new_sound_name = sound_obj['name'].replace(self.__oldName, self.__newName)
        WaapiTools.rename_object(sound_obj, new_sound_name)

        sources = WaapiTools.get_child_objects(sound_obj, False)
        for source in sources:
            original_path = WaapiTools.get_object_property(source, 'sound:originalWavFilePath')
            language = WaapiTools.get_sound_language(source)
            new_wave_path = original_path.replace(self.__oldName, self.__newName)
            WaapiTools.delete_object(source)
            WaapiTools.import_audio_file(new_wave_path, sound_obj, new_sound_name, language)

    # 对事件名和内容进行替换
    def replace_event(self, event_obj):
        new_event_name = event_obj['name'].replace(self.__oldName, self.__newName).replace('_01', '')
        WaapiTools.rename_object(event_obj, new_event_name)
        for action in WaapiTools.get_child_objects(event_obj, False):
            target = WaapiTools.get_object_property(action, '@Target')
            target_full = WaapiTools.get_full_info_from_obj_id(target['id'])
            new_target_path = target_full['path'].replace(self.__oldName, self.__newName)
            new_target = WaapiTools.get_object_from_path(new_target_path)
            if new_target:
                WaapiTools.set_object_reference(action, 'Target', new_target)

    # 对bank内容进行替换
    def replace_bank(self, bank_obj):
        new_bank_name = bank_obj['name'].replace(self.__oldName, self.__newName).replace('_01', '')
        WaapiTools.rename_object(bank_obj, new_bank_name)
        new_inclusion_objects = []
        for old_inclusion_obj in SoundBankTools.get_bank_inclusions(bank_obj):
            target_full = WaapiTools.get_full_info_from_obj_id(old_inclusion_obj['object'])
            new_target_path = target_full['path'].replace(self.__oldName, self.__newName)
            new_target = WaapiTools.get_object_from_path(new_target_path)
            if new_target:
                inclusion = {
                    'object': new_target['id'],
                    'filter': old_inclusion_obj['filter']
                }
                new_inclusion_objects.append(inclusion)
        SoundBankTools.clear_bank_inclusions(bank_obj)
        SoundBankTools.add_objects_to_bank_with_individual_inclusion(bank_obj, new_inclusion_objects)
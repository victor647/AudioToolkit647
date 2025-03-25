import os
import shutil
import logging
import xml.etree.ElementTree as ElementTree
from Libraries import WAAPI, FileTools, ScriptingHelper
from ObjectTools import ProjectTools, AudioSourceTools, MixingTools, GameSyncTools
from PyQt6.QtWidgets import QDialog
from QtDesign.WorkUnitImporter_ui import Ui_WorkUnitImporter


# 导入WorkUnit到另一个Wwise工程
class WorkUnitImporter(QDialog, Ui_WorkUnitImporter):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__sourceProjectPath = ''
        self.__objectCount = 0

    def setup_triggers(self):
        self.btnStartImport.clicked.connect(self.start_import)

    # 从WorkUnit中根据名称导入对象
    def start_import(self):
        root, path = FileTools.import_from_work_unit()
        if not root or not path:
            return
        index = path.find('Actor-Mixer Hierarchy')
        rel_path = path[index:]
        self.__sourceProjectPath = path[:index]
        self.__objectCount = 0
        folder_path = os.path.dirname(rel_path)
        folder = WAAPI.find_object_by_path(folder_path)
        if folder is None:
            folder = WAAPI.create_object_by_path(folder_path, 'Physical Folder')
        if folder:
            for node in root.find('AudioObjects'):
                self.parse_node(node, folder)
            ScriptingHelper.show_message_box('导入完成', f'共导入{self.__objectCount}个对象！')
        self.lblCurrentObject.setText('')
        self.lblObjectCount.setText('')

    # 遍历Wwu节点
    def parse_node(self, node: ElementTree, parent_obj: dict):
        obj_type = node.tag
        if obj_type == 'AudioFileSource':
            if self.cbxImportSourceFile.isChecked():
                self.import_audio_file(node, parent_obj)
            return

        obj_name = node.attrib['Name']
        obj_path = str(os.path.join(parent_obj['path'], obj_name))
        obj = WAAPI.find_object_by_path(obj_path)
        self.lblCurrentObject.setText(obj_name)
        self.__objectCount += 1
        self.lblObjectCount.setText(f'已导入{self.__objectCount}个对象')
        self.repaint()
        if obj is None:
            obj = WAAPI.create_child_object(obj_name, obj_type, parent_obj)
        if obj is None:
            logging.error(f'Cannot create {obj_type} named {obj_name}!')
            return
        for element in node:
            if element.tag == 'ChildrenList':
                for child_node in element:
                    self.parse_node(child_node, obj)
            elif element.tag == 'PropertyList':
                for child_node in element:
                    import_property(child_node, obj)
            elif element.tag == 'ReferenceList':
                for child_node in element:
                    self.import_reference(child_node, obj)
            elif element.tag == 'ObjectLists':
                for child_node in element:
                    self.import_object_list(child_node, obj)
            elif element.tag == 'GroupingInfo':
                import_grouping_list(element.find('GroupingList'), obj)
            elif element.tag == 'Comment':
                WAAPI.set_object_notes(obj, element.text)

    # 根据名称获取引用
    def import_reference(self, node: ElementTree, obj: dict):
        ref_name = node.attrib['Name']
        ref_type = ref_name
        value_node = node.find('ObjectRef')
        if value_node is None:
            return
        ref_obj_name = value_node.attrib['Name']

        if ref_name == 'OutputBus':
            if not self.cbxImportBus.isChecked():
                return
            ref_type = 'Bus'
        elif ref_name == 'SwitchGroupOrStateGroup':
            ref_type = 'SwitchGroup'
            if 'Ambience' in obj['path']:
                ref_type = 'StateGroup'
        elif ref_name == 'DefaultSwitchOrState':
            import_default_switch(node, obj)
            return
        elif ref_name == 'Attenuation':
            if not self.cbxImportAttenuation.isChecked():
                return
        elif ref_name == 'Conversion':
            if not self.cbxImportConversion.isChecked():
                return

        ref_obj = WAAPI.find_object_by_name_and_type(ref_obj_name, ref_type)
        if ref_obj:
            WAAPI.set_object_reference(obj, ref_name, ref_obj)
        else:
            if self.cbbMissingAction.currentText() == '忽略':
                logging.error(f'Cannot find reference of type [{ref_type}] named [{ref_obj_name}]!')
            elif self.cbbMissingAction.currentText() == '警告':
                ScriptingHelper.show_message_box('导入失败', f'找不到名为{ref_obj_name}的{ref_type}, 无法设置引用！')
            elif self.cbbMissingAction.currentText() == '创建':
                new_obj = WAAPI.create_object_at_default_location(ref_obj_name, ref_type)
                if new_obj is None:
                    logging.error(f'Failed to create {ref_type} named {ref_obj_name}!')
                else:
                    WAAPI.set_object_reference(obj, ref_name, new_obj)

    # 导入Effect/RTPC等对象
    def import_object_list(self, node: ElementTree, obj: dict):
        if node.attrib['Name'] == 'RTPC' and self.cbxImportRTPC.isChecked():
            import_rtpc(node, obj)
        if node.attrib['Name'] == 'Effects' and self.cbxImportEffects.isChecked():
            import_effects(node, obj)

    # 导入音频文件
    def import_audio_file(self, source_node: ElementTree, sound: dict):
        language = 'SFX'
        for info_node in source_node:
            if info_node.tag == 'Language':
                language = info_node.text
            elif info_node.tag == 'AudioFile':
                new_wav_path = str(os.path.join(ProjectTools.get_originals_folder(), language, info_node.text))
                if not os.path.exists(new_wav_path):
                    old_wav_path = os.path.join(self.__sourceProjectPath, 'Originals', language, info_node.text)
                    if os.path.exists(old_wav_path):
                        os.makedirs(os.path.dirname(new_wav_path), exist_ok=True)
                        shutil.copy(old_wav_path, new_wav_path)
                        WAAPI.import_audio_file(new_wav_path, sound, language)
                    else:
                        logging.error(f'Original file [{old_wav_path}] not found!')
                        continue
                else:
                    existing_wav_path = AudioSourceTools.get_source_file_path(sound)
                    if existing_wav_path is None or not os.path.samefile(new_wav_path, existing_wav_path):
                        WAAPI.import_audio_file(new_wav_path, sound, language)


# 导入属性值
def import_property(node: ElementTree, obj: dict):
    property_name = node.attrib['Name']
    if 'Value' in node.attrib:
        value = node.attrib['Value']
        WAAPI.set_object_property(obj, property_name, value)
    elif node.find('ValueList'):
        value_list = node.find('ValueList')
        for value_node in value_list:
            if 'Platform' in value_node.attrib:
                platform = value_node.attrib['Platform']
                if ProjectTools.has_platform(platform):
                    WAAPI.set_object_property(obj, property_name, value_node.text, platform)
            else:
                WAAPI.set_object_property(obj, property_name, value_node.text)


# 导入组策略（如Switch分配）
def import_grouping_list(node: ElementTree, obj: dict):
    switch_group = WAAPI.get_object_property(obj, 'SwitchGroupOrStateGroup')
    if switch_group is None:
        return
    children = WAAPI.get_child_objects(obj)
    WAAPI.remove_switch_mappings(obj)
    for grouping in node:
        switch_name = grouping.find('SwitchRef').attrib['Name']
        value = GameSyncTools.find_or_create_switch_value(switch_group, switch_name)
        for item_ref in grouping.find('ItemList'):
            item_name = item_ref.attrib['Name']
            for child in children:
                if child['name'] == item_name:
                    WAAPI.assign_switch_mapping(child, value)


# 导入默认的Switch或State值
def import_default_switch(node: ElementTree, obj: dict):
    switch_group = WAAPI.get_object_property(obj, 'SwitchGroupOrStateGroup')
    if switch_group is None:
        return
    switch_name = node.find('ObjectRef').attrib['Name']
    option = GameSyncTools.find_or_create_switch_value(switch_group, switch_name)
    if option:
        WAAPI.set_object_reference(obj, 'DefaultSwitchOrState', option)


# 导入RTPC（仅对2022版本后生效）
def import_rtpc(node: ElementTree, obj: dict):
    GameSyncTools.clear_rtpc(obj)
    for ref_node in node:
        points = []
        rtpc_name = ''
        rtpc_node = ref_node.find('Local').find('RTPC')
        for sub_ref_node in rtpc_node.find('ReferenceList'):
            ref_type = sub_ref_node.attrib['Name']
            if ref_type == 'ControlInput':
                rtpc_name = sub_ref_node.find('ObjectRef').attrib['Name']
            elif ref_type == 'Curve':
                for point_node in sub_ref_node.find('Custom').find('Curve').find('PointList'):
                    shape = point_node.find('SegmentShape')
                    point = {
                        'x': float(point_node.find('XPos').text),
                        'y': float(point_node.find('YPos').text),
                        'shape': shape.text if shape is not None else 'Linear'
                    }
                    points.append(point)
        if rtpc_name != '':
            rtpc_obj = WAAPI.find_object_by_name_and_type(rtpc_name, 'GameParameter')
            if rtpc_obj:
                property_name = rtpc_node.find('PropertyList').find('Property').attrib['Value']
                WAAPI.add_rtpc(obj, rtpc_obj, property_name, points)
            else:
                ScriptingHelper.show_message_box('导入失败', f'找不到名为{rtpc_name}的RTPC, 无法设置引用！')


# 导入对象上绑定的插件
def import_effects(node: ElementTree, obj: dict):
    MixingTools.clear_effects(obj)
    for ref_node in node:
        effect_node = ref_node.find('Local').find('EffectSlot').find('ReferenceList').find('Reference')
        if 'PluginName' in effect_node.attrib:
            share_set = effect_node.find('ObjectRef')
            share_set_name = share_set.attrib['Name']
            WAAPI.add_effect(obj, share_set_name)
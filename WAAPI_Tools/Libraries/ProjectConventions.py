import os
import re
import json
from ObjectTools import ProjectTools

Conventions = {}


# 初始化工程规范配置文件
def init():
    project_directory = ProjectTools.get_project_directory()
    json_path = os.path.join(project_directory, 'ProjectConventions.json')
    if not os.path.exists(json_path):
        json_path = 'ProjectConventions.json'
    global Conventions
    Conventions = json.load(open(json_path, 'r'))


# 根据对象的名称获取类型
def get_object_category(obj: dict):
    if not Conventions or 'ColorMap' not in Conventions:
        return None
    obj_path = obj['path']
    splits = obj_path.split('\\')[1:]
    for name in splits:
        for key, value in Conventions['ColorMap'].items():
            if key in name:
                return key
    return None


# 根据对象的类型获取应当的颜色
def get_color_by_category(category: str):
    if not Conventions or 'ColorMap' not in Conventions:
        return 0
    for key, value in Conventions['ColorMap'].items():
        if key in category:
            return value
    return 0


# 根据全名获取缩写名
def convert_category_to_acronym(category: str):
    if not Conventions or 'AcronymMap' not in Conventions:
        return category
    for key, value in Conventions['AcronymMap'].items():
        if key in category:
            return value
    return category


# 根据全名获取缩写名
def convert_acronym_to_category(acronym: str):
    if not Conventions or 'AcronymMap' not in Conventions:
        return acronym
    for key, value in Conventions['AcronymMap'].items():
        if acronym == value:
            return key
    return acronym


# 在名称中去除缩写
def remove_acronym_from_name(obj_name: str):
    if not Conventions or 'AcronymMap' not in Conventions:
        return obj_name
    for key, value in Conventions['AcronymMap'].items():
        if value in obj_name:
            obj_name = obj_name.replace(value, key)
    return obj_name


# 添加缩写到名称中
def add_acronym_from_name(obj_name: str):
    if not Conventions or 'AcronymMap' not in Conventions:
        return obj_name
    for key, value in Conventions['AcronymMap'].items():
        if key in obj_name:
            obj_name = obj_name.replace(key, value)
    return obj_name


# 根据容器类型获取对应末尾命名规范
def get_container_suffix_pattern(container_type: str):
    if not Conventions or 'ContainerSuffix' not in Conventions:
        return None
    if container_type not in Conventions['ContainerSuffix']:
        return None
    return Conventions['ContainerSuffix'][container_type]


# 获取1P/2P/3P的后缀
def get_net_role_suffix(role: str):
    if not Conventions or 'NetRole' not in Conventions:
        return '_' + role
    return Conventions['NetRole']['Suffix'][role]


# 获取1P/2P/3P的SwitchGroup名称
def get_net_role_switch_group():
    if not Conventions or 'NetRole' not in Conventions:
        return 'Net_Role'
    return Conventions['NetRole']['SwitchGroup']


# 获取1P/2P/3P的Switch名称
def get_net_role_switch_name(role: str):
    if not Conventions or 'NetRole' not in Conventions:
        return 'Net_Role'
    return Conventions['NetRole']['SwitchValues'][role]


# 判定对象的名称是否包含123P的后缀
def get_net_role_suffix_from_name(obj_name: str):
    if not Conventions:
        pattern = re.search(r'_[1-3]P$', obj_name)
        if not pattern:
            return None
        return pattern.group()
    for suffix in Conventions['NetRole']['Suffix'].values():
        if suffix in obj_name:
            return suffix
    return None


# 获取1P默认的后缀
def get_default_net_role_suffix():
    if not Conventions:
        return '_1P'
    return Conventions['NetRole']['Suffix']['1P']


# 获取已经接入的语言列表
def get_implemented_languages():
    if not Conventions or 'ImplementedLanguages' not in Conventions:
        return ['Chinese', 'English']
    return Conventions['ImplementedLanguages']


# 是否使用全名作为Sound节点名称
def use_full_name_in_sound():
    if not Conventions or 'FullNameInSound' not in Conventions:
        return False
    return Conventions['FullNameInSound']


# 事件是否以Play_开头
def has_event_play_prefix():
    if not Conventions or 'PlayPrefixInEvent' not in Conventions:
        return False
    return Conventions['PlayPrefixInEvent']
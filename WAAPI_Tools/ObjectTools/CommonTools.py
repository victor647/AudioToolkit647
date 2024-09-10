import re
from Libraries import WaapiTools, ScriptingTools
from ObjectTools import EventTools


# 检查对象是否处于勾选状态
def is_object_included(obj: dict):
    included = WaapiTools.get_object_property(obj, 'Inclusion')
    if included is None:
        return True
    return included


# 通过递归拼成全名，用于创建Event或SoundBank
def get_full_name_with_acronym(obj: dict):
    obj_name = obj['name']
    # 如果对象本身包含了下划线，视为完整路径
    if '_' in obj_name:
        return obj_name
    return get_full_name(obj, obj['name'], True)


def get_full_name(obj: dict, name: str, acronym: bool):    
    if obj['type'] == 'Sound':
        return name
    parent = WaapiTools.get_parent_objects(obj, False)
    if parent is None:
        return name
    parent_name = parent['name']
    if parent_name == obj['name']:
        return get_full_name(parent, name, acronym)

    if acronym:
        short_name = ScriptingTools.convert_category_to_acronym(parent_name)
        if short_name != parent_name:
            return f'{short_name}_{name}'
    elif parent['type'] == 'WorkUnit':
        return name

    name = f'{parent_name}_{name}'
    return get_full_name(parent, name, acronym)


# 重命名为不包含重复名称的最简名称
def rename_to_short_name(obj: dict):
    if obj['type'] == 'Sound':
        return True
    short_name = get_short_name(obj, obj['name'])
    return WaapiTools.rename_object(obj, short_name)


def get_short_name(obj: dict, name: str):
    parent = WaapiTools.get_parent_objects(obj, False)
    if not parent:
        return name
    parent_name = parent['name']
    if parent_name in name:
        name = name.replace(parent_name + '_', '')
    else:
        acronym = ScriptingTools.convert_category_to_acronym(parent_name)
        if acronym != parent_name and acronym in name:
            name = name.replace(acronym + '_', '')
    return get_short_name(parent, name)


# 检查对象是否没有实际内容
def is_object_empty(obj: dict):
    obj_type = obj['type']
    if obj_type == 'AudioFileSource' or obj_type == 'SoundBank' or obj_type == 'GameParameter' or obj_type == 'Action' or 'Bus' in obj_type:
        return False
    if obj['name'] == 'Default Work Unit':
        return False
    children = WaapiTools.get_child_objects(obj, False)
    return len(children) == 0


# 检查对象是否符合CamelCase命名规范
def is_not_camel_cased(obj: dict):
    if obj['type'] == 'Action':
        return False
    obj_name = obj['name']
    words = obj_name.split('_')
    if len(words) == 1:
        words = obj_name.split(' ')
    for word in words:
        if len(word) > 1 and not re.match(r'^[A-Z\d][a-zA-Z\d]*$', word):
            return True
    return False


# 检查是否符合颜色规范
def has_wrong_color(obj: dict):
    reference = WaapiTools.get_references_to_object(obj)
    obj_color = get_object_color(obj)
    parent = WaapiTools.get_parent_objects(obj, False)
    if not parent:
        return False
    parent_color = get_object_color(parent)
    if len(reference) == 0:
        # 最上一层或带引用对象的下级
        if parent_color == 0 or obj_color - parent_color == 13:
            return False
        return obj_color != parent_color
    else:
        # 存在引用，检查是否深浅对应
        parent = WaapiTools.get_parent_objects(obj, False)
        parent_color = get_object_color(parent)
        return parent_color - obj_color != 13


# 检查带引用的对象是否缺少备注
def is_note_missing(obj: dict):
    if obj['type'] == 'Event':
        notes = WaapiTools.get_object_property(obj, 'Notes')
        return notes == ''
    else:
        references = WaapiTools.get_references_to_object(obj)
        for reference in references:
            ref_type = reference['type']
            if ref_type == 'Action' or ref_type == 'SoundBank':
                notes = WaapiTools.get_object_property(obj, 'Notes')
                return notes == ''
    return False


# 更新带引用对象的备注和颜色
def update_notes_and_color(obj: dict):
    # 对象是Event
    if obj['type'] == 'Event':
        target = EventTools.get_event_target(obj)
        if target:
            event_name = obj['name']
            WaapiTools.set_object_notes(target, f'Referenced by Event [{event_name}]')
            target_path = WaapiTools.get_object_property(target, 'path')
            WaapiTools.set_object_notes(obj, target_path)
            set_dark_color(target)
            return True
    # 对象是Event播放目标
    else:
        references = WaapiTools.get_references_to_object(obj)
        for reference in references:
            ref_type = reference['type']
            if ref_type == 'Action':
                event = WaapiTools.get_parent_objects(reference, False)
                event_name = event['name']
                WaapiTools.set_object_notes(obj, f'Referenced by Event [{event_name}]')
                target_path = obj['path']
                WaapiTools.set_object_notes(event, target_path)
                set_dark_color(obj)
                return True
            if ref_type == 'SoundBank':
                WaapiTools.set_object_notes(obj, f"Included by SoundBank [{reference['name']}]")
                set_dark_color(obj)
                return True
    return False


# 将对象的颜色设为深色
def set_dark_color(obj: dict):
    light_color = get_object_color(obj)
    # 已经是深色了，不需要设置
    if light_color <= 13:
        return
    dark_color = light_color - 13
    set_object_color(obj, dark_color)
    children = WaapiTools.get_child_objects(obj, False)
    for child in children:
        set_object_color(child, light_color)


# 设置对象的勾选状态
def set_object_inclusion(obj: dict, enabled: bool):
    return WaapiTools.set_object_property(obj, 'Inclusion', enabled)


# 对象是否设置了特殊颜色
def has_color_override(obj: dict):
    return WaapiTools.get_object_property(obj, 'OverrideColor')


# 获取对象的颜色
def get_object_color(obj: dict):
    return WaapiTools.get_object_property(obj, 'Color')


# 设置对象的颜色
def set_object_color(obj: dict, color: int):
    WaapiTools.set_object_property(obj, 'OverrideColor', True)
    WaapiTools.set_object_property(obj, 'Color', color)
    print(f"Color of {obj['type']} [{obj['name']}] set to {color}")


def rename_to_lower_case(obj: dict):
    new_name = obj['name'].lower()
    if new_name != obj['name']:
        WaapiTools.rename_object(obj, new_name)


def rename_to_title_case(obj: dict):
    new_name = obj['name'].title()
    if new_name != obj['name']:
        WaapiTools.rename_object(obj, new_name)


def rename_to_upper_case(obj: dict):
    new_name = obj['name'].upper()
    if new_name != obj['name']:
        WaapiTools.rename_object(obj, new_name)


# 移除对象末尾_后面的名字
def remove_suffix(obj: dict):
    old_name = obj['name']
    splits = old_name.split('_')
    suffix_length = len(splits[-1]) + 1
    new_name = old_name[:-suffix_length]
    WaapiTools.rename_object(obj, new_name)


# 在对象上添加RTPC控制
def add_rtpc(obj: dict):
    pass

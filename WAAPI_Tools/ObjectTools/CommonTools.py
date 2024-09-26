import os.path
from Libraries import WAAPI, ProjectConventions
from ObjectTools import EventTools, AudioSourceTools, LogicContainerTools


# 检查对象是否处于勾选状态
def is_object_included(obj: dict):
    included = WAAPI.get_object_property(obj, 'Inclusion')
    if included is None:
        return True
    return included


# 重命名为包含完整路径的名称
def rename_to_full_name(obj: dict):
    full_name = get_full_name_with_acronym(obj)
    return WAAPI.rename_object(obj, full_name)


# 通过递归拼成全名，用于创建Event或SoundBank
def get_full_name_with_acronym(obj: dict):
    obj_name = obj['name']
    # 如果对象本身包含了下划线，视为完整路径
    if '_' in obj_name:
        return obj_name
    return get_full_name(obj, obj['name'], True)


def get_full_name(obj: dict, name: str, acronym: bool):
    parent = WAAPI.get_parent_object(obj)
    if parent is None:
        return name
    parent_name = parent['name']
    if parent_name == obj['name']:
        return get_full_name(parent, name, acronym)

    if acronym:
        short_name = ProjectConventions.convert_category_to_acronym(parent_name)
        if short_name != parent_name:
            return f'{short_name}_{name}'
    elif parent['type'] == 'WorkUnit':
        return name

    name = f'{parent_name}_{name}'
    return get_full_name(parent, name, acronym)


# 优化对象的名称长度
def optimize_name_length(obj: dict):
    obj_path = obj['path']
    obj_type = obj['type']
    if obj_path.startswith('\\Actor-Mixer Hierarchy'):
        if obj_type == 'Sound':
            if AudioSourceTools.sound_play_from_plugin(obj):
                return rename_to_short_name(obj)
            return rename_to_full_name(obj)
        return rename_to_short_name(obj)
    elif obj_path.startswith('\\Interactive Music Hierarchy'):
        if obj_type == 'MusicSegment' or obj_type == 'MusicTrack':
            return True
        return rename_to_short_name(obj)
    else:
        print(f"{obj_type} [{obj['name']}] does not need to follow naming length convention.")
        return False


# 重命名为不包含重复名称的最简名称
def rename_to_short_name(obj: dict):
    short_name = get_short_name(obj, obj['name'])
    return WAAPI.rename_object(obj, short_name)


def get_short_name(obj: dict, name: str):
    parent = WAAPI.get_parent_object(obj)
    if not parent:
        return name
    parent_name = parent['name']
    if parent_name in name:
        name = name.replace(parent_name + '_', '')
    else:
        acronym = ProjectConventions.convert_category_to_acronym(parent_name)
        if acronym != parent_name and acronym in name:
            name = name.replace(acronym + '_', '')
    return get_short_name(parent, name)


# 检查是否符合颜色规范
def has_wrong_color(obj: dict):
    obj_type = obj['type']
    reference = WAAPI.get_references_to_object(obj)
    obj_color = get_object_color(obj)
    parent = WAAPI.get_parent_object(obj)
    if not parent:
        return False
    parent_color = get_object_color(parent)
    if len(reference) == 0:
        # 最上一层或带引用对象的下级
        if parent_color == 0 or obj_color - parent_color == 13:
            return False
        return obj_color != parent_color
    elif obj_type != 'GameParameter' and obj_type != 'Bus':
        # 存在引用，检查是否深浅对应
        parent = WAAPI.get_parent_object(obj)
        parent_color = get_object_color(parent)
        return parent_color - obj_color != 13
    return False


# 获取对象的备注
def get_object_notes(obj: dict):
    return WAAPI.get_object_property(obj, 'Notes')


# 更新带引用对象的备注和颜色
def update_notes_and_color(obj: dict):
    set_object_color_by_category(obj)
    # 对象是Event
    if obj['type'] == 'Event':
        targets = EventTools.get_event_targets(obj)
        if len(targets) == 1:
            target = targets[0]
            event_name = obj['name']
            WAAPI.set_object_notes(target, f'Referenced by Event [{event_name}]')
            WAAPI.set_object_notes(obj, target['path'])
            set_object_color_by_category(target)
            set_dark_color(target)
            set_light_color(obj)
            return True
    # 对象是Event播放目标
    else:
        references = WAAPI.get_references_to_object(obj)
        for reference in references:
            ref_type = reference['type']
            if ref_type == 'Action':
                event = WAAPI.get_parent_object(reference)
                event_name = event['name']
                WAAPI.set_object_notes(obj, f'Referenced by Event [{event_name}]')
                target_path = obj['path']
                WAAPI.set_object_notes(event, target_path)
                set_dark_color(obj)
                set_object_color_by_category(event)
                return True
            if ref_type == 'SoundBank':
                WAAPI.set_object_notes(obj, f"Included by SoundBank [{reference['name']}]")
                set_object_color_by_category(reference)
                set_dark_color(obj)
                return True
    return False


# 将对象的颜色设为深色
def set_dark_color(obj: dict):
    light_color = get_object_color(obj)
    # 已经是深色了，不需要设置
    if light_color <= 13:
        return False
    dark_color = light_color - 13
    set_object_color(obj, dark_color)
    children = WAAPI.get_child_objects(obj, False)
    for child in children:
        set_object_color(child, light_color)
    return True


# 将对象的颜色设为浅色
def set_light_color(obj: dict):
    parent = WAAPI.get_parent_object(obj)
    parent_color = get_object_color(parent)
    if 0 < parent_color <= 13:
        return set_object_color(obj, parent_color + 13)
    return False


# 勾选对象
def set_included(obj: dict):
    return WAAPI.set_object_property(obj, 'Inclusion', True)


# 取消勾选对象
def set_excluded(obj: dict):
    return WAAPI.set_object_property(obj, 'Inclusion', False)


# 获取对象的颜色
def get_object_color(obj: dict):
    return WAAPI.get_object_property(obj, 'Color')


# 根据对象的类型自动识别并设置颜色
def set_object_color_by_category(obj: dict):
    category = ProjectConventions.get_object_category(obj)
    if not category:
        return False
    color = ProjectConventions.get_color_by_category(category)
    return set_object_color(obj, color)


# 设置对象的颜色
def set_object_color(obj: dict, color: int):
    print(f"Color of {obj['type']} [{obj['name']}] set to {color}")
    WAAPI.set_object_property(obj, 'OverrideColor', True)
    return WAAPI.set_object_property(obj, 'Color', color)


def rename_to_lower_case(obj: dict):
    new_name = obj['name'].lower()
    if new_name != obj['name']:
        return WAAPI.rename_object(obj, new_name)
    return False


def rename_to_title_case(obj: dict):
    new_name = obj['name'].title()
    if new_name != obj['name']:
        return WAAPI.rename_object(obj, new_name)
    return False


def rename_to_upper_case(obj: dict):
    new_name = obj['name'].upper()
    if new_name != obj['name']:
        return WAAPI.rename_object(obj, new_name)
    return False


# 获取特定类型的全部子对象
def get_descendants_by_type(obj: dict, type_name: str):
    parent_obj = obj
    descendants = WAAPI.get_child_objects(parent_obj, True)
    return [obj for obj in descendants if obj['type'] == type_name]


# 移除对象末尾_后面的名字
def remove_name_suffix(obj: dict):
    old_name = obj['name']
    splits = old_name.split('_')
    suffix_length = len(splits[-1]) + 1
    new_name = old_name[:-suffix_length]
    WAAPI.rename_object(obj, new_name)


# 为对象创建父级
def create_parent(obj: dict, target_type: str):
    # 先在父级创建一个不同名的新对象
    old_parent = WAAPI.get_parent_object(obj)
    original_name = obj['name']
    new_parent = WAAPI.create_object(original_name + '_Temp', target_type, old_parent, 'rename')
    if new_parent is None:
        return
    WAAPI.move_object(obj, new_parent)
    # 将新对象重命名成原对象名
    WAAPI.rename_object(new_parent, original_name)
    print(f'Parent of type {target_type} created for {obj}')
    return new_parent


# 为路径依次创建文件夹
def create_folders_for_path(path: str):
    obj = WAAPI.get_object_from_path(path)
    if obj:
        return obj
    splits = path.split('\\')
    node_path = '\\' + splits[1]
    parent = WAAPI.get_object_from_path(node_path)
    node = None
    for i in range(2, len(splits)):
        node_name = ProjectConventions.convert_acronym_to_category(splits[i])
        node_path = f'{node_path}\\{node_name}'
        node = WAAPI.get_object_from_path(node_path)
        if not node:
            node = WAAPI.create_object(node_name, 'Folder', parent)
        parent = node
    return node


# 根据命名中的下划线移到文件夹中
def split_underscore_to_folder(obj: dict):
    obj_name = obj['name']
    if '_' not in obj_name:
        return False
    splits = obj_name.split('_')
    folder_name = splits[0]
    # 先找已有文件夹，找不到就创建
    folder_path = str(os.path.join(os.path.dirname(obj['path']), folder_name))
    folder = WAAPI.get_object_from_path(folder_path)
    if not folder:
        parent = WAAPI.get_parent_object(obj)
        folder = WAAPI.create_object(folder_name, 'Folder', parent)
    WAAPI.move_object(obj, folder)
    WAAPI.rename_object(obj, obj_name[len(folder_name) + 1:])


# 将对象转换类型
def convert_to_type(obj: dict, target_type: str):
    # 先在父级创建一个不同名的新对象
    parent = WAAPI.get_parent_object(obj)
    original_name = obj['name']
    new_obj = WAAPI.create_object(original_name + '_Temp', target_type, parent, 'rename')
    # 创建失败，返回
    if new_obj is None:
        return False
    # 将所有子对象移至新对象上
    for child in WAAPI.get_child_objects(obj, False):
        WAAPI.move_object(child, new_obj)
    # 刷新SwitchContainer分配
    if parent['type'] == 'SwitchContainer':
        mappings = LogicContainerTools.get_switch_mappings(parent)
        for mapping in mappings:
            if mapping['child'] == obj['id']:
                LogicContainerTools.assign_switch_mapping(new_obj, mapping['stateOrSwitch'])
    # 删除原对象
    WAAPI.delete_object(obj)
    # 将新对象重命名成原对象名
    WAAPI.rename_object(new_obj, original_name)
    print(f'{obj} converted to type {target_type}')
    return True


# 将选中对象复制到目标对象下
def copy_from_selection(obj: dict):
    selections = WAAPI.get_selected_objects()
    if len(selections) == 0:
        return False
    for selection in selections:
        WAAPI.copy_object(selection, obj)
    return True


# 将对象移动到选中对象下
def move_to_selection(obj: dict):
    selections = WAAPI.get_selected_objects()
    if len(selections) == 0:
        return False
    WAAPI.move_object(obj, selections[0])

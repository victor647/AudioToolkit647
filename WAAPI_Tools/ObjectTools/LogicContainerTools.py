import re
from Libraries import WAAPI, ProjectConventions
from ObjectTools import MixingTools


# 打破Container并将内容移出
def break_container(container: dict):
    children = WAAPI.get_child_objects(container)
    parent = WAAPI.get_parent_object(container)
    for child in children:
        WAAPI.move_object(child, parent)
    return WAAPI.delete_object(container)


# 替换父级对象并分配Switch Container
def replace_parent(obj: dict):
    parent = WAAPI.get_parent_object(obj)
    grand_parent = WAAPI.get_parent_object(parent)
    WAAPI.move_object(obj, grand_parent)
    if grand_parent['type'] == 'SwitchContainer':
        mappings = WAAPI.get_switch_mappings(grand_parent)
        for mapping in mappings:
            if mapping['child'] == parent['id']:
                WAAPI.assign_switch_mapping(obj, mapping['stateOrSwitch'])
    if WAAPI.delete_object(parent):
        return WAAPI.rename_object(obj, parent['name'])
    return False


# region SwitchContainer
# 根据名称为Switch Container的下级自动分配
def auto_assign_switch_mappings(container: dict):
    if 'SwitchContainer' not in container['type']:
        return False
    # 获取Switch Group中所有可能值
    switch_objects = get_available_switch_items(container)
    if len(switch_objects) == 0:
        return False

    # 找到Switch Container里面的所有子对象
    switch_container_children = WAAPI.get_child_objects(container)
    assigned = False
    for child in switch_container_children:
        for switch_obj in switch_objects:
            # 两者名字任一包括即符合
            switch_name = switch_obj['name']
            child_name = child['name']
            if switch_name in child_name or child_name in switch_name:
                assigned |= WAAPI.assign_switch_mapping(child, switch_obj)
    return assigned


# 获取SwitchContainer当前分配的Switch下面所有的选项
def get_available_switch_items(container: dict):
    if 'SwitchContainer' not in container['type']:
        return []
    group = WAAPI.get_object_property(container, 'SwitchGroupOrStateGroup')
    if group:
        children = WAAPI.get_child_objects(group)
        return children
    return []


# 设置为通用路径分配的对象
def assign_to_generic_path(obj: dict):
    parent = WAAPI.get_parent_object(obj)
    switch_items = get_available_switch_items(parent)
    if len(switch_items) == 0:
        return False

    mappings = WAAPI.get_switch_mappings(parent)
    assigned = False
    for item in switch_items:
        found = False
        for mapping in mappings:
            if item['id'] == mapping['stateOrSwitch']:
                found = True
                break
        if not found:
            assigned |= WAAPI.assign_switch_mapping(obj, item)
    return assigned


# 将一个对象根据自己，队友(可选)和敌人拆分成子对象
def split_by_net_role(obj: dict, has_teammate: bool, has_enemy: bool):
    # Actor Mixer和Virtual Folder无法被放在SwitchContainer下面
    if obj['type'] == 'ActorMixer' or obj['type'] == 'Folder':
        return False
    if not has_teammate and not has_enemy:
        return False
    original_name = obj['name']
    suffix_1p = ProjectConventions.get_net_role_suffix('1P')
    suffix_2p = ProjectConventions.get_net_role_suffix('2P')
    suffix_3p = ProjectConventions.get_net_role_suffix('3P')
    obj_teammate = obj_enemy = None
    # 拆分结构并重组到SwitchContainer下面
    old_parent = WAAPI.get_parent_object(obj)
    new_parent = WAAPI.create_child_object(original_name + '_Temp', 'SwitchContainer', old_parent, 'rename')
    WAAPI.move_object(obj, new_parent)
    WAAPI.rename_object(obj, original_name + suffix_1p)
    if has_teammate:
        obj_teammate = WAAPI.copy_object(obj, new_parent)
        WAAPI.rename_object(obj_teammate, original_name + suffix_2p)
    if has_enemy:
        obj_enemy = WAAPI.copy_object(obj, new_parent)
        WAAPI.rename_object(obj_enemy, original_name + suffix_3p)
    WAAPI.rename_object(new_parent, original_name)
    # 创建并分配bus
    original_bus = WAAPI.get_object_property(obj, 'OutputBus')
    original_bus = WAAPI.get_full_info_from_obj_id(original_bus['id'])
    original_bus_name = original_bus['name']
    if original_bus_name != 'Master Audio Bus':
        bus_self = MixingTools.get_or_create_bus(original_bus_name + suffix_1p, original_bus)
        bus_teammate = MixingTools.get_or_create_bus(original_bus_name + suffix_2p, original_bus) if has_teammate else None
        bus_enemy = MixingTools.get_or_create_bus(original_bus_name + suffix_3p, original_bus)
        MixingTools.set_output_bus(obj, bus_self)
        if has_teammate:
            MixingTools.set_output_bus(obj_teammate, bus_teammate)
        if has_enemy:
            MixingTools.set_output_bus(obj_enemy, bus_enemy)
    # 为1P和3P对象设置空间开关
    MixingTools.set_sound_3d(obj, False)
    if has_teammate:
        MixingTools.set_sound_3d(obj_teammate, True)
    if has_enemy:
        MixingTools.set_sound_3d(obj_enemy, True)
    role_switch_group = WAAPI.find_object_by_name_and_type(ProjectConventions.get_net_role_switch_group(), 'SwitchGroup')
    if role_switch_group is None:
        return False
    # 为SwitchContainer分配SwitchGroup
    WAAPI.set_object_reference(new_parent, 'SwitchGroupOrStateGroup', role_switch_group)
    for switch_value in WAAPI.get_child_objects(role_switch_group):
        switch_name = switch_value['name']
        if switch_name == ProjectConventions.get_net_role_switch_name('1P'):
            WAAPI.assign_switch_mapping(obj, switch_value)
        elif has_teammate and switch_name == ProjectConventions.get_net_role_switch_name('2P'):
            WAAPI.assign_switch_mapping(obj_teammate, switch_value)
            # 默认不能是1P
            if not has_enemy:
                WAAPI.set_object_reference(new_parent, 'DefaultSwitchOrState', switch_value)
        elif has_enemy and switch_name == ProjectConventions.get_net_role_switch_name('3P'):
            WAAPI.assign_switch_mapping(obj_enemy, switch_value)
            WAAPI.set_object_reference(new_parent, 'DefaultSwitchOrState', switch_value)
    return True


# 将SwitchContainer的默认值设为3P
def set_default_switch_to_3p(container: dict):
    switches = get_available_switch_items(container)
    switch_name = ProjectConventions.get_net_role_switch_name('3P')
    for switch in switches:
        if switch_name in switch['name']:
            return WAAPI.set_object_property(container, 'DefaultSwitchOrState', switch)
    return False
# endregion SwitchContainer


# region RandomContainer
# 重命名随机容器下的对象为数字
def rename_random_children(container: dict):
    if container['type'] != 'RandomSequenceContainer':
        return False
    children = WAAPI.get_child_objects(container)
    renamed = False
    for i in range(len(children)):
        renamed |= WAAPI.rename_object(children[i], '{:02d}'.format(i+1))
    return renamed


# 将对象根据命名规范自动归类到随机容器
def group_as_random(obj: dict):
    if obj['type'] != 'Sound':
        return False
    obj_name = obj['name']
    pattern = re.search(r'_\d+$', obj_name) or re.search(r'-\d+$', obj_name)
    if pattern is None:
        return False
    parent = WAAPI.get_parent_object(obj)
    if parent['type'] == 'RandomSequenceContainer':
        return False
    parent_name = obj_name.replace(pattern.group(), '')
    parent_container = WAAPI.find_object_by_name_and_type(parent_name, 'RandomSequenceContainer')
    if not parent_container:
        parent_container = WAAPI.create_child_object(parent_name, 'RandomSequenceContainer', parent)
    return WAAPI.move_object(obj, parent_container)
# endregion RandomContainer

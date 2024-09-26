import re
from Libraries import WAAPI, ProjectConventions
from ObjectTools import MixingTools


# 打破Container并将内容移出
def break_container(container: dict):
    children = WAAPI.get_child_objects(container, False)
    parent = WAAPI.get_parent_object(container)
    for child in children:
        WAAPI.move_object(child, parent)
    WAAPI.delete_object(container)


# 替换父级对象并分配Switch Container
def replace_parent(obj: dict):
    parent = WAAPI.get_parent_object(obj)
    grand_parent = WAAPI.get_parent_object(parent)
    WAAPI.move_object(obj, grand_parent)
    if grand_parent['type'] == 'SwitchContainer':
        mappings = get_switch_mappings(grand_parent)
        for mapping in mappings:
            if mapping['child'] == parent['id']:
                assign_switch_mapping(obj, mapping['stateOrSwitch'])
    WAAPI.delete_object(parent)
    WAAPI.rename_object(obj, parent['name'])


# region SwitchContainer
# 根据名称为Switch Container的下级自动分配
def assign_switch_mappings(container: dict):
    if 'SwitchContainer' not in container['type']:
        return False
    # 获取Switch Group中所有可能值
    switch_objects = get_available_switch_items(container)
    if len(switch_objects) == 0:
        return False

    # 找到Switch Container里面的所有子对象
    switch_container_children = WAAPI.get_child_objects(container, False)
    for child in switch_container_children:
        for switch_obj in switch_objects:
            # 两者名字任一包括即符合
            switch_name = switch_obj['name']
            child_name = child['name']
            if switch_name in child_name or child_name in switch_name:
                assign_switch_mapping(child, switch_obj)
    return True


# 获取SwitchContainer当前分配的Switch下面所有的选项
def get_available_switch_items(container: dict):
    if 'SwitchContainer' not in container['type']:
        return []
    group = WAAPI.get_object_property(container, 'SwitchGroupOrStateGroup')
    if group:
        children = WAAPI.get_child_objects(group, False)
        return children
    return []


# 分配SwitchContainer的内容
def assign_switch_mapping(child_obj, switch_obj):
    assign_args = {
        'child': child_obj['id'],
        'stateOrSwitch': switch_obj if isinstance(switch_obj, str) else switch_obj['id']
    }
    WAAPI.Client.call('ak.wwise.core.switchContainer.addAssignment', assign_args)


# 获取SwitchContainer的Mapping
def get_switch_mappings(container: dict):
    if 'SwitchContainer' not in container['type']:
        return []
    assign_args = {
        'id': container['id']
    }
    options = {
        'return': ['id', 'name', 'type', 'path']
    }
    result = WAAPI.Client.call('ak.wwise.core.switchContainer.getAssignments', assign_args, options)
    return result['return'] if result else []


def get_switch_container_child_context(obj: dict):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'options': {
            'return': ['switchContainerChild:context']
        }
    }
    result = WAAPI.Client.call('ak.wwise.core.object.get', get_args)
    context = result['return'][0]['switchContainerChild:context']
    print(context)
    descendants = WAAPI.get_child_objects(context, True)
    print(descendants)
    get_args = {
        'from': {
            'id': [context['id']]
        },
        'options': {
            'return': ['VoicePitch']
        }
    }
    result = WAAPI.Client.call('ak.wwise.core.object.get', get_args)
    print(result)


# 删除Switch Container下面所有的分配
def remove_switch_mappings(obj: dict):
    if 'SwitchContainer' not in obj['type']:
        return False
    get_args = {
        'id': obj['id']
    }
    results = WAAPI.Client.call('ak.wwise.core.switchContainer.getAssignments', get_args)['return']
    for assignment in results:
        WAAPI.Client.call('ak.wwise.core.switchContainer.removeAssignment', assignment)
    return True


def divide_group(obj_group):
    group_structure = {}
    for item in obj_group:
        parts = item['name'].split('-')
        key = '-'.join(parts[:-1])
        if key in group_structure:
            group_structure[key].append(item)
        else:
            group_structure[key] = [item]
    return group_structure


# 设置为通用路径分配的对象
def assign_to_generic_path(obj: dict):
    parent = WAAPI.get_parent_object(obj)
    switch_items = get_available_switch_items(parent)
    if len(switch_items) == 0:
        return

    mappings = get_switch_mappings(parent)
    for item in switch_items:
        found = False
        for mapping in mappings:
            if item['id'] == mapping['stateOrSwitch']:
                found = True
                break
        if not found:
            assign_switch_mapping(obj, item)


# 将一个对象根据自己，队友(可选)和敌人拆分成子对象
def split_by_net_role(obj: dict, has_teammate: bool):
    # Actor Mixer和Virtual Folder无法被放在SwitchContainer下面
    if obj['type'] == 'ActorMixer' or obj['type'] == 'Folder':
        return
    original_name = obj['name']
    suffix_1p = ProjectConventions.get_net_role_suffix('1P')
    suffix_2p = ProjectConventions.get_net_role_suffix('2P')
    suffix_3p = ProjectConventions.get_net_role_suffix('3P')
    # 拆分结构并重组到SwitchContainer下面
    old_parent = WAAPI.get_parent_object(obj)
    new_parent = WAAPI.create_object(original_name + '_Temp', 'SwitchContainer', old_parent, 'rename')
    WAAPI.move_object(obj, new_parent)
    obj_enemy = WAAPI.copy_object(obj, new_parent)
    WAAPI.rename_object(obj, original_name + suffix_1p)
    obj_teammate = WAAPI.copy_object(obj, new_parent) if has_teammate else None
    if has_teammate:
        WAAPI.rename_object(obj_teammate, original_name + suffix_2p)
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
        MixingTools.set_output_bus(obj_enemy, bus_enemy)
    # 为1P和3P对象设置空间开关
    MixingTools.set_sound_3d(obj, False)
    if has_teammate:
        MixingTools.set_sound_3d(obj_teammate, True)
    MixingTools.set_sound_3d(obj_enemy, True)
    role_switch_group = WAAPI.find_object_by_name_and_type(ProjectConventions.get_net_role_switch_group(), 'SwitchGroup')
    if role_switch_group is None:
        return
    # 为SwitchContainer分配SwitchGroup
    WAAPI.set_object_reference(new_parent, 'SwitchGroupOrStateGroup', role_switch_group)
    for switch_value in WAAPI.get_child_objects(role_switch_group, False):
        switch_name = switch_value['name']
        if switch_name == ProjectConventions.get_net_role_switch_name('1P'):
            assign_switch_mapping(obj, switch_value)
        elif has_teammate and switch_name == ProjectConventions.get_net_role_switch_name('2P'):
            assign_switch_mapping(obj_teammate, switch_value)
        elif switch_name == ProjectConventions.get_net_role_switch_name('3P'):
            assign_switch_mapping(obj_enemy, switch_value)
            WAAPI.set_object_reference(new_parent, 'DefaultSwitchOrState', switch_value)


# 将SwitchContainer的默认值设为3P
def set_default_switch_to_3p(container: dict):
    switches = get_available_switch_items(container)
    for switch in switches:
        if '3P' in switch['name']:
            return WAAPI.set_object_property(container, 'DefaultSwitchOrState', switch)
    return False
# endregion SwitchContainer


# region RandomContainer
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
        parent_container = WAAPI.create_object(parent_name, 'RandomSequenceContainer', parent)
    WAAPI.move_object(obj, parent_container)
# endregion RandomContainer

from Libraries import WaapiTools


# 打破Container并将内容移出
def break_container(obj):
    children = WaapiTools.get_children_objects(obj, False)
    parent = WaapiTools.get_parent_objects(obj, False)
    for child in children:
        WaapiTools.move_object(child, parent)
    WaapiTools.delete_object(obj)


# 替换父级对象并分配Switch Container
def replace_parent(obj):
    parent = WaapiTools.get_parent_objects(obj, False)
    grand_parent = WaapiTools.get_parent_objects(parent, False)
    WaapiTools.move_object(obj, grand_parent)
    if grand_parent['type'] == 'SwitchContainer':
        mappings = get_switch_mapping(grand_parent)
        for mapping in mappings:
            if mapping['child'] == parent['id']:
                assign_switch_mapping(obj, mapping['stateOrSwitch'])
    WaapiTools.delete_object(parent)
    WaapiTools.rename_object(obj, parent['name'])


# 根据名称为Switch Container的下级自动分配
def auto_assign_switch_mappings(obj):
    # 获取Switch Group中所有可能值
    switch_objects = get_available_switch_items(obj)
    if switch_objects is None:
        return

    # 找到Switch Container里面的所有子对象
    switch_container_children = WaapiTools.get_children_objects(obj, False)
    for child in switch_container_children:
        for switch_obj in switch_objects:
            # 两者名字任一包括即符合
            switch_name = switch_obj['name']
            child_name = child['name']
            if switch_name in child_name or child_name in switch_name:
                assign_switch_mapping(child, switch_obj)


# 获取SwitchContainer当前分配的Switch下面所有的选项
def get_available_switch_items(obj):
    if obj['type'] != 'SwitchContainer' and obj['type'] != 'MusicSwitchContainer':
        return None

    # 获取分配的Switch Group
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'options': {
            'return': ['@SwitchGroupOrStateGroup']
        }
    }
    switch_group_objects = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)['return']
    if len(switch_group_objects) == 0:
        return None

    switch_group_obj = switch_group_objects[0]['@SwitchGroupOrStateGroup']
    return WaapiTools.get_children_objects(switch_group_obj, False)


# 分配SwitchContainer的内容
def assign_switch_mapping(child_obj, switch_obj):
    assign_args = {
        'child': child_obj['id'],
        'stateOrSwitch': switch_obj if isinstance(switch_obj, str) else switch_obj['id']
    }
    WaapiTools.Client.call('ak.wwise.core.switchContainer.addAssignment', assign_args)


# 获取SwitchContainer的Mapping
def get_switch_mapping(obj):
    assign_args = {
        'id': obj['id']
    }
    options = {
        'return': ['id', 'name', 'type', 'path']
    }
    result = WaapiTools.Client.call('ak.wwise.core.switchContainer.getAssignments', assign_args, options)
    return result if result is None else result['return']


def get_switch_container_child_context(obj):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'options': {
            'return': ['switchContainerChild:context']
        }
    }
    result = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)
    context = result['return'][0]['switchContainerChild:context']
    print(context)
    descendants = WaapiTools.get_children_objects(context, True)
    print(descendants)
    get_args = {
        'from': {
            'id': [context['id']]
        },
        'options': {
            'return': ['@VoicePitch']
        }
    }
    result = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)
    print(result)


# 删除Switch Container下面所有的分配
def remove_all_switch_assignments(obj):
    if obj['type'] != 'SwitchContainer' and obj['type'] != 'MusicSwitchContainer':
        return
    get_args = {
        'id': obj['id']
    }
    results = WaapiTools.Client.call('ak.wwise.core.switchContainer.getAssignments', get_args)['return']
    for assignment in results:
        WaapiTools.Client.call('ak.wwise.core.switchContainer.removeAssignment', assignment)


# 设置为通用路径分配的对象
def set_as_generic_path_obj(obj):
    parent = WaapiTools.get_parent_objects(obj, False)
    switch_items = get_available_switch_items(parent)
    if switch_items is None:
        return

    mappings = get_switch_mapping(parent)
    for item in switch_items:
        found = False
        for mapping in mappings:
            if item['id'] == mapping['stateOrSwitch']:
                found = True
                break
        if not found:
            assign_switch_mapping(obj, item)


# 将音量音高滤波器等设置应用到下一层
def apply_fader_edits_downstream(obj):
    volume_bias = WaapiTools.get_object_property(obj, '@Volume')
    pitch_bias = WaapiTools.get_object_property(obj, '@Pitch')
    low_pass_bias = WaapiTools.get_object_property(obj, '@Lowpass')
    high_pass_bias = WaapiTools.get_object_property(obj, '@Highpass')
    WaapiTools.set_object_property(obj, 'Volume', 0)
    WaapiTools.set_object_property(obj, 'Pitch', 0)
    WaapiTools.set_object_property(obj, 'Lowpass', 0)
    WaapiTools.set_object_property(obj, 'Highpass', 0)
    children = WaapiTools.get_children_objects(obj, False)
    for child in children:
        volume_base = WaapiTools.get_object_property(child, '@Volume')
        pitch_base = WaapiTools.get_object_property(child, '@Pitch')
        low_pass_base = WaapiTools.get_object_property(child, '@Lowpass')
        high_pass_base = WaapiTools.get_object_property(child, '@Highpass')
        WaapiTools.set_object_property(child, 'Volume', volume_base + volume_bias)
        WaapiTools.set_object_property(child, 'Pitch', pitch_base + pitch_bias)
        WaapiTools.set_object_property(child, 'Lowpass', low_pass_base + low_pass_bias)
        WaapiTools.set_object_property(child, 'Highpass', high_pass_base + high_pass_bias)
        # 递归应用编辑
        if child['type'] != 'Sound':
            apply_fader_edits_downstream(child)


# 将一个对象根据1P2P3P拆分成子对象
def split_by_net_role(obj):
    # Actor Mixer和Virtual Folder无法被放在SwitchContainer下面
    if obj['type'] == 'ActorMixer' or obj['type'] == 'Folder':
        return
    original_name = obj['name']
    # 拆分结构并重组到SwitchContainer下面
    old_parent = WaapiTools.get_parent_objects(obj, False)
    new_parent = WaapiTools.create_object(original_name + '_Temp', 'SwitchContainer', old_parent, 'rename')
    WaapiTools.move_object(obj, new_parent)
    obj_p3 = WaapiTools.copy_object(obj, new_parent)
    WaapiTools.rename_object(obj, original_name + '_P1')
    WaapiTools.rename_object(obj_p3, original_name + '_P3')
    WaapiTools.rename_object(new_parent, original_name)
    # 分配bus
    original_bus = WaapiTools.get_object_property(obj, '@OutputBus')
    original_bus_name = original_bus['name']
    bus_p1 = WaapiTools.find_object_by_name(original_bus_name + '_P1', 'Bus')
    if bus_p1 is None:
        bus_p1 = WaapiTools.create_object(original_bus_name + '_P1', 'Bus', original_bus, 'replace')

    bus_p3 = WaapiTools.find_object_by_name(original_bus_name + '_P3', 'Bus')
    if bus_p3 is None:
        bus_p3 = WaapiTools.create_object(original_bus_name + '_P3', 'Bus', original_bus, 'replace')
    WaapiTools.set_object_property(obj, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj, 'OutputBus', bus_p1)
    WaapiTools.set_object_property(obj_p3, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj_p3, 'OutputBus', bus_p3)
    net_role_switch_group = WaapiTools.find_object_by_name('Net_Role', 'SwitchGroup')
    if net_role_switch_group is None:
        return
    WaapiTools.set_object_reference(new_parent, 'SwitchGroupOrStateGroup', net_role_switch_group)
    for switch_obj in WaapiTools.get_children_objects(net_role_switch_group, False):
        if '1P' in switch_obj['name']:
            assign_switch_mapping(obj, switch_obj)
        if '3P' in switch_obj['name']:
            assign_switch_mapping(obj_p3, switch_obj)
            WaapiTools.set_object_reference(new_parent, 'DefaultSwitchOrState', switch_obj)
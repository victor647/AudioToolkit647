from Libraries import WaapiTools


# 打破Container并将内容移出
def break_container(obj):
    children = WaapiTools.get_children_objects(obj, False)
    parent = WaapiTools.get_parent_objects(obj, False)
    for child in children:
        WaapiTools.move_object(child, parent)
    WaapiTools.delete_object(obj)


# 根据名称为Switch Container的下级自动分配
def auto_assign_switch_mappings(obj):
    if obj['type'] != 'SwitchContainer' and obj['type'] != 'MusicSwitchContainer':
        return

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
        return

    switch_group_obj = switch_group_objects[0]['@SwitchGroupOrStateGroup']
    # 获取Switch Group中所有可能值
    switch_objects = WaapiTools.get_children_objects(switch_group_obj, False)

    # 找到Switch Container里面的所有子对象
    switch_container_children = WaapiTools.get_children_objects(obj, False)
    for child in switch_container_children:
        for switch_obj in switch_objects:
            # 两者名字任一包括即符合
            switch_name = switch_obj['name']
            child_name = child['name']
            if switch_name in child_name or child_name in switch_name:
                assign_switch_mapping(child, switch_obj)


# 分配SwitchContainer的内容
def assign_switch_mapping(child_obj, switch_obj):
    assign_args = {
        'child': child_obj['id'],
        'stateOrSwitch': switch_obj['id']
    }
    WaapiTools.Client.call('ak.wwise.core.switchContainer.addAssignment', assign_args)


# 获取SwitchContainer的Mapping
def get_switch_mapping(child_obj, switch_obj):
    assign_args = {
        'id': child_obj['id']
    }
    result = WaapiTools.Client.call('ak.wwise.core.switchContainer.getAssignments', assign_args)
    return result if result is None else result['return']


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
    obj_2p = WaapiTools.copy_object(obj, new_parent)
    obj_3p = WaapiTools.copy_object(obj, new_parent)
    WaapiTools.rename_object(obj, original_name + '_1P')
    WaapiTools.rename_object(obj_2p, original_name + '_2P')
    WaapiTools.rename_object(obj_3p, original_name + '_3P')
    WaapiTools.rename_object(new_parent, original_name)
    # 分配bus
    original_bus = WaapiTools.get_object_property(obj, '@OutputBus')
    original_bus_name = original_bus['name']
    bus_1p = WaapiTools.find_object_by_name(original_bus_name + '_1P', 'Bus')
    if bus_1p is None:
        bus_1p = WaapiTools.create_object(original_bus_name + '_1P', 'Bus', original_bus, 'replace')
    bus_2p = WaapiTools.find_object_by_name(original_bus_name + '_2P', 'Bus')
    if bus_2p is None:
        bus_2p = WaapiTools.create_object(original_bus_name + '_2P', 'Bus', original_bus, 'replace')
    bus_3p = WaapiTools.find_object_by_name(original_bus_name + '_3P', 'Bus')
    if bus_3p is None:
        bus_3p = WaapiTools.create_object(original_bus_name + '_3P', 'Bus', original_bus, 'replace')
    WaapiTools.set_object_property(obj, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj, 'OutputBus', bus_1p)
    WaapiTools.set_object_property(obj_2p, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj_2p, 'OutputBus', bus_2p)
    WaapiTools.set_object_property(obj_3p, 'OverrideOutput', True)
    WaapiTools.set_object_reference(obj_3p, 'OutputBus', bus_3p)
    net_role_switch_group = WaapiTools.find_object_by_name('Net_Role', 'SwitchGroup')
    if net_role_switch_group is None:
        return
    WaapiTools.set_object_reference(new_parent, 'SwitchGroupOrStateGroup', net_role_switch_group)
    for switch_obj in WaapiTools.get_children_objects(net_role_switch_group, False):
        if '1P' in switch_obj['name']:
            assign_switch_mapping(obj, switch_obj)
            WaapiTools.set_object_reference(new_parent, 'DefaultSwitchOrState', switch_obj)
        if '2P' in switch_obj['name']:
            assign_switch_mapping(obj_2p, switch_obj)
        if '3P' in switch_obj['name']:
            assign_switch_mapping(obj_3p, switch_obj)
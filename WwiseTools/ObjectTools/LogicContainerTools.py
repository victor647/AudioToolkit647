from ObjectTools import WaapiTools


# 根据名称为Switch Container的下级自动分配
def assign_switch_mappings(client, obj):
    if obj['type'] != 'SwitchContainer' or obj['type'] != 'MusicSwitchContainer':
        return

    # 获取分配的Switch Group
    get_args = {
        'from': {
            'id': obj['id']
        },
        'options': {
            'return': ['@SwitchGroupOrStateGroup']
        }
    }
    switch_group_objects = client.call('ak.wwise.core.object.get', get_args)['return']
    if switch_group_objects == '{}':
        return

    switch_group_obj = switch_group_objects['@SwitchGroupOrStateGroup']
    # 获取Switch Group中所有可能值
    switch_objects = WaapiTools.get_children_objects(client, switch_group_obj, False)

    # 找到Switch Container里面的所有子对象
    switch_container_children = WaapiTools.get_children_objects(client, obj, False)
    for child in switch_container_children:
        for switch_obj in switch_objects:
            # 若子对象名称中含有Switch名称，则自动分配
            if switch_obj['name'] in child['name']:
                assign_args = {
                    'child': child['id'],
                    'stateOrSwitch': switch_obj['id']
                }
                client.call('ak.wwise.core.switchContainer.addAssignment', assign_args)




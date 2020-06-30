import ScriptingTools


# 根据名称为Switch Container的下级自动分配
def auto_assign_switch(client, objects):
    # 筛选选取对象中所有的SwitchContainer
    switch_containers = ScriptingTools.filter_objects_by_type(objects, "SwitchContainer")
    for switch_container in switch_containers:
        get_args = {
            'from': {
                'id': [switch_container['id']]
            },
            'options': {
                'return': ['@SwitchGroupOrStateGroup']
            }
        }
        # 获取分配的Switch Group
        switch_group_objects = client.call('ak.wwise.core.object.get', get_args)['return']
        if len(switch_group_objects) == 0:
            return

        switch_group_obj = switch_group_objects[0]['@SwitchGroupOrStateGroup']
        # 获取Switch Group中所有可能值
        switch_objects = ScriptingTools.get_child_objects(client, switch_group_obj)

        # 找到Switch Container里面的所有子对象
        switch_container_children = ScriptingTools.get_child_objects(client, switch_container)
        for child in switch_container_children:
            for switch_obj in switch_objects:
                # 若子对象名称中含有Switch名称，则自动分配
                if switch_obj['name'] in child['name']:
                    assign_args = {
                        'child': child['id'],
                        'stateOrSwitch': switch_obj['id']
                    }
                    client.call('ak.wwise.core.switchContainer.addAssignment', assign_args)




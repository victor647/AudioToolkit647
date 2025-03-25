from Libraries import WAAPI


# 清除对象上绑定的RTPC
def clear_rtpc(obj: dict):
    WAAPI.clear_slots(obj, 'RTPC')


# 替换对象上的RTPC
def copy_rtpc(source_obj: dict, target_objects: list):
    WAAPI.paste_object_property(source_obj, target_objects, 'Rtpc')


# 在SwitchGroup或StateGroup中查找或创建对应名称的选项
def find_or_create_switch_value(switch_or_state_group: dict, value_name: str):
    if 'type' not in switch_or_state_group:
        switch_or_state_group = WAAPI.get_full_info_from_obj_id(switch_or_state_group['id'])
    if not switch_or_state_group:
        return None
    existing_values = WAAPI.get_child_objects(switch_or_state_group)
    for value in existing_values:
        if value['name'] == value_name:
            return value
    switch_type = 'Switch' if switch_or_state_group['type'] == 'SwitchGroup' else 'State'
    return WAAPI.create_child_object(value_name, switch_type, switch_or_state_group)

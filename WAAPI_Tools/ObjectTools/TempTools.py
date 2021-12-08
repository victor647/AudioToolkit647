from Libraries import WaapiTools
from ObjectTools import LogicContainerTools


def temp_tool(objects: list):
    for obj in objects:
        parent = WaapiTools.get_parent_objects(obj, False)
        new_obj = WaapiTools.create_object('Tail', 'SwitchContainer', parent, 'rename')
        WaapiTools.move_object(obj, new_obj)
        indoor_switch_group = WaapiTools.find_object_by_name('Indoor_Outdoor', 'SwitchGroup')
        WaapiTools.set_object_reference(new_obj, 'SwitchGroupOrStateGroup', indoor_switch_group)
        outdoor_switch = WaapiTools.get_children_objects(indoor_switch_group, False)[1]
        LogicContainerTools.assign_switch_mapping(obj, outdoor_switch)
        WaapiTools.set_object_reference(new_obj, 'DefaultSwitchOrState', outdoor_switch)

        if parent['type'] == 'SwitchContainer':
            loop_switch_group = WaapiTools.find_object_by_name('Gun_Shot_Loop_Mode', 'SwitchGroup')
            end_switch = WaapiTools.get_children_objects(loop_switch_group, False)[0]
            LogicContainerTools.assign_switch_mapping(new_obj, end_switch)



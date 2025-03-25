import os
from Libraries import WAAPI, ProjectConventions, FileTools, ScriptingHelper
from ObjectTools import CommonTools, AudioSourceTools


# 为每个选中的对象创建一个播放事件
def create_play_event(obj: dict):
    obj_type = obj['type']
    obj_path = obj['path']
    if 'Container' not in obj_type and 'Sound' not in obj_type:
        print(f'{obj_type} [{obj_path}] cannot be an event target.')
        return False

    event_name = get_event_name(obj)
    event = WAAPI.find_object_by_name_and_type(event_name, 'Event')
    # 已有事件，替换播放对象
    if event:
        targets = get_event_targets(event)
        if len(targets) == 0 or targets[0] != obj:
            clear_event_actions(event)
            create_event_action(event, obj, 1)
            print(f'Assigning {obj_type} [{obj_path}] to existing event [{event_name}].')
        else:
            print(f'An existing event [{event_name}] found for target {obj_type} [{obj_path}].')
    # 创建新的事件
    else:
        if '_' in event_name:
            event_path = ProjectConventions.remove_acronym_from_name(event_name.replace('_', '\\'))
            parent_path = os.path.dirname('\\Events\\' + event_path)
            parent = CommonTools.create_folders_for_path(parent_path)
        else:
            parent_path = '\\Events\\Default Work Unit'
            parent = WAAPI.find_object_by_path(parent_path)
        if not parent:
            return False
        event = WAAPI.create_child_object(event_name, 'Event', parent)
        create_event_action(event, obj, 1)
        # End的事件需要停止Start
        if obj['name'] == 'End':
            obj_start = CommonTools.find_parallel_object(obj, 'Start')
            if obj_start:
                action = create_event_action(event, obj_start, 2)
                WAAPI.set_object_property(action, 'FadeTime', 0.5)
    CommonTools.update_notes_and_color(obj)
    return WAAPI.select_objects_in_wwise([event])


# 为事件创建播放动作
def create_event_action(event: dict, target: dict, action_type: int):
    if not event or not target:
        return False
    action = WAAPI.create_child_object(event['name'], 'Action', event)
    WAAPI.set_object_property(action, 'ActionType', action_type)
    set_action_target(action, target)
    return action


# 清除事件中所有的动作
def clear_event_actions(event: dict):
    actions = WAAPI.get_child_objects(event)
    for action in actions:
        WAAPI.delete_object(action)
    return True


# 获取对象对应的事件名称
def get_event_name(obj: dict):
    obj_name = obj['name']
    if obj['type'] == 'Sound' and ProjectConventions.use_full_name_in_sound():
        if '_' in obj_name and AudioSourceTools.get_source_file_path(obj):
            event_name = obj_name
        else:
            event_name = CommonTools.get_full_name_with_acronym(obj)
    elif '_' in obj_name:
        event_name = obj_name
    else:
        event_name = CommonTools.get_full_name_with_acronym(obj)
    if obj['path'].startswith('\\Interactive Music Hierarchy'):
        event_name = 'BGM_' + event_name
    if ProjectConventions.has_event_play_prefix():
        event_name = 'Play_' + event_name
    return event_name


# 获取Event的目标对象
def get_event_targets(event: dict):
    actions = WAAPI.get_child_objects(event)
    if len(actions) == 0:
        print(f"Event [{event['name']}] has no actions!")
        return []
    targets = []
    for action in actions:
        target = WAAPI.get_object_property(action, 'Target')
        if not target:
            print(f"Event [{event['name']}] has an action with no target!")
            continue
        if 'name' not in target:
            print(f"Event [{event['name']}] has an action with missing target!")
            continue
        target = WAAPI.get_full_info_from_obj_id(target['id'])
        targets.append(target)
    return targets


# 改变Action的目标对象
def set_action_target(action: dict, target: dict):
    return WAAPI.set_object_reference(action, 'Target', target)


# 根据播放对象重命名事件
def rename_event_by_target(event: dict):
    if event['type'] != 'Event':
        return False
    targets = get_event_targets(event)
    if len(targets) == 1:
        full_name = get_event_name(targets[0])
        WAAPI.rename_object(event, full_name)
        CommonTools.update_notes_and_color(event)
        return True
    return False


# 对象是否被某个事件所引用
def has_event_reference(obj):
    references = WAAPI.get_references_to_object(obj)
    for reference in references:
        if reference['type'] == 'Action':
            return True
    return False


# 导出全部事件及其播放内容
def export_all_events():
    data = []
    all_events = WAAPI.find_all_objects_by_type('Event')
    for event in all_events:
        targets = get_event_targets(event)
        event_data = [event['name']]
        for target in targets:
            event_data.append(target['path'])
        data.append(event_data)
    FileTools.export_to_csv(data, 'All_Events')
    ScriptingHelper.show_message_box('导出完成', f'共导出{len(data)}条事件')

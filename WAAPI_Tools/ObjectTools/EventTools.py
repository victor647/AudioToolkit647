import os
from Libraries import WAAPI, ProjectConventions
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
            parent = WAAPI.get_object_from_path(parent_path)
        event = WAAPI.create_object(event_name, 'Event', parent)
        create_event_action(event, obj, 1)
    CommonTools.update_notes_and_color(obj)
    WAAPI.select_objects_in_wwise([event])
    return True


# 为事件创建播放动作
def create_event_action(event: dict, target: dict, action_type: int):
    if not event or not target:
        return False
    action = WAAPI.create_object(event['name'], 'Action', event)
    WAAPI.set_object_property(action, 'ActionType', action_type)
    return set_action_target(action, target)


# 清除事件中所有的动作
def clear_event_actions(event: dict):
    actions = WAAPI.get_child_objects(event, False)
    for action in actions:
        WAAPI.delete_object(action)


# 获取对象对应的事件名称
def get_event_name(obj: dict):
    if obj['type'] == 'Sound' and AudioSourceTools.get_source_file_path(obj):
        return obj['name']
    return CommonTools.get_full_name_with_acronym(obj)


# 获取Event的目标对象
def get_event_targets(event: dict):
    actions = WAAPI.get_child_objects(event, False)
    if len(actions) == 0:
        print(f"Event [{event['name']}] has no actions!")
        return []
    targets = []
    for action in actions:
        info = get_action_info(action)
        target = info['Target']
        if not target:
            print(f"Event [{event['name']}] has an action with no target!")
            continue
        if 'name' not in target:
            print(f"Event [{event['name']}] has an action with missing target!")
            continue
        target = WAAPI.get_full_info_from_obj_id(target['id'])
        targets.append(target)
    return targets


# 获取Action的类型和对象
def get_action_info(action: dict):
    if action['type'] != 'Action':
        return None
    action_id = action['id']
    get_args = {
        'waql': f'from object \"{action_id}\"',
        'options': {
            'return': ['ActionType', 'Target']
        }
    }
    result = WAAPI.Client.call('ak.wwise.core.object.get', get_args)
    return result['return'][0]


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

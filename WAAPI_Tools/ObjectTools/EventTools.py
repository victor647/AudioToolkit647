from Libraries import WaapiTools
from ObjectTools import CommonTools, SoundBankTools


# 为每个选中的对象创建一个播放事件
def create_play_event(obj: dict):
    obj_type = obj['type']
    obj_path = obj['path']
    if 'Container' not in obj_type and 'Sound' not in obj_type:
        print(f'{obj_type} [{obj_path}] cannot be an event target.')
        return
    work_unit = WaapiTools.get_object_from_path('\\Events\\Default Work Unit')
    event_name = CommonTools.get_full_name_with_acronym(obj)
    event = WaapiTools.find_object_by_name_and_type(event_name, 'Event')
    if event:
        target = get_event_target(event)
        if target != obj:
            create_event_action(event, obj, 1)
            print(f'Assigning {obj_type} [{obj_path}] to existing event [{event_name}].')
        else:
            print(f'An existing event [{event_name}] found for target {obj_type} [{obj_path}].')
    else:
        event = WaapiTools.create_object(event_name, 'Event', work_unit, 'fail')
        create_event_action(event, obj, 1)
    CommonTools.update_notes_and_color(obj)


# 为事件创建播放动作
def create_event_action(event: dict, target: dict, action_type: int):
    create_args = {
        'name': event['name'],
        'parent': event['id'],
        'type': 'Action',
    }
    options = {
        'return': ['id', 'name', 'type', 'path']
    }
    action = WaapiTools.Client.call('ak.wwise.core.object.create', create_args, options)
    # 设置播放操作
    set_args = {
        'object': action['id'],
        'property': 'ActionType',
        'value': action_type
    }
    WaapiTools.Client.call('ak.wwise.core.object.setProperty', set_args)
    set_action_target(action, target)


# 获取Event的目标对象
def get_event_target(event: dict):
    actions = WaapiTools.get_child_objects(event, False)
    for action in actions:
        info = get_action_info(action)
        target = info['Target']
        if not target:
            print(f"Event [{event['name']}] has an action with no target!")
            return None
        if 'name' not in target:
            print(f"Event [{event['name']}] has an action with missing target!")
            return None
        target['type'] = WaapiTools.get_object_property(target, 'type')
        target['path'] = WaapiTools.get_object_property(target, 'path')
        return target
    return None


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
    result = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)
    return result['return'][0]


# 改变Action的目标对象
def set_action_target(action: dict, target: dict):
    return WaapiTools.set_object_reference(action, 'Target', target)


# 检查Event命名是否与目标一致
def naming_mismatches_target(event: dict):
    event_name = event['name']
    actions = WaapiTools.get_child_objects(event, False)
    # 仅处理Event包含单个Action的情况
    if len(actions) > 1:
        return False
    target = get_event_target(event)
    if not target:
        return True
    if 'Bus' in target['type']:
        return False
    full_name = CommonTools.get_full_name_with_acronym(target)
    return full_name != event_name


# 根据播放对象重命名事件
def rename_by_target(event: dict):
    if event['type'] != 'Event':
        return False
    target = get_event_target(event)
    if target:
        full_name = CommonTools.get_full_name_with_acronym(target)
        WaapiTools.rename_object(event, full_name)
        CommonTools.update_notes_and_color(event)
        return True
    return False


# 检查是否存在不必要的Event
def is_event_unnecessary(event: dict):
    event_name = event['name']
    return event_name.endswith('_1P') or event_name.endswith('_3P')


# 检查声音是否被事件所引用
def is_sound_not_in_event(obj: dict):
    references = WaapiTools.get_references_to_object(obj)
    if len(references) == 0:
        parent = WaapiTools.get_parent_objects(obj, False)
        if parent['type'] == 'ActorMixer' or parent['type'] == 'WorkUnit':
            return True
        return is_sound_not_in_event(parent)
    return False


# 检查事件是否被Bank所引用
def is_event_not_in_bank(event: dict):
    parent = WaapiTools.get_parent_objects(event, False)
    if not parent:
        return True
    references = WaapiTools.get_references_to_object(parent)
    for reference in references:
        if reference['type'] == 'SoundBank':
            return False
    return is_event_not_in_bank(parent)


# 生成所有Event与Bank的对应关系
def generate_event_bank_map():
    event_bank_map = {}
    all_banks = WaapiTools.find_all_objects_by_type('SoundBank')
    for bank in all_banks:
        inclusions = SoundBankTools.get_bank_inclusions(bank)
        for inclusion in inclusions:
            obj_id = inclusion['object']
            obj = WaapiTools.get_full_info_from_obj_id(obj_id)
            if obj['path'].startswith('\\Events\\'):
                descendants = WaapiTools.get_descendants_by_type(obj, 'Event')
                for event in descendants:
                    event_bank_map[event['name']] = bank['name']
    return event_bank_map

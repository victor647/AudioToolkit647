from Libraries import WaapiTools


# 为每个选中的对象创建一个播放事件
def create_play_event(obj):
    work_unit = WaapiTools.get_object_from_path('\\Events\\Default Work Unit')
    new_event = WaapiTools.create_object(obj['name'], 'Event', work_unit, 'rename')
    create_event_action(new_event, obj, 1)


# 为事件创建播放动作
def create_event_action(event_obj, target_obj, action_type: int):
    create_args = {
        'name': event_obj['name'],
        'parent': event_obj['id'],
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
    change_action_target(action, target_obj)


# 改变Action的目标对象
def change_action_target(action_obj, target_obj):
    set_args = {
        'object': action_obj['id'],
        'reference': 'Target',
        'value': target_obj['id']
    }
    WaapiTools.Client.call('ak.wwise.core.object.setReference', set_args)

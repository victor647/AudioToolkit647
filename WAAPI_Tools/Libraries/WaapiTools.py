from waapi import WaapiRequestFailed
import os.path
from ObjectTools.LogicContainerTools import get_switch_mapping, assign_switch_mapping

Client = None


# 获取项目工程路径
def get_project_directory():
    get_args = {
        'from': {
            'ofType': ['Project']
        },
        'options': {
            'return': ['filePath']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'][0]['filePath']


# 获取项目默认语言
def get_default_language():
    get_args = {
        'from': {
            'ofType': ['Project']
        },
        'options': {
            'return': ['DefaultLanguage']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'][0]['DefaultLanguage']


# 获取所有的语言
def get_language_list():
    args = {
        'from': {
            'ofType': ['Language']
        }
    }
    options = {
        'return': ['name']
    }
    result = Client.call('ak.wwise.core.object.get', args, options)
    return result['return']


# 开始记录操作
def begin_undo_group(action: str):
    Client.call('ak.wwise.core.undo.beginGroup')
    print(f'Begin Action [{action}]')


# 结束记录操作
def end_undo_group(action: str):
    end_args = {
        'displayName': 'WAAPI Tool - ' + action
    }
    Client.call('ak.wwise.core.undo.endGroup', end_args)
    print(f'End Action [{action}]')


# 撤销操作
def undo():
    execute_args = {
        'command': 'Undo'
    }
    Client.call('ak.wwise.ui.commands.execute', execute_args)


# 重做操作
def redo():
    execute_args = {
        'command': 'Redo'
    }
    Client.call('ak.wwise.ui.commands.execute', execute_args)


# 获取选中的对象列表
def get_selected_objects():
    get_args = {
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.ui.getSelectedObjects', get_args)
    return result['objects'] if result else []


# 获取一个对象所有的引用
def get_references_to_object(obj: dict):
    obj_id = obj['id']
    get_args = {
        'waql': f'from object \"{obj_id}\" select referencesTo',
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'] if result else []


# 获取一个对象递归上层的所有母对象
def get_parent_objects(obj, include_ancestors: bool):
    obj_id = obj['id']
    parent_type = 'ancestors' if include_ancestors else 'parent'
    get_args = {
        'waql': f'from object \"{obj_id}\" select {parent_type}',
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    parents = result['return']
    if len(parents) == 0:
        return None
    return parents if include_ancestors else parents[0]


# 获取一个对象递归下层的所有子对象
def get_child_objects(obj, include_descendants: bool):
    children = []
    index = 0
    interval = 500
    while True:
        get_args = {
            'from': {
                'id': [obj['id']]
            },
            'transform': [
                {'select': ['descendants' if include_descendants else 'children']},
                {'range': [index * interval, interval]}
            ],
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        cur_range_result = Client.call('ak.wwise.core.object.get', get_args)
        if cur_range_result and len(cur_range_result['return']) > 0:
            children += cur_range_result['return']
            index += 1
        else:
            break
    return children


# 获取特定类型的全部子对象
def get_descendants_by_type(obj, type_name):
    parent_obj = obj
    descendants = get_child_objects(parent_obj, True)
    return [obj for obj in descendants if obj['type'] == type_name]


# 获取整个Wwise工程所有对象
def get_global_objects():
    global_objects = []
    objects_type = {'WorkUnit', 'Folder', 'ActorMixer', 'SwitchContainer', 'BlendContainer', 'RandomSequenceContainer',
                    'Sound', 'Event', 'AuxBus', 'Bus', 'SoundBank', 'StateGroup', 'SwitchGroup', 'GameParameter',
                    'MusicSwitchContainer', 'MusicPlaylistContainer', 'MusicSegment', 'MusicTrack'}
    for obj_type in objects_type:
        results = find_all_objects_by_type(obj_type)
        global_objects += results
    return global_objects


# 从Sound层级获取包含的AudioSource
def get_audio_source_from_sound(sound_obj):
    get_args = {
        'from': {
            'id': [sound_obj['id']]
        },
        'transform': [
            {'select': ['children']},
        ],
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)['return']
    if len(result) > 0:
        return result[0]
    return None


# 通过guid获取对象完整信息
def get_full_info_from_obj_id(obj_id):
    get_args = {
        'from': {
            'id': [obj_id]
        },
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return_obj = Client.call('ak.wwise.core.object.get', get_args)
    if return_obj is None or len(return_obj['return']) == 0:
        return None
    return return_obj['return'][0]


# 从路径获取对象
def get_object_from_path(path: str):
    get_args = {
        'from': {
            'path': [path]
        },
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return_obj = Client.call('ak.wwise.core.object.get', get_args)
    if return_obj is None or len(return_obj['return']) == 0:
        return None
    return return_obj['return'][0]


# 从名称和类型获取对象
def find_object_by_name_and_type(obj_name: str, obj_type: str):
    get_args = {
        'waql': f'from type {obj_type} where name: \"{obj_name}\"',
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return_obj = Client.call('ak.wwise.core.object.get', get_args)
    if return_obj is None or len(return_obj['return']) == 0:
        return None
    # 仅查找名称完全一致的对象
    for obj in return_obj['return']:
        if obj['name'] == obj_name:
            return obj
    return None


# 查找所有符合名称的对象
def find_all_objects_by_name(obj_name: str, exact_match: bool):
    get_args = {
        'waql': f'from search \"{obj_name}\"',
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    if result is None or len(result['return']) == 0:
        return None
    if not exact_match:
        return result['return']
    matching_objects = []
    for return_obj in result['return']:
        if return_obj['name'] == obj_name:
            matching_objects.append(return_obj)
    return matching_objects


# 查找所有特定类型的对象
def find_all_objects_by_type(type_name: str):
    get_args = {
        'waql': f'from type {type_name}',
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'] if result else []


# 在指定路径下创建一个新的对象
def create_object(obj_name: str, obj_type: str, parent_obj: dict, on_name_conflict: str):
    try:
        create_args = {
            'parent': parent_obj['id'],
            'type': obj_type,
            'name': obj_name,
            'onNameConflict': on_name_conflict
        }
        options = {
            'return': ['id', 'name', 'type', 'path']
        }
        result_obj = Client.call('ak.wwise.core.object.create', create_args, options)
        print(f"{obj_type} [{obj_name}] created under [{parent_obj['path']}]")
        return result_obj
    except WaapiRequestFailed:
        return None


# 移动对象到新的路径
def move_object(obj: dict, new_parent: dict):
    move_args = {
        'object': obj['id'],
        'parent': new_parent['id'],
        'onNameConflict': 'replace'
    }
    Client.call('ak.wwise.core.object.move', move_args)


# 复制对象到某个对象下面
def copy_object(obj: dict, parent: dict):
    copy_args = {
        'object': obj['id'],
        'parent': parent['id'],
        'onNameConflict': 'rename'
    }
    options = {
        'return': ['id', 'name', 'type', 'path']
    }
    result = Client.call('ak.wwise.core.object.copy', copy_args, options)
    if result is None:
        print(f'Copy {obj} to {parent} failed!')
    return result


# 将对象转换类型
def convert_to_type(obj: dict, target_type: str):
    # 先在父级创建一个不同名的新对象
    parent = get_parent_objects(obj, False)
    original_name = obj['name']
    new_obj = create_object(original_name + '_Temp', target_type, parent, 'rename')
    # 创建失败，返回
    if new_obj is None:
        return False
    # 将所有子对象移至新对象上
    for child in get_child_objects(obj, False):
        move_object(child, new_obj)
    # 刷新SwitchContainer分配
    if parent['type'] == 'SwitchContainer':
        mappings = get_switch_mapping(parent)
        for mapping in mappings:
            if mapping['child'] == obj['id']:
                assign_switch_mapping(new_obj, mapping['stateOrSwitch'])
    # 删除原对象
    delete_object(obj)
    # 将新对象重命名成原对象名
    rename_object(new_obj, original_name)
    print(f'{obj} converted to type {target_type}')
    return True


# 为对象创建父级
def create_parent(obj: dict, target_type: str):
    # 先在父级创建一个不同名的新对象
    old_parent = get_parent_objects(obj, False)
    original_name = obj['name']
    new_parent = create_object(original_name + '_Temp', target_type, old_parent, 'rename')
    if new_parent is None:
        return
    move_object(obj, new_parent)
    # 将新对象重命名成原对象名
    rename_object(new_parent, original_name)
    print(f'Parent of type {target_type} created for {obj}')
    return new_parent


# 导入新的音频文件
def import_audio_file(wave_path: str, sound_obj: dict, new_sound_name: str, language='SFX'):
    if not os.path.exists(wave_path):
        print(f'File not found at {wave_path}')
        return False
    try:
        import_args = {
            'importOperation': 'createNew',
            'default': {
                'objectType': 'Sound',
                'importLanguage': language
            },
            'imports': [
                {
                    'audioFile': wave_path,
                    'importLocation': sound_obj['id'],
                    'objectPath': '<Sound>' + new_sound_name
                },
            ]
        }
        Client.call('ak.wwise.core.audio.import', import_args)
        return True
    except WaapiRequestFailed:
        return False


# 执行Wwise操作
def execute_ui_command(objects: list, command: str):
    try:
        if len(objects) == 0:
            return
        obj_ids = [obj['id'] for obj in objects]
        execute_args = {
            'command': command,
            'objects': obj_ids
        }
        Client.call('ak.wwise.ui.commands.execute', execute_args)
        return True
    except WaapiRequestFailed:
        return False


# 在Wwise里选中对象
def open_item_in_wwise_by_path(path: str):
    try:
        select_args = {
            'command': 'FindInProjectExplorerSyncGroup1',
            'objects': [path]
        }
        Client.call('ak.wwise.ui.commands.execute', select_args)
        select_args = {
            'command': 'Inspect',
            'objects': [path]
        }
        Client.call('ak.wwise.ui.commands.execute', select_args)
        return True
    except WaapiRequestFailed:
        return False


# 给一个对象重命名
def rename_object(obj: dict, new_name: str):
    if new_name == obj['name']:
        return True
    try:
        rename_args = {
            'object': obj['id'],
            'value': new_name
        }
        Client.call('ak.wwise.core.object.setName', rename_args)
        print(f"{obj['type']} [{obj['name']}] renamed to [{new_name}]")
        return True
    except WaapiRequestFailed:
        return False


# 获取对象的属性
def get_object_property(obj: dict, property_name: str):
    obj_id = obj['id']
    get_args = {
        'waql': f'from object \"{obj_id}\"',
        'options': {
            'return': [property_name]
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    if result is None or len(result['return']) == 0:
        return None
    return_obj = result['return'][0]
    return return_obj[property_name] if property_name in return_obj else None


# 设置对象的属性
def set_object_property(obj: dict, property_name: str, value):
    try:
        set_args = {
            'object': obj['id'],
            'property': property_name,
            'value': value
        }
        Client.call('ak.wwise.core.object.setProperty', set_args)
        return True
    except WaapiRequestFailed:
        return False


# 设置对象的引用
def set_object_reference(obj: dict, reference_type: str, value: dict):
    try:
        set_args = {
            'object': obj['id'],
            'reference': reference_type,
            'value': value['id']
        }
        Client.call('ak.wwise.core.object.setReference', set_args)
        return True
    except WaapiRequestFailed:
        return False


# 为对象设置备注
def set_object_notes(obj: dict, notes: str):
    try:
        set_args = {
            "object": obj['id'],
            "value": notes
        }
        Client.call('ak.wwise.core.object.setNotes', set_args)
        return True
    except WaapiRequestFailed:
        return False


# 删除一个对象
def delete_object(obj: dict):
    try:
        delete_args = {
            'object': obj['id'],
        }
        Client.call('ak.wwise.core.object.delete', delete_args)
        return True
    except WaapiRequestFailed:
        return False


# 将文件添加到版本控制
def add_to_source_control(file_path: str):
    try:
        add_args = {
            'files': file_path,
        }
        Client.call('ak.wwise.core.sourceControl.add', add_args)
        return True
    except WaapiRequestFailed:
        return False

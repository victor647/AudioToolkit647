from Libraries import LogTool
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
            'return': ['@DefaultLanguage']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'][0]['@DefaultLanguage']


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
def begin_undo_group():
    Client.call('ak.wwise.core.undo.beginGroup')


# 结束记录操作
def end_undo_group():
    end_args = {
        'displayName': 'WAAPI'
    }
    Client.call('ak.wwise.core.undo.endGroup', end_args)


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
    return result['objects'] if result is not None else []


# 获取一个对象递归上层的所有母对象
def get_parent_objects(obj, include_ancestors: bool):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'transform': [
            {'select': ['ancestors' if include_ancestors else 'parent']},
        ],
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    parents = result['return'] if result is not None else []
    if not include_ancestors and len(parents) > 0:
        return parents[0]
    return parents


# 获取一个对象递归下层的所有子对象
def get_children_objects(obj, include_descendants: bool):
    result_obj = []
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
        if cur_range_result is not None and len(cur_range_result['return']):
            result_obj += cur_range_result['return']
            index += 1
        else:
            break

    return result_obj


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
def find_object_by_name(obj_name: str, obj_type: str):
    get_args = {
        'from': {
            'search': [obj_name]
        },
        'transform': [
            {
                'where': [
                    'type:isIn',
                    [obj_type]
                ]
            }
        ],
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return_obj = Client.call('ak.wwise.core.object.get', get_args)
    if return_obj is None or len(return_obj['return']) == 0:
        return None
    # Exact match only
    for obj in return_obj['return']:
        if obj['name'] == obj_name:
            return obj
    return None


# 获取音频源文件路径
def get_original_wave_path(obj):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'options': {
            'return': ['sound:originalWavFilePath']
        }
    }
    return_obj = Client.call('ak.wwise.core.object.get', get_args)
    if return_obj is None or len(return_obj['return']) == 0:
        return ''
    return_obj = return_obj['return'][0]
    return return_obj['sound:originalWavFilePath'] if 'sound:originalWavFilePath' in return_obj else ''


# 获取音频源文件语言
def get_sound_language(obj):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'options': {
            'return': ['audioSource:language']
        }
    }
    return_obj = Client.call('ak.wwise.core.object.get', get_args)
    if return_obj is None or len(return_obj['return']) == 0:
        return ''
    return_obj = return_obj['return'][0]
    return return_obj['audioSource:language']['name'] if 'audioSource:language' in return_obj else ''


# 在指定路径下创建一个新的对象
def create_object(name: str, obj_type: str, parent_obj, on_name_conflict: str):
    create_args = {
        'parent': parent_obj['id'],
        'type': obj_type,
        'name': name,
        'onNameConflict': on_name_conflict
    }
    options = {
        'return': ['id', 'name', 'type', 'path']
    }
    return Client.call('ak.wwise.core.object.create', create_args, options)


# 移动对象到新的路径
def move_object(obj, new_parent):
    move_args = {
        'object': obj['id'],
        'parent': new_parent['id'],
        'onNameConflict': 'replace'
    }
    Client.call('ak.wwise.core.object.move', move_args)


# 复制对象到某个对象下面
def copy_object(obj, parent):
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
        LogTool.safe_log('[Copy Failed] Obj:' + obj['name'] + ' to Parent:' + parent['name'], 'error')
    return result


# 将对象转换类型
def convert_to_type(obj, target_type: str):
    # 先在父级创建一个不同名的新对象
    parent = get_parent_objects(obj, False)
    original_name = obj['name']
    new_obj = create_object(original_name + '_Temp', target_type, parent, 'rename')
    # 创建失败，返回
    if new_obj is None:
        return
    # 将所有子对象移至新对象上
    for child in get_children_objects(obj, False):
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


# 为对象创建父级
def create_parent(obj, target_type: str):
    # 先在父级创建一个不同名的新对象
    old_parent = get_parent_objects(obj, False)
    original_name = obj['name']
    new_parent = create_object(original_name + '_Temp', target_type, old_parent, 'rename')
    if new_parent is None:
        return
    move_object(obj, new_parent)
    # 将新对象重命名成原对象名
    rename_object(new_parent, original_name)


# 导入音频文件
def import_audio_file(wave_path, parent_obj, new_sound_name, language='SFX'):
    import_args = {
        'importOperation': 'createNew',
        'default': {
            'objectType': 'Sound',
            'importLanguage': language
        },
        'imports': [
            {
                'audioFile': wave_path,
                'importLocation': parent_obj['id'],
                'objectPath': '<Sound>' + new_sound_name
            },
        ]
    }
    Client.call('ak.wwise.core.audio.import', import_args)


# 执行Wwise操作
def execute_ui_command(objects, command: str):
    if len(objects) == 0:
        return
    obj_ids = [obj['id'] for obj in objects]
    execute_args = {
        'command': command,
        'objects': obj_ids
    }
    Client.call('ak.wwise.ui.commands.execute', execute_args)


# 在Wwise里选中对象
def open_item_in_wwise_by_path(path):
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


# 给一个对象重命名
def rename_object(obj, new_name: str):
    rename_args = {
        'object': obj['id'],
        'value': new_name
    }
    Client.call('ak.wwise.core.object.setName', rename_args)


# 获取对象的属性
def get_object_property(obj, property_name: str):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'options': {
            'return': [property_name]
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'][0][property_name]


# 设置对象的属性
def set_object_property(obj, property_name: str, value):
    set_args = {
        'object': obj['id'],
        'property': property_name,
        'value': value
    }
    Client.call('ak.wwise.core.object.setProperty', set_args)


# 设置对象的引用
def set_object_reference(obj, reference_type_name: str, value):
    set_args = {
        'object': obj['id'],
        'reference': reference_type_name,
        'value': value['id']
    }
    Client.call('ak.wwise.core.object.setReference', set_args)


# 删除一个对象
def delete_object(obj):
    delete_args = {
        'object': obj['id'],
    }
    Client.call('ak.wwise.core.object.delete', delete_args)

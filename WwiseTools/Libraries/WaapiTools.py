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
    return result['return'] if result is not None else []


# 获取一个对象递归下层的所有子对象
def get_children_objects(obj, include_descendants: bool):
    get_args = {
        'from': {
            'id': [obj['id']]
        },
        'transform': [
            {'select': ['descendants' if include_descendants else 'children']},
        ],
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = Client.call('ak.wwise.core.object.get', get_args)
    return result['return'] if result is not None else []


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
    obj = Client.call('ak.wwise.core.object.get', get_args)
    return obj['return'][0] if obj else {}


# 从名称和类型获取对象
def get_object_from_name_and_type(obj_name: str, obj_type: str):
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
    obj = Client.call('ak.wwise.core.object.get', get_args)
    return obj['return'][0] if obj else {}


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
    obj = Client.call('ak.wwise.core.object.get', get_args)
    return obj['return'][0]['sound:originalWavFilePath'] if obj else ''


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


# 将对象转换类型
def convert_to_type(obj, target_type: str):
    # 先在父级创建一个不同名的新对象
    parent = get_parent_objects(obj, False)[0]
    original_name = obj['name']
    temp_object = create_object(original_name + '_Temp', target_type, parent, 'rename')
    # 创建失败，返回
    if temp_object is None:
        return
    # 将所有子对象移至新对象上
    for child in get_children_objects(obj, False):
        move_object(child, temp_object)
    # 删除原对象
    delete_object(obj)
    # 将新对象重命名成原对象名
    rename_object(temp_object, original_name)


# 导入音频文件
def import_audio_file(wave_path, parent_obj, new_sound_name):
    import_args = {
        'importOperation': 'createNew',
        'default': {
            'importLanguage': 'SFX'
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


# 给一个对象重命名
def rename_object(obj, new_name: str):
    rename_args = {
        'object': obj['id'],
        'value': new_name
    }
    Client.call('ak.wwise.core.object.setName', rename_args)


# 设置对象的属性
def set_object_property(obj, property_name: str, value):
    set_args = {
        'object': obj['id'],
        'property': property_name,
        'value': value
    }
    Client.call('ak.wwise.core.object.setProperty', set_args)


# 删除一个对象
def delete_object(obj):
    delete_args = {
        'object': obj['id'],
    }
    Client.call('ak.wwise.core.object.delete', delete_args)
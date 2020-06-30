# 获取选中的对象列表
def get_selected_objects(client):
    get_args = {
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = client.call('ak.wwise.ui.getSelectedObjects', get_args)
    return result['objects'] if result is not None else []


# 获取一个对象递归上层的所有母对象
def get_parent_objects(client, obj, include_ancestors: bool):
    query_args = {
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
    result = client.call('ak.wwise.core.object.get', query_args)
    return result['return'] if result is not None else []


# 获取一个对象递归下层的所有子对象
def get_children_objects(client, obj, include_descendants: bool):
    query_args = {
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
    result = client.call('ak.wwise.core.object.get', query_args)
    return result['return'] if result is not None else []


# 检测路径是否已有对象
def object_exists_at_path(client, path: str):
    query_args = {
        'from': {
            'path': [path]
        },
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    result = client.call('ak.wwise.core.object.get', query_args)
    return result is not None


# 在指定路径下创建一个新的对象
def create_object(client, name: str, obj_type: str, parent_path: str, replace_if_exist: bool):
    create_args = {
        'parent': parent_path,
        'type': obj_type,
        'name': name,
        'onNameConflict': 'replace' if replace_if_exist else 'rename'
    }
    options = {
        'return': ['id', 'name', 'type', 'path']
    }
    return client.call('ak.wwise.core.object.create', create_args, options)


# 移动对象到新的路径
def move_object(client, obj, new_parent):
    move_args = {
        'object': obj['id'],
        'parent': new_parent['id'],
        'onNameConflict': 'replace'
    }
    return client.call('ak.wwise.core.object.move', move_args)


# 执行Wwise操作
def execute_ui_command(client, objects, command: str):
    if len(objects) == 0:
        return
    obj_ids = [obj['id'] for obj in objects]
    execute_args = {
        'command': command,
        'objects': obj_ids
    }
    client.call('ak.wwise.ui.commands.execute', execute_args)


# 在Wwise里选中对象
def open_item_in_wwise_by_path(client, path):
    select_args = {
        'command': 'FindInProjectExplorerSyncGroup1',
        'objects': [path]
    }
    client.call('ak.wwise.ui.commands.execute', select_args)


# 给一个对象重命名
def rename_object(client, obj, new_name: str):
    rename_args = {
        'object': obj['id'],
        'value': new_name
    }
    client.call('ak.wwise.core.object.setName', rename_args)


# 设置对象的属性
def set_object_property(client, obj, property_name: str, value):
    set_args = {
        'object': obj['id'],
        'property': property_name,
        'value': value
    }
    client.call('ak.wwise.core.object.setProperty', set_args)


# 删除一个对象
def delete_object(client, obj):
    delete_args = {
        'object': obj['id'],
    }
    client.call('ak.wwise.core.object.delete', delete_args)
# 获取选中的对象列表
def get_selected_objects(client):
    get_args = {
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return client.call('ak.wwise.ui.getSelectedObjects', get_args)['objects']


# 在对象列表中根据类型过滤
def filter_objects_by_type(objects: list, filter_type: str):
    valid_objects = []
    for result in objects:
        if result['type'] == filter_type:
            valid_objects.append(result)
    return valid_objects


# 在对象中筛选名称包含特定字符的
def filter_objects_by_name(objects: list, filter_name: str, case_sensitive: bool):
    objects_filtered = []
    for obj in objects:
        if case_sensitive:
            if filter_name in obj['name']:
                objects_filtered.append(obj)
        else:
            if filter_name.lower() in obj['name'].lower():
                objects_filtered.append(obj)
    return objects_filtered


# 获取一个对象递归下层的所有子对象
def get_all_descendant_objects(client, obj):
    query_args = {
        'from': {
            'id': [obj['id']]
        },
        'transform': [
            {'select': ['descendants']},
        ],
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return client.call('ak.wwise.core.object.get', query_args)['return']


# 获取一个对象直属下层的所有子对象
def get_child_objects(client, obj):
    query_args = {
        'from': {
            'id': [obj['id']]
        },
        'transform': [
            {'select': ['children']},
        ],
        'options': {
            'return': ['id', 'name', 'type', 'path']
        }
    }
    return client.call('ak.wwise.core.object.get', query_args)['return']


# 选中一批对象
def select_objects(client, objects):
    if len(objects) == 0:
        return
    obj_ids = [obj['id'] for obj in objects]
    select_args = {
        'command': 'FindInProjectExplorerSyncGroup1',
        'objects': obj_ids
    }
    client.call('ak.wwise.ui.commands.execute', select_args)


# 在批量编辑器中打开一批对象
def open_in_multi_editor(client, objects):
    if len(objects) == 0:
        return
    obj_ids = [obj['id'] for obj in objects]
    select_args = {
        'command': 'ShowMultiEditor',
        'objects': obj_ids
    }
    client.call('ak.wwise.ui.commands.execute', select_args)


# 给一个对象重命名
def rename_object(client, obj, new_name: str):
    rename_args = {
        'object': obj['id'],
        'value': new_name
    }
    client.call('ak.wwise.core.object.setName', rename_args)

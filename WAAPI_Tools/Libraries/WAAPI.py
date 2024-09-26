import os.path
from waapi import WaapiClient

Client = WaapiClient(url='ws://127.0.0.1:8080/waapi')


# 获取Waapi客户端
def get_client():
    global Client
    if not Client:
        Client = WaapiClient(url='ws://127.0.0.1:8080/waapi')
    return Client


# region Query
# 获取工程全局属性
def get_project_property(property_name: str):
    if not Client:
        return None
    try:
        get_args = {
            'waql': 'from type Project',
            'options': {
                'return': [property_name]
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        return result['return'][0][property_name] if result else None
    except Exception as e:
        print(e)
        return None


# 获取对象的属性
def get_object_property(obj: dict, property_name: str):
    if not Client or not obj:
        return None
    try:
        obj_id = obj['id']
        get_args = {
            'waql': f'from object \"{obj_id}\"',
            'options': {
                'return': [property_name]
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        if not result or len(result['return']) == 0:
            return None
        return_obj = result['return'][0]
        return return_obj[property_name] if property_name in return_obj else None
    except Exception as e:
        print(e)
        return None


# 获取选中的对象列表
def get_selected_objects():
    if not Client:
        return []
    try:
        get_args = {
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        result = Client.call('ak.wwise.ui.getSelectedObjects', get_args)
        return result['objects'] if result else []
    except Exception as e:
        print(e)
        return []


# 获取一个对象所有的引用
def get_references_to_object(obj: dict):
    if not Client:
        return []
    try:
        obj_id = obj['id']
        get_args = {
            'waql': f'from object \"{obj_id}\" select referencesTo',
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        return result['return'] if result else []
    except Exception as e:
        print(e)
        return []


# 获取一个对象直属上层的对象
def get_parent_object(obj: dict):
    if not Client or not obj:
        return None
    try:
        obj_id = obj['id']
        get_args = {
            'waql': f'from object \"{obj_id}\" select parent',
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        parents = result['return']
        return parents[0] if len(parents) > 0 else None
    except Exception as e:
        print(e)
        return None


# 获取一个对象递归上层的所有对象
def get_ancestor_objects(obj: dict):
    if not Client or not obj:
        return []
    try:
        obj_id = obj['id']
        get_args = {
            'waql': f'from object \"{obj_id}\" select ancestors',
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        return result['return'] if result else []
    except Exception as e:
        print(e)
        return []


# 获取一个对象递归下层的所有子对象
def get_child_objects(obj: dict, include_descendants: bool):
    if not Client or not obj:
        return []
    try:
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
    except Exception as e:
        print(e)
        return []


# 获取整个Wwise工程所有对象
def get_global_objects():
    if not Client:
        return []
    try:
        global_objects = []
        objects_type = {'WorkUnit', 'ActorMixer', 'Folder', 'SwitchContainer', 'BlendContainer', 'RandomSequenceContainer',
                        'Sound', 'Event', 'AuxBus', 'Bus', 'SoundBank', 'StateGroup', 'SwitchGroup', 'GameParameter',
                        'MusicSwitchContainer', 'MusicPlaylistContainer', 'MusicSegment', 'MusicTrack'}
        for obj_type in objects_type:
            results = find_all_objects_by_type(obj_type)
            global_objects += results
        return global_objects
    except Exception as e:
        print(e)
        return []


# 通过guid获取对象完整信息
def get_full_info_from_obj_id(obj_id):
    if not Client:
        return None
    try:
        get_args = {
            'from': {
                'id': [obj_id]
            },
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        return_obj = Client.call('ak.wwise.core.object.get', get_args)
        if not return_obj or len(return_obj['return']) == 0:
            return None
        return return_obj['return'][0]
    except Exception as e:
        print(e)
        return None


# 从路径获取对象
def get_object_from_path(path: str):
    if not Client:
        return None
    try:
        get_args = {
            'waql': f'from object \"{path}\"',
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        return_obj = Client.call('ak.wwise.core.object.get', get_args)
        if not return_obj or len(return_obj['return']) == 0:
            return None
        return return_obj['return'][0]
    except Exception as e:
        print(e)
        return None


# 从名称和类型获取对象
def find_object_by_name_and_type(obj_name: str, obj_type: str, exact_match=True):
    if not Client:
        return None
    try:
        get_args = {
            'waql': f'from type {obj_type} where name: \"{obj_name}\"',
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        return_obj = Client.call('ak.wwise.core.object.get', get_args)
        if return_obj is None or len(return_obj['return']) == 0:
            return None
        # 可模糊查找
        if not exact_match:
            return return_obj['return'][0]
        # 仅查找名称完全一致的对象
        for obj in return_obj['return']:
            if obj['name'] == obj_name:
                return obj
        return None
    except Exception as e:
        print(e)
        return None


# 查找所有符合名称的对象
def find_all_objects_by_name(obj_name: str, exact_match: bool):
    if not Client:
        return []
    try:
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
    except Exception as e:
        print(e)
        return []


# 查找所有特定类型的对象
def find_all_objects_by_type(type_name: str):
    if not Client:
        return []
    try:
        get_args = {
            'waql': f'from type {type_name}',
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        return result['return'] if result else []
    except Exception as e:
        print(e)
        return []
# endregion Query


# region CommonOperation
# 在指定路径下创建一个新的对象
def create_object(obj_name: str, obj_type: str, parent_obj: dict, on_name_conflict='fail'):
    if not Client or not parent_obj:
        return None
    try:
        create_args = {
            'parent': parent_obj['id'],
            'type': obj_type,
            'name': obj_name,
            'onNameConflict': on_name_conflict
        }
        result_obj = Client.call('ak.wwise.core.object.create', create_args)
        if result_obj:
            result_obj = get_full_info_from_obj_id(result_obj['id'])
            print(f"{obj_type} [{obj_name}] created under [{parent_obj['path']}]")
        return result_obj
    except Exception as e:
        print(e)
        return None


# 移动对象到新的路径
def move_object(obj: dict, new_parent: dict):
    if not Client or not obj or not new_parent:
        return False
    try:
        move_args = {
            'object': obj['id'],
            'parent': new_parent['id'],
            'onNameConflict': 'replace'
        }
        Client.call('ak.wwise.core.object.move', move_args)
        return True
    except Exception as e:
        print(e)
        return False


# 复制对象到某个对象下面
def copy_object(obj: dict, parent: dict):
    if not Client or not obj or not parent:
        return False
    try:
        copy_args = {
            'object': obj['id'],
            'parent': parent['id'],
            'onNameConflict': 'rename'
        }
        options = {
            'return': ['id', 'name', 'type', 'path']
        }
        result = Client.call('ak.wwise.core.object.copy', copy_args, options)
        result = get_full_info_from_obj_id(result['id'])
        if result is None:
            print(f'Copy {obj} to {parent} failed!')
        return result
    except Exception as e:
        print(e)
        return None


# 给一个对象重命名
def rename_object(obj: dict, new_name: str):
    if not Client or not obj:
        return False
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
    except Exception as e:
        print(e)
        return False


# 设置对象的属性
def set_object_property(obj: dict, property_name: str, value):
    if not Client or not obj:
        return False
    try:
        set_args = {
            'object': obj['id'],
            'property': property_name,
            'value': value
        }
        Client.call('ak.wwise.core.object.setProperty', set_args)
        return True
    except Exception as e:
        print(e)
        return False


# 设置对象的引用
def set_object_reference(obj: dict, reference_type: str, value: dict):
    if not Client or not obj:
        return False
    try:
        set_args = {
            'object': obj['id'],
            'reference': reference_type,
            'value': value['id']
        }
        Client.call('ak.wwise.core.object.setReference', set_args)
        return True
    except Exception as e:
        print(e)
        return False


# 为对象设置备注
def set_object_notes(obj: dict, notes: str):
    if not Client or not obj:
        return False
    try:
        set_args = {
            "object": obj['id'],
            "value": notes
        }
        Client.call('ak.wwise.core.object.setNotes', set_args)
        return True
    except Exception as e:
        print(e)
        return False


# 删除一个对象
def delete_object(obj: dict):
    if not Client or not obj:
        return False
    try:
        delete_args = {
            'object': obj['id'],
        }
        Client.call('ak.wwise.core.object.delete', delete_args)
        print(f"Deleted {obj['type']} [{obj['name']}]")
        return True
    except Exception as e:
        print(e)
        return False
# endregion CommonOperation


# region LogicContainer
# 为顺序容器设置播放列表
def set_sequence_container_playlist(container: dict, playlist: list):
    if not Client or not container:
        return False
    try:
        set_args = {
            'objects': [{
                'object': container['id'],
                '@Playlist': [item['id'] for item in playlist]
            }],
            'onNameConflict': 'merge',
            'listMode': 'replaceAll'
        }
        Client.call('ak.wwise.core.object.set', set_args)
        return True
    except Exception as e:
        print(e)
        return False
# endregion LogicContainer


# region AudioSource
# 导入新的音频文件
def import_audio_file(wave_path: str, sound: dict, new_sound_name: str, language='SFX'):
    if not Client or not sound:
        return None
    if not os.path.exists(wave_path):
        print(f'File not found at {wave_path}')
        return None
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
                    'importLocation': sound['id'],
                    'objectPath': '<Sound>' + new_sound_name
                },
            ]
        }
        result = Client.call('ak.wwise.core.audio.import', import_args)
        return result['objects'][0] if result else None
    except Exception as e:
        print(e)
        return None


# 为声音创建静音源插件
def add_silence(obj: dict, length: int, language='SFX'):
    if not Client or not obj:
        return None
    try:
        set_args = {
            'objects': [{
                'object': obj['id'],
                'children': [
                    {
                        'type': 'SourcePlugin',
                        'name': f'Silence_{language}' if language != 'SFX' else 'Silence',
                        'classId': 6619138,
                        '@Length': length
                    }
                ]
            }]
        }
        if language != 'SFX':
            set_args['objects'][0]['children'][0]['language'] = language
        options = {
            'return': ['id', 'name', 'type', 'path']
        }
        result = Client.call('ak.wwise.core.object.set', set_args, options)
        return result['objects'][0] if result else None
    except Exception as e:
        print(e)
        return None


# 从Sound层级获取包含的AudioSource
def get_audio_source_from_sound(sound: dict):
    if not Client or not sound:
        return None
    try:
        get_args = {
            'from': {
                'id': [sound['id']]
            },
            'transform': [
                {'select': ['children']},
            ],
            'options': {
                'return': ['id', 'name', 'type', 'path']
            }
        }
        result = Client.call('ak.wwise.core.object.get', get_args)
        return result['return'][0] if result else None
    except Exception as e:
        print(e)
        return None
# endregion AudioSource


# region SoundBank
# 获取bank中的内容
def get_bank_inclusions(bank: dict):
    if not Client or not bank:
        return None
    try:
        get_args = {
            'soundbank': bank['id']
        }
        result = Client.call('ak.wwise.core.soundbank.getInclusions', get_args)
        return result['inclusions'] if result else None
    except Exception as e:
        print(e)
        return None


# 清除Bank中所有内容
def clear_bank_inclusions(bank: dict):
    if not Client or not bank:
        return False
    if bank['type'] != 'SoundBank':
        return False
    try:
        set_args = {
            'soundbank': bank['id'],
            'operation': 'replace',
            'inclusions': []
        }
        Client.call('ak.wwise.core.soundbank.setInclusions', set_args)
        return True
    except Exception as e:
        print(e)
        return False


# 为SoundBank设置包含内容
def set_bank_inclusion(bank: dict, inclusion: dict):
    if not Client or not bank or not inclusion:
        return False
    try:
        set_args = {
            'soundbank': bank['id'],
            'operation': 'add',
            'inclusions': [
                {
                    'object': inclusion['id'],
                    'filter': ['events', 'structures', 'media']
                }
            ]
        }
        Client.call('ak.wwise.core.soundbank.setInclusions', set_args)
        return True
    except Exception as e:
        print(e)
        return False
# endregion SoundBank


# region Localization
# 获取所有的语言
def get_language_list():
    if not Client:
        return []
    try:
        args = {
            'from': {
                'ofType': ['Language']
            }
        }
        options = {
            'return': ['name']
        }
        result = Client.call('ak.wwise.core.object.get', args, options)
        return result['return'] if result else []
    except Exception as e:
        print(e)
        return []
# endregion Localization


# region UICommand
# 执行Wwise操作
def execute_ui_command(objects: list, command: str):
    if not Client or len(objects) == 0:
        return False
    try:
        obj_ids = [obj['id'] for obj in objects]
        execute_args = {
            'command': command,
            'objects': obj_ids
        }
        Client.call('ak.wwise.ui.commands.execute', execute_args)
        return True
    except Exception as e:
        print(e)
        return False


# 在Wwise里选中对象
def select_objects_in_wwise(objects: list):
    if not Client:
        return False
    try:
        id_list = [obj['id'] for obj in objects]
        select_args = {
            'command': 'FindInProjectExplorerSyncGroup1',
            'objects': id_list
        }
        Client.call('ak.wwise.ui.commands.execute', select_args)
        select_args = {
            'command': 'Inspect',
            'objects': id_list
        }
        Client.call('ak.wwise.ui.commands.execute', select_args)
        bring_wwise_to_foreground()
        return True
    except Exception as e:
        print(e)
        return False


# 将Wwise窗口带到最前方
def bring_wwise_to_foreground():
    if not Client:
        return False
    Client.call('ak.wwise.ui.bringToForeground')
    return True


# 开始记录操作
def begin_undo_group(action: str):
    if not Client:
        return False
    Client.call('ak.wwise.core.undo.beginGroup')
    print(f'Begin Action [{action}]')
    return True


# 结束记录操作
def end_undo_group(action: str):
    if not Client:
        return False
    try:
        end_args = {
            'displayName': 'WAAPI Tool - ' + action
        }
        Client.call('ak.wwise.core.undo.endGroup', end_args)
        print(f'End Action [{action}]')
        return True
    except Exception as e:
        print(e)
        return False


# 撤销操作
def undo():
    if not Client:
        return False
    try:
        execute_args = {
            'command': 'Undo'
        }
        Client.call('ak.wwise.ui.commands.execute', execute_args)
        return True
    except Exception as e:
        print(e)
        return False


# 重做操作
def redo():
    if not Client:
        return False
    try:
        execute_args = {
            'command': 'Redo'
        }
        Client.call('ak.wwise.ui.commands.execute', execute_args)
        return True
    except Exception as e:
        print(e)
        return False


# 将文件添加到版本控制
def add_to_source_control(file_path: str):
    if not Client:
        return False
    try:
        add_args = {
            'files': file_path,
        }
        Client.call('ak.wwise.core.sourceControl.add', add_args)
        return True
    except Exception as e:
        print(e)
        return False
# endregion UICommand

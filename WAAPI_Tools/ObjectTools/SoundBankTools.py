import os

from Libraries import WAAPI, FileTools
from ObjectTools import CommonTools


# 为每个选中的对象创建一个SoundBank
def create_bank_for_object(obj: dict):
    bank_name = CommonTools.get_full_name_with_acronym(obj)
    if bank_name.startswith('Events_'):
        bank_name = bank_name[7:]
    bank = WAAPI.find_object_by_name_and_type(bank_name, 'SoundBank')
    if bank is None:
        bank = create_sound_bank_by_name(bank_name)
    else:
        print(f'SoundBank [{bank_name}] already exists, replacing its inclusion instead.')
    WAAPI.set_bank_inclusion(bank, obj)
    CommonTools.update_notes_and_color(obj)
    WAAPI.select_objects_in_wwise([bank])
    return True


# 根据名字创建SoundBank
def create_sound_bank_by_name(bank_name: str):
    if '_' in bank_name:
        parent_path = '\\SoundBanks\\' + bank_name.replace('_', '\\')
        parent_path = os.path.dirname(parent_path)
        parent = CommonTools.create_folders_for_path(parent_path)
    else:
        parent_path = '\\SoundBanks\\Default Work Unit'
        parent = WAAPI.get_object_from_path(parent_path)
    new_bank = WAAPI.create_object(bank_name, 'SoundBank', parent)
    return new_bank


# 传统方式获取Bank大小
def get_bank_size(bank: dict):
    wav_size = wem_size = used_files_count = 0
    unused_files = []
    for inclusion in WAAPI.get_bank_inclusions(bank):
        if 'media' in inclusion['filter']:
            bank_id = inclusion['object']
            get_args = {
                'waql': f'from object \"{bank_id}\" select descendants where type = \"AudioFileSource\"',
                'options': {
                    'return': ['name', 'originalWavFilePath', 'convertedWemFilePath', 'audioSourceLanguage']
                }
            }
            result = WAAPI.Client.call('ak.wwise.core.object.get', get_args)
            bank_name = bank['name']
            if len(result) == 0:
                print(f'Bank[{bank_name}]不包含任何资源！')
                return 5

            for audio_source in result['return']:
                language = audio_source['audioSourceLanguage']['name']
                if language == 'SFX' or language == 'Chinese':
                    wav_path = audio_source['originalWavFilePath']
                    if not os.path.exists(wav_path):
                        print(f'在Bank[{bank_name}]中找不到源文件[{wav_path}!]')
                        continue
                    wav_name = os.path.basename(wav_path)
                    wav_size += os.path.getsize(wav_path) / 1024
                    wem_path = audio_source['convertedWemFilePath']
                    if os.path.exists(wem_path):
                        wem_size += os.path.getsize(wem_path) / 1024
                        used_files_count += 1
                    else:
                        unused_files.append(wav_name)

    wav_size = round(wav_size / 1024, 2)
    wem_size = round(wem_size / 1024, 2)
    return wav_size, wem_size, used_files_count, unused_files


# 计算多个Bank合计大小
def get_total_bank_size(banks: list):
    total_wav_size = total_wem_size = total_used_files_count = 0
    total_unused_files = []
    for bank in banks:
        if bank['type'] == 'SoundBank':
            wav_size, wem_size, used_files_count, unused_files = get_bank_size(bank)
            total_wav_size += wav_size
            total_wem_size += wem_size
            total_used_files_count += used_files_count
            total_unused_files += unused_files
    return total_wav_size, total_wem_size, total_used_files_count, total_unused_files


# 把一批对象添加到的bank中，使用统一的inclusion
def add_objects_to_bank(bank: dict, objects: list, inclusion_type: list):
    inclusions = []
    for obj in objects:
        inclusion = {
            'object': obj['id'],
            'filter': inclusion_type
        }
        inclusions.append(inclusion)

    set_args = {
        'soundbank': bank['id'],
        'operation': 'add',
        'inclusions': inclusions
    }
    WAAPI.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 把一批对象添加到的bank中，每个对象使用单独的inclusion
def add_objects_to_bank_with_individual_inclusion(bank: dict, objects):
    set_args = {
        'soundbank': bank['id'],
        'operation': 'add',
        'inclusions': objects
    }
    WAAPI.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 设置SoundBank的包含内容
def set_inclusion_type(bank: dict, inclusion_types: list):
    if bank['type'] != 'SoundBank':
        return
    get_args = {
        'soundbank': bank['id']
    }
    # 获取bank的内容并更改inclusion类别
    inclusions = WAAPI.Client.call('ak.wwise.core.soundbank.getInclusions', get_args)['inclusions']
    for inclusion in inclusions:
        inclusion['filter'] = inclusion_types
    # 设置新的内容
    set_args = {
        'soundbank': bank['id'],
        'operation': 'replace',
        'inclusions': inclusions
    }
    WAAPI.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 生成所有Event与Bank的对应关系
def generate_event_bank_map():
    event_bank_map = {}
    all_banks = WAAPI.find_all_objects_by_type('SoundBank')
    for bank in all_banks:
        inclusions = WAAPI.get_bank_inclusions(bank)
        for inclusion in inclusions:
            obj_id = inclusion['object']
            obj = WAAPI.get_full_info_from_obj_id(obj_id)
            if obj['path'].startswith('\\Events\\'):
                descendants = CommonTools.get_descendants_by_type(obj, 'Event')
                for event in descendants:
                    event_bank_map[event['name']] = bank['name']
    FileTools.export_to_json(event_bank_map, 'EventBankMap')

import os

from Libraries import WAAPI, FileTools
from ObjectTools import CommonTools, EventTools, AudioSourceTools


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
    WAAPI.set_bank_inclusion(bank, obj, True)
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
        parent = WAAPI.find_object_by_path(parent_path)
    new_bank = WAAPI.create_child_object(bank_name, 'SoundBank', parent)
    return new_bank


# 计算多个Bank合计大小
def get_total_bank_size(banks: list):
    wav_size = memory_wem_size = stream_wem_size = 0
    used_files = []
    for bank in banks:
        if bank['type'] == 'SoundBank':
            wav_size, memory_wem_size, stream_wem_size, used_files = get_bank_size(bank, wav_size, memory_wem_size, stream_wem_size, used_files)
    wav_size = round(wav_size / 1024, 2)
    memory_wem_size = round(memory_wem_size / 1024, 2)
    stream_wem_size = round(stream_wem_size / 1024, 2)
    return wav_size, memory_wem_size, stream_wem_size, used_files


# 传统方式获取Bank大小
def get_bank_size(bank: dict, total_wav_size: float, total_memory_wem_size: float, total_stream_wem_size: float, used_files: list):
    for inclusion in WAAPI.get_bank_inclusions(bank):
        if 'media' in inclusion['filter']:
            inclusion_obj = WAAPI.get_full_info_from_obj_id(inclusion['object'])
            # Bank包含Events中的内容
            if 'Events' in inclusion_obj['path']:
                total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files = (
                    get_event_media_size(inclusion_obj, total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files))
            # Bank包含ActorMixerHierarchy中的内容
            else:
                total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files = (
                    get_object_media_size(inclusion_obj, total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files))
    return total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files


# 获取Events中的对象包含的所有音频文件的大小
def get_event_media_size(obj: dict, total_wav_size: float, total_memory_wem_size: float, total_stream_wem_size: float, used_files: list):
    events = WAAPI.get_descendants_of_type(obj, 'Event')
    if len(events) > 0:
        for event in events:
            targets = EventTools.get_event_targets(event)
            for target in targets:
                total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files = (
                    get_object_media_size(target, total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files))
    return total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files


# 获取ActorMixerHierarchy中的对象包含的所有音频文件的大小
def get_object_media_size(obj: dict, total_wav_size: float, total_memory_wem_size: float, total_stream_wem_size: float, used_files: list):
    audio_sources = WAAPI.get_descendants_of_type(obj, 'AudioFileSource')
    if len(audio_sources) > 0:
        for audio_source in audio_sources:
            wav_path = AudioSourceTools.get_source_file_path(audio_source)
            if not os.path.exists(wav_path) or wav_path in used_files:
                continue
            used_files.append(wav_path)
            wav_size = os.path.getsize(wav_path) / 1024
            total_wav_size += wav_size
            print(f'{wav_path} has size of {wav_size}KB')
            wem_path = WAAPI.get_object_property(audio_source, 'convertedWemFilePath')
            if os.path.exists(wem_path):
                wem_size = os.path.getsize(wem_path) / 1024
                is_streaming = WAAPI.get_object_property(WAAPI.get_parent_object(audio_source), 'IsStreamingEnabled')
                if is_streaming:
                    total_stream_wem_size += wem_size
                else:
                    total_memory_wem_size += wem_size
                print(f'{wem_path} has size of {wem_size}KB')
    return total_wav_size, total_memory_wem_size, total_stream_wem_size, used_files


# 把一批对象添加到的bank中，使用统一的inclusion
def add_objects_to_bank(bank: dict, objects: list, inclusion_type: list):
    for obj in objects:
        WAAPI.set_bank_inclusion(bank, obj, False, inclusion_type)
    return True


# 设置SoundBank的包含内容
def set_inclusion_type(bank: dict, inclusion_types: list):
    if bank['type'] != 'SoundBank':
        return
    inclusions = WAAPI.get_bank_inclusions(bank)
    for inclusion in inclusions:
        inclusion['filter'] = inclusion_types
        WAAPI.set_bank_inclusion(bank, inclusion, False)


# 为Bank添加内容，可选择是否清除已有内容
def set_inclusions(bank: dict, inclusion: dict, remove_existing: bool):
    if remove_existing:
        WAAPI.clear_bank_inclusions(bank)
    return WAAPI.set_bank_inclusion(bank, inclusion, remove_existing)


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
                descendants = WAAPI.get_descendants_of_type(obj, 'Event')
                for event in descendants:
                    event_bank_map[event['name']] = bank['name']
    FileTools.export_to_json(event_bank_map, 'EventBankMap')

import os
from Libraries import FileTools, WAAPI
from ObjectTools import EventTools, ProjectTools
from Threading.BatchProcessor import BatchProcessor


# 从FMOD导出的json导入Event
def import_fmod_events():
    work_unit = WAAPI.get_object_from_path('\\Actor-Mixer Hierarchy\\Default Work Unit')
    json = FileTools.import_from_json()
    if json is None:
        return
    batch_processor = BatchProcessor(json, lambda event: import_fmod_event(event, work_unit), '从FMOD导入事件')
    batch_processor.start()


def import_fmod_event(event: dict, work_unit: dict):
    event_name = event['name']
    existing_event = WAAPI.find_object_by_name_and_type(event_name, 'Event')
    if existing_event:
        print(f'Existing event [{event_name}] found, will not import.')
        return
    print(f'Begin import FMOD event [{event_name}]')
    tracks = event['tracks']
    if len(tracks) > 1:
        root = WAAPI.create_object(event_name, 'BlendContainer', work_unit)
        if not root:
            print(f'Create blend container failed: {event_name}')
            return
        WAAPI.set_object_property(root, 'Volume', event['volume'])
        for i in range(len(tracks)):
            import_fmod_track(tracks[i], i, root)
    else:
        root = import_fmod_track(tracks[0], 0, work_unit)
    EventTools.create_play_event(root)


def import_fmod_track(track: dict, index: int, parent: dict):
    if not parent:
        return None
    container = None
    instrument = None
    last_clip_end = 0
    clips = sorted(track['clips'], key=lambda c: c['startTime'])
    playlist = []
    for i in range(len(clips)):
        clip = clips[i]
        if clip['instrument'] == {}:
            continue
        clip_start = clip['startTime']
        if clip_start > 0:
            if container is None:
                # 创建一个连续播放的顺序容器
                container = WAAPI.create_object(f'Track_{index}', 'RandomSequenceContainer', parent)
                WAAPI.set_object_property(container, 'RandomOrSequence', 0)
                WAAPI.set_object_property(container, 'PlayMechanismStepOrContinuous', 0)
            # 创建一段静音
            silence_obj = WAAPI.create_object(f'Silence_{i}', 'Sound', container)
            playlist.append(silence_obj)
            WAAPI.add_silence(silence_obj, clip_start - last_clip_end)
            instrument = import_fmod_instrument(clip['instrument'], container, i)
            if instrument:
                playlist.append(instrument)
        else:
            instrument = import_fmod_instrument(clip['instrument'], parent, index)
        last_clip_end = clip_start + clip['length']
    # 为顺序容器设置播放顺序
    if container:
        WAAPI.set_sequence_container_playlist(container, playlist)
        return container
    else:
        return instrument


def import_fmod_instrument(instrument: dict, parent: dict, index: int):
    instrument_type = instrument['type']
    if instrument_type == 'multi':
        return import_fmod_random_container(instrument, f'Instrument_{index}', parent)
    if instrument_type == 'single':
        return import_single_sound(instrument, parent)


# 从FMOD导入RandomContainer
def import_fmod_random_container(instrument: dict, node_name: str, parent: dict):
    if not parent:
        return None
    container = WAAPI.create_object(node_name, 'RandomSequenceContainer', parent)
    if not container:
        print(f'Create random container failed: {node_name}')
        return None
    playlist = instrument['playList']
    play_mode = playlist['playMode']
    WAAPI.set_object_property(container, 'Pitch', instrument['pitch'])
    WAAPI.set_object_property(container, 'Volume', instrument['volume'])
    WAAPI.set_object_property(container, 'PlayMechanismLoop', instrument['loop'])
    if play_mode == 'Random':
        WAAPI.set_object_property(container, 'RandomOrSequence', 1)
        WAAPI.set_object_property(container, 'NormalOrShuffle', 1)
    elif play_mode == 'Shuffle':
        WAAPI.set_object_property(container, 'RandomOrSequence', 1)
        WAAPI.set_object_property(container, 'NormalOrShuffle', 0)
    elif play_mode == 'SequenceLocal':
        WAAPI.set_object_property(container, 'RandomOrSequence', 0)
    elif play_mode == 'SequenceGlobal':
        WAAPI.set_object_property(container, 'RandomOrSequence', 0)
    for item in playlist['items']:
        if item['type'] == 'single':
            import_single_sound(item, container)
    return container


# 从FMOD导入单个音效
def import_single_sound(instrument: dict, parent: dict):
    if not parent:
        return None
    asset_path = instrument['asset']
    sound_name = asset_path.split('/')[-1][:-4]
    sound = WAAPI.create_object(sound_name, 'Sound', parent)
    if not sound:
        print(f'Create sound failed: {sound_name}')
        return None
    asset_path = str(os.path.join(ProjectTools.get_originals_folder(), 'SFX', asset_path))
    WAAPI.import_audio_file(asset_path, sound, sound_name)
    WAAPI.set_object_property(sound, 'IsLoopingEnabled', 0)
    WAAPI.set_object_property(sound, 'Pitch', instrument['pitch'])
    WAAPI.set_object_property(sound, 'Volume', instrument['volume'])
    return sound


# 从FMOD导出的json导入Preset
def import_fmod_presets():
    state_root = WAAPI.get_object_from_path('\\States\\Default Work Unit')
    switch_root = WAAPI.get_object_from_path('\\Switches\\Default Work Unit')
    rtpc_root = WAAPI.get_object_from_path('\\Game Parameters\\Default Work Unit')
    json = FileTools.import_from_json()
    if json is None:
        return
    for preset in json:
        preset_name = preset['name']
        preset_type = preset['type']
        if preset_type == 'Label':
            if preset['isGlobal']:
                state = WAAPI.create_object(preset_name, 'StateGroup', state_root)
                if state:
                    print(f'StateGroup created: {preset_name}')
                    for label in preset['labels']:
                        WAAPI.create_object(label, 'State', state)
            else:
                switch = WAAPI.create_object(preset_name, 'SwitchGroup', switch_root)
                if switch:
                    print(f'SwitchGroup created: {preset_name}')
                    for label in preset['labels']:
                        WAAPI.create_object(label, 'Switch', switch)
        else:
            rtpc = WAAPI.create_object(preset_name, 'GameParameter', rtpc_root)
            if rtpc:
                min_value = preset['minValue']
                max_value = preset['maxValue']
                WAAPI.set_object_property(rtpc, 'InitialValue', preset['initValue'])
                WAAPI.set_object_property(rtpc, 'Min', min_value)
                WAAPI.set_object_property(rtpc, 'Max', max_value)
                slew_rate = preset['slewRateUp']
                if slew_rate > 0:
                    WAAPI.set_object_property(rtpc, 'RTPCRamping', 1)
                    WAAPI.set_object_property(rtpc, 'SlewRateUp', slew_rate)
                    WAAPI.set_object_property(rtpc, 'SlewRateDown', preset['slewRateDown'] if 'slewRateDown' in preset else slew_rate)
                if preset_type == 'BuiltInDistance':
                    WAAPI.set_object_property(rtpc, 'BindToBuiltInParam', 1)
                print(f'RTPC created: {preset_name} ({min_value}-{max_value})')


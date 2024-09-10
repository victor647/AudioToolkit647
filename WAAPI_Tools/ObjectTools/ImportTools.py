import os
from Libraries import FileTools, WaapiTools


# 从FMOD导出的json导入Event
def import_fmod_events():
    work_unit = WaapiTools.get_object_from_path('\\Actor-Mixer Hierarchy\\Default Work Unit')
    json = FileTools.import_from_json()
    for event in json:
        event_name = event['name']
        tracks = event['tracks']
        root = None
        if len(tracks) > 1:
            root = WaapiTools.create_object(event_name, 'BlendContainer', work_unit, 'fail')
            if not root:
                print(f'Create blend container failed: {event_name}')
                continue
            for i in range(len(tracks)):
                import_fmod_track(tracks[i], i, root)
        else:
            import_fmod_track(tracks[0], 0, work_unit)
        if root:
            WaapiTools.set_object_property(root, 'Volume', event['volume'])


def import_fmod_track(track, index, parent):
    if not parent:
        return
    for clip in track['clips']:
        instrument = clip['instrument']
        if instrument == {}:
            continue
        if instrument['type'] == 'multi':
            import_fmod_random_container(instrument, f'Track_{index}', parent)


# 从FMOD导入RandomContainer
def import_fmod_random_container(instrument, node_name, parent):
    if not parent:
        return
    container = WaapiTools.create_object(node_name, 'RandomSequenceContainer', parent, 'fail')
    if not container:
        print(f'Create random container failed: {node_name}')
        return
    playlist = instrument['playList']
    play_mode = playlist['playMode']
    WaapiTools.set_object_property(container, 'Pitch', instrument['pitch'])
    WaapiTools.set_object_property(container, 'Volume', instrument['volume'])
    WaapiTools.set_object_property(container, 'PlayMechanismLoop', instrument['loop'])
    if play_mode == 'Random':
        WaapiTools.set_object_property(container, 'RandomOrSequence', 1)
        WaapiTools.set_object_property(container, 'NormalOrShuffle', 1)
    elif play_mode == 'Shuffle':
        WaapiTools.set_object_property(container, 'RandomOrSequence', 1)
        WaapiTools.set_object_property(container, 'NormalOrShuffle', 0)
    elif play_mode == 'SequenceLocal':
        WaapiTools.set_object_property(container, 'RandomOrSequence', 0)
    elif play_mode == 'SequenceGlobal':
        WaapiTools.set_object_property(container, 'RandomOrSequence', 0)
    for item in playlist['items']:
        if item['type'] == 'single':
            import_single_sound(item, container)


# 从FMOD导入单个音效
def import_single_sound(instrument, parent):
    if not parent:
        return
    asset_path = instrument['asset']
    sound_name = asset_path.split('/')[-1][:-4]
    sound = WaapiTools.create_object(sound_name, 'Sound', parent, 'fail')
    if not sound:
        print(f'Create sound failed: {sound_name}')
        return
    asset_path = os.path.join(WaapiTools.get_project_directory(), '../Originals/SFX', asset_path)
    WaapiTools.import_audio_file(asset_path, sound, sound_name)
    WaapiTools.set_object_property(sound, 'IsLoopingEnabled', 0)
    WaapiTools.set_object_property(sound, 'Pitch', instrument['pitch'])
    WaapiTools.set_object_property(sound, 'Volume', instrument['volume'])


# 从FMOD导出的json导入Preset
def import_fmod_presets():
    state_root = WaapiTools.get_object_from_path('\\States\\Default Work Unit')
    switch_root = WaapiTools.get_object_from_path('\\Switches\\Default Work Unit')
    rtpc_root = WaapiTools.get_object_from_path('\\Game Parameters\\Default Work Unit')
    json = FileTools.import_from_json()
    for preset in json:
        preset_name = preset['name']
        preset_type = preset['type']
        if preset_type == 'Label':
            if preset['isGlobal']:
                state = WaapiTools.create_object(preset_name, 'StateGroup', state_root, 'fail')
                if state:
                    print(f'StateGroup created: {preset_name}')
                    for label in preset['labels']:
                        WaapiTools.create_object(label, 'State', state, 'fail')
            else:
                switch = WaapiTools.create_object(preset_name, 'SwitchGroup', switch_root, 'fail')
                if switch:
                    print(f'SwitchGroup created: {preset_name}')
                    for label in preset['labels']:
                        WaapiTools.create_object(label, 'Switch', switch, 'fail')
        else:
            rtpc = WaapiTools.create_object(preset_name, 'GameParameter', rtpc_root, 'fail')
            if rtpc:
                min_value = preset['minValue']
                max_value = preset['maxValue']
                WaapiTools.set_object_property(rtpc, 'InitialValue', preset['initValue'])
                WaapiTools.set_object_property(rtpc, 'Min', min_value)
                WaapiTools.set_object_property(rtpc, 'Max', max_value)
                slew_rate = preset['slewRateUp']
                if slew_rate > 0:
                    WaapiTools.set_object_property(rtpc, 'RTPCRamping', 1)
                    WaapiTools.set_object_property(rtpc, 'SlewRateUp', slew_rate)
                    WaapiTools.set_object_property(rtpc, 'SlewRateDown', preset['slewRateDown'] if 'slewRateDown' in preset else slew_rate)
                if preset_type == 'BuiltInDistance':
                    WaapiTools.set_object_property(rtpc, 'BindToBuiltInParam', 1)
                print(f'RTPC created: {preset_name} ({min_value}-{max_value})')


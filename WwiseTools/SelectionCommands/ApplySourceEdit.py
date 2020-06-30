from Libraries.SSWave import SWaveObject
import ScriptingTools

Client = None


# 将Source Editor里编辑的信息写入源文件中
def apply_source_edit(client, objects):
    global Client
    Client = client
    for obj in objects:
        obj_guid = obj['id']
        type_args = {
            'from': {
                'id': [obj_guid]
            },
            'options': {
                'return': ['type', 'path', 'sound:originalWavFilePath']
            }
        }
        # 获取所选object的类型
        type_search_result = client.call('ak.wwise.core.object.get', type_args)['return']
        object_type = type_search_result[0]['type']
        # 如果选中的就是单个音效，则直接进行处理
        if object_type == 'Sound':
            object_path = type_search_result[0]['path']
            original_path = type_search_result[0]['sound:originalWavFilePath']
            apply_modifications(object_path, original_path)
        # 如果选中的不是单个音效，则搜索里面所有的音效
        else:
            sound_search_args = {
                'from': {
                    'id': [obj_guid]
                },
                'transform': [
                    {'select': ['descendants']},
                    {'where': ['type:isIn', ['Sound']]}
                ],
                'options': {
                    'return': ['id', 'path', 'sound:originalWavFilePath']
                }
            }
            sound_search_result = client.call('ak.wwise.core.object.get', sound_search_args)['return']
            # 遍历每个找到的音效
            for sound_id in range(len(sound_search_result)):
                sound_path = sound_search_result[sound_id]['path']
                original_path = sound_search_result[sound_id]['sound:originalWavFilePath']
                apply_modifications(sound_path, original_path)


# 对所选的音效进行处理
def apply_modifications(sound_object_path, original_wave_path):
    source_editor_path = sound_object_path + '\\' + sound_object_path.split('\\')[-1]
    change_source(source_editor_path, original_wave_path)
    reset_source_editor(source_editor_path)


# 重置所有的淡入淡出和裁剪
def reset_source_editor(obj_source_path):
    reset_fade_or_trim(obj_source_path, 'FadeInDuration', 0)
    reset_fade_or_trim(obj_source_path, 'FadeOutDuration', 0)
    reset_fade_or_trim(obj_source_path, 'TrimBegin', -1)
    reset_fade_or_trim(obj_source_path, 'TrimEnd', -1)


# 设置单项Source Editor属性
def reset_fade_or_trim(obj_source_path, prop, value):
    arguments = {
        'object': obj_source_path,
        'property': prop,
        'value': value
    }
    Client.call('ak.wwise.core.object.setProperty', arguments)


# 将裁剪和淡入淡出覆盖写入源文件
def change_source(obj_source_path, original_wav_path):
    fade_info_args = {
        'from': {
            'path': [obj_source_path]
        },
        'options': {
            'return': ['@TrimBegin', '@TrimEnd', '@FadeInDuration', '@FadeOutDuration']
        }
    }
    # 获取淡入淡出和裁剪信息
    fade_info_result = Client.call('ak.wwise.core.object.get', fade_info_args)['return'][0]
    trim_begin = fade_info_result['@TrimBegin']
    fade_in_duration = fade_info_result['@FadeInDuration']
    fade_out_duration = fade_info_result['@FadeOutDuration']
    trim_end = fade_info_result['@TrimEnd']
    # 确保源文件是wav
    if original_wav_path[-4:] == '.wav':
        wave_file = SWaveObject(original_wav_path)
        song_length = wave_file.duration
        if trim_begin != -1.0:
            wave_file.audioCut(original_wav_path, trim_begin, song_length)
        if trim_end != -1.0:
            wave_file.audioCut(original_wav_path, 0, trim_end)
        if fade_in_duration > 0:
            wave_file.audioFadeIn(original_wav_path, -120.0, 0, round(fade_in_duration, 2))
        if fade_out_duration > 0:
            wave_file.audioFadeOut(original_wav_path, -120.0, song_length, fade_out_duration)



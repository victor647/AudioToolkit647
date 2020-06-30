from Libraries.SSWave import SWaveObject
from ObjectTools import WaapiTools


# 将Source Editor里编辑的信息写入源文件中
def apply_source_edit(client, obj):
    query_args = {
        'from': {
            'id': obj['id']
        },
        'options': {
            'return': ['sound:originalWavFilePath']
        }
    }
    # 获取所选object的类型
    query_result = client.call('ak.wwise.core.object.get', query_args)['return']
    change_source(client, obj, query_result['sound:originalWavFilePath'])
    reset_source_editor(client, obj)


# 重置所有的淡入淡出和裁剪
def reset_source_editor(client, sound_object):
    if sound_object['type'] != 'AudioFileSource':
        return
    WaapiTools.set_object_property(client, sound_object, 'FadeInDuration', 0)
    WaapiTools.set_object_property(client, sound_object, 'FadeOutDuration', 0)
    WaapiTools.set_object_property(client, sound_object, 'TrimBegin', -1)
    WaapiTools.set_object_property(client, sound_object, 'TrimEnd', -1)
    WaapiTools.set_object_property(client, sound_object, 'LoopBegin', -1)
    WaapiTools.set_object_property(client, sound_object, 'LoopEnd', -1)


# 将裁剪和淡入淡出覆盖写入源文件
def change_source(client, sound_object_id, original_wav_path):
    fade_info_args = {
        'from': {
            'id': sound_object_id
        },
        'options': {
            'return': ['@TrimBegin', '@TrimEnd', '@FadeInDuration', '@FadeOutDuration']
        }
    }
    # 获取淡入淡出和裁剪信息
    fade_info_result = client.call('ak.wwise.core.object.get', fade_info_args)['return']
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



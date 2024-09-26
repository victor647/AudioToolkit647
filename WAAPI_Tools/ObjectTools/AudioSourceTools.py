import os
import soundfile
from Libraries import WAAPI, AudioEditTools, FileTools, ProjectConventions, ScriptingHelper
from ObjectTools import LocalizationTools, ProjectTools


# 检测Sound是否播放样本，还是播放其他插件
def sound_play_from_plugin(sound: dict):
    children = WAAPI.get_child_objects(sound, False)
    if len(children) == 0:
        return False
    for child in children:
        if child['type'] != 'AudioFileSource':
            return True
    return False


# 获取当前Sound下面所有的AudioSource并删除
def delete_audio_sources(sound: dict):
    audio_sources = WAAPI.get_child_objects(sound, False)
    for audio_source in audio_sources:
        WAAPI.delete_object(audio_source)
    return True


# 获取音效的源文件路径
def get_source_file_path(sound_or_source: dict):
    return WAAPI.get_object_property(sound_or_source, 'sound:originalWavFilePath')


# 将Source Editor里编辑的信息写入源文件中
def apply_source_edits(source: dict):
    if source['type'] != 'AudioFileSource':
        return False
    source_path = get_source_file_path(source)
    if not source_path:
        return False
    trim_begin = WAAPI.get_object_property(source, 'TrimBegin')
    trim_end = WAAPI.get_object_property(source, 'TrimEnd')
    fade_in_duration = WAAPI.get_object_property(source, 'FadeInDuration')
    fade_out_duration = WAAPI.get_object_property(source, 'FadeOutDuration')
    sound_file = soundfile.SoundFile(file=source_path)
    sound_data = sound_file.read()
    sample_rate = sound_file.samplerate
    song_length = sound_file.duration
    if trim_begin != -1.0:
        AudioEditTools.trim(sound_data, trim_begin * sample_rate, song_length * sample_rate)
    if trim_end != -1.0:
        AudioEditTools.trim(sound_data, 0, trim_end * sample_rate)
    if fade_in_duration > 0:
        AudioEditTools.fade(sound_data, fade_in_duration * sample_rate, 1)
    if fade_out_duration > 0:
        AudioEditTools.fade(sound_data, fade_out_duration * sample_rate, -1)
    soundfile.write(file=source_path, data=sound_data, samplerate=sample_rate)
    return reset_source_editor(source)


# 重置所有的淡入淡出和裁剪
def reset_source_editor(source: dict):
    if source['type'] != 'AudioFileSource':
        return False
    WAAPI.set_object_property(source, 'FadeInDuration', 0)
    WAAPI.set_object_property(source, 'FadeOutDuration', 0)
    WAAPI.set_object_property(source, 'TrimBegin', -1)
    WAAPI.set_object_property(source, 'TrimEnd', -1)
    WAAPI.set_object_property(source, 'LoopBegin', -1)
    WAAPI.set_object_property(source, 'LoopEnd', -1)
    return True


# 替换样本文件
def replace_audio_file(sound: dict, new_wav_path: str, language: str):
    old_source = WAAPI.get_audio_source_from_sound(sound)
    if not old_source:
        return False
    fade_in = WAAPI.get_object_property(old_source, 'FadeInDuration')
    fade_out = WAAPI.get_object_property(old_source, 'FadeOutDuration')
    trim_begin = WAAPI.get_object_property(old_source, 'TrimBegin')
    trim_end = WAAPI.get_object_property(old_source, 'TrimEnd')
    loop_begin = WAAPI.get_object_property(old_source, 'LoopBegin')
    loop_end = WAAPI.get_object_property(old_source, 'LoopEnd')
    delete_audio_sources(sound)

    WAAPI.import_audio_file(new_wav_path, sound, sound['name'], language)
    new_source = WAAPI.get_audio_source_from_sound(sound)
    if not new_source:
        return False
    WAAPI.set_object_property(new_source, 'FadeInDuration', fade_in)
    WAAPI.set_object_property(new_source, 'FadeOutDuration', fade_out)
    WAAPI.set_object_property(new_source, 'TrimBegin', trim_begin)
    WAAPI.set_object_property(new_source, 'TrimEnd', trim_end)
    WAAPI.set_object_property(new_source, 'LoopBegin', loop_begin)
    WAAPI.set_object_property(new_source, 'LoopEnd', loop_end)
    return True


# 将原始资源文件名字改为Wwise中资源名字
def rename_original_to_wwise(sound: dict):
    if sound['type'] != 'Sound':
        return False
    # 去除1P和3P后缀
    sound_name = sound['name']
    suffix = ProjectConventions.get_net_role_suffix_from_name(sound_name)
    sources = WAAPI.get_child_objects(sound, False)
    for source in sources:
        language = LocalizationTools.get_sound_language(source)
        original_wave_path = get_source_file_path(sound)
        if not original_wave_path:
            print(f'AudioFile of Sound [{sound_name}] missing at [{original_wave_path}]!')
            continue
        original_wave_name = os.path.basename(original_wave_path)
        # Sound名称包含NetRole但源文件不区分
        if suffix and suffix not in original_wave_name:
            new_wave_name = sound_name[:-len(suffix)] + '.wav'
        else:
            new_wave_name = sound_name + '.wav'
        if original_wave_name != new_wave_name:
            new_wave_path = original_wave_path.replace(original_wave_name, new_wave_name)
            # 重命名源文件，若已存在则直接导入
            if os.path.exists(original_wave_path) and not os.path.exists(new_wave_path):
                os.rename(original_wave_path, new_wave_path)
            replace_audio_file(sound, new_wave_path, language)
    return True


# 按照文件夹与WorkUnit整理源文件目录
def tidy_original_folders(sound: dict):
    if sound['type'] != 'Sound':
        return False
    original_path = get_source_file_path(sound)
    file_name = os.path.basename(original_path)
    language = LocalizationTools.get_sound_language(sound)
    base_folder = ProjectTools.get_originals_folder()
    wav_sub_folder = get_wav_subfolder(sound)
    new_path = os.path.join(base_folder, language, wav_sub_folder, file_name)
    if original_path == new_path:
        return False
    FileTools.move_file(original_path, new_path)
    print(f'[{sound["name"]}] moved from [{original_path}] to [{new_path}]')
    return replace_audio_file(sound, str(new_path), language)


# 递归查找最近的Folder或WorkUnit
def get_wav_subfolder(obj: dict, path=''):
    parent = WAAPI.get_parent_object(obj)
    if not parent:
        return path[22:]
    parent_type = parent['type']
    if parent_type == 'WorkUnit' or parent_type == 'Folder':
        path = os.path.join(parent['name'], path)
    return get_wav_subfolder(parent, path)


# 清除工程中多余的akd文件
def delete_unused_akd_files():
    count = 0
    originals_folder = ProjectTools.get_originals_folder()
    for root, dirs, files in os.walk(originals_folder):
        for file in files:
            if file.endswith(".akd"):
                full_path = os.path.join(root, file)
                wave_path = full_path.replace('.akd', '.wav')
                if not os.path.exists(wave_path):
                    os.remove(full_path)
                    count += 1
    ScriptingHelper.show_message_box('删除完毕', f'共删除了{count}个akd文件！')


def add_silence(sound: dict, duration: int, language: str):
    version = ProjectTools.get_project_version()
    if version > 2021:
        return WAAPI.add_silence(sound, duration, language)
    else:
        ref_wav_path, ref_language = LocalizationTools.get_wave_path_for_any_existing_language(sound)
        if not ref_wav_path or not ref_language:
            return False
        new_wav_path = ref_wav_path.replace(ref_language, language)
        AudioEditTools.create_silence_audio_file(new_wav_path, duration)
        source = WAAPI.import_audio_file(new_wav_path, sound, sound['name'], language)
        return WAAPI.set_object_notes(source, 'Silence')

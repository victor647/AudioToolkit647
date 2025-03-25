import os
import soundfile
from Libraries import WAAPI, AudioEditTools, FileTools, ProjectConventions, ScriptingHelper
from ObjectTools import LocalizationTools, ProjectTools, CommonTools


# 检测Sound是否播放样本，还是播放其他插件
def sound_play_from_plugin(sound: dict):
    children = WAAPI.get_child_objects(sound)
    if len(children) == 0:
        return False
    for child in children:
        if child['type'] != 'AudioFileSource':
            return True
    return False


# 获取当前Sound下面指定语言的AudioSource并删除
def delete_audio_source_by_language(sound: dict, language: str):
    if sound['type'] != 'Sound':
        return
    audio_sources = WAAPI.get_child_objects(sound)
    for audio_source in audio_sources:
        source_language = LocalizationTools.get_sound_language(audio_source)
        if source_language == language:
            return WAAPI.delete_object(audio_source)
    return False


# 获取音效的源文件路径
def get_source_file_path(sound_or_source: dict):
    return WAAPI.get_object_property(sound_or_source, 'sound:originalWavFilePath')


# 获取源文件相对路径
def get_source_relative_path(sound_or_source: dict):
    full_path = get_source_file_path(sound_or_source)
    original_path = ProjectTools.get_originals_folder()
    return os.path.relpath(full_path, original_path)


# 将Source Editor里编辑的信息写入源文件中
def apply_source_edits(obj: dict):
    modified = False
    obj_type = obj['type']
    if obj_type == 'Sound':
        for child in WAAPI.get_child_objects(obj):
            modified |= apply_source_edits(child)
        return modified
    elif obj_type != 'AudioFileSource':
        return False
    source_path = get_source_file_path(obj)
    if not source_path:
        return False
    trim_begin = WAAPI.get_object_property(obj, 'TrimBegin')
    trim_end = WAAPI.get_object_property(obj, 'TrimEnd')
    fade_in_duration = WAAPI.get_object_property(obj, 'FadeInDuration')
    fade_out_duration = WAAPI.get_object_property(obj, 'FadeOutDuration')
    sound_file = soundfile.SoundFile(file=source_path)
    sound_data = sound_file.read()
    sample_rate = sound_file.samplerate
    if trim_end > 0:
        sound_data = AudioEditTools.trim(sound_data, 0, trim_end * sample_rate)
    if trim_begin > 0:
        sound_data = AudioEditTools.trim(sound_data, trim_begin * sample_rate, 0)
    if fade_in_duration > 0:
        AudioEditTools.fade(sound_data, fade_in_duration * sample_rate, 1)
    if fade_out_duration > 0:
        AudioEditTools.fade(sound_data, fade_out_duration * sample_rate, -1)
    soundfile.write(file=source_path, data=sound_data, samplerate=sample_rate)
    return reset_source_editor(obj)


# 重置所有的淡入淡出和裁剪
def reset_source_editor(obj: dict):
    modified = False
    obj_type = obj['type']
    if obj_type == 'Sound':
        for child in WAAPI.get_child_objects(obj):
            modified |= reset_source_editor(child)
        return modified
    elif obj_type != 'AudioFileSource':
        return False
    modified |= WAAPI.set_object_property(obj, 'FadeInDuration', 0)
    modified |= WAAPI.set_object_property(obj, 'FadeOutDuration', 0)
    modified |= WAAPI.set_object_property(obj, 'TrimBegin', -1)
    modified |= WAAPI.set_object_property(obj, 'TrimEnd', -1)
    modified |= WAAPI.set_object_property(obj, 'LoopBegin', -1)
    modified |= WAAPI.set_object_property(obj, 'LoopEnd', -1)
    return modified


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
    delete_audio_source_by_language(sound, language)

    if not WAAPI.import_audio_file(new_wav_path, sound, language):
        return False
    new_source = WAAPI.get_audio_source_from_sound(sound)
    if not new_source:
        return False
    WAAPI.set_object_property(new_source, 'FadeInDuration', fade_in)
    WAAPI.set_object_property(new_source, 'FadeOutDuration', fade_out)
    WAAPI.set_object_property(new_source, 'TrimBegin', trim_begin)
    WAAPI.set_object_property(new_source, 'TrimEnd', trim_end)
    WAAPI.set_object_property(new_source, 'LoopBegin', loop_begin)
    return WAAPI.set_object_property(new_source, 'LoopEnd', loop_end)


# 根据声音路径自动导入源文件
def auto_import_by_path(sound: dict):
    language = LocalizationTools.get_sound_language(sound)
    delete_audio_source_by_language(sound, language)
    base_folder = ProjectTools.get_originals_folder()
    wav_sub_folder = get_wav_subfolder(sound)
    full_name = CommonTools.get_full_name_with_acronym(sound)
    wav_path = os.path.join(base_folder, language, wav_sub_folder, full_name + '.wav')
    if os.path.exists(wav_path):
        return WAAPI.import_audio_file(str(wav_path), sound, language)
    else:
        suffix = ProjectConventions.get_net_role_suffix_from_name(full_name)
        if suffix:
            suffix_1p = ProjectConventions.get_default_net_role_suffix()
            # 如果1P找不到，则找不带1P的文件
            if suffix == suffix_1p:
                wav_path = wav_path.replace(suffix, '')
            # 如果3P找不到，则去找1P的文件
            else:
                wav_path = wav_path.replace(suffix, suffix_1p)
            if os.path.exists(wav_path):
                return WAAPI.import_audio_file(str(wav_path), sound, language)
    return False


# 将原始资源文件名字改为Wwise中资源名字
def rename_original_to_wwise(sound: dict):
    if sound['type'] != 'Sound':
        return False
    # 去除1P和3P后缀
    sound_name = sound['name']
    if '_' not in sound_name:
        sound_name = CommonTools.get_full_name_with_acronym(sound)
    suffix = ProjectConventions.get_net_role_suffix_from_name(sound_name)
    sources = WAAPI.get_child_objects(sound)
    modified = False
    for source in sources:
        language = LocalizationTools.get_sound_language(source)
        original_wave_path = get_source_file_path(source)
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
            # 重命名源文件，若已存在则覆盖
            if os.path.exists(original_wave_path):
                os.replace(original_wave_path, new_wave_path)
            if os.path.exists(new_wave_path):
                modified = replace_audio_file(sound, new_wave_path, language)
    return modified


# 按照文件夹与WorkUnit整理源文件目录
def tidy_original_folders(sound: dict):
    if sound['type'] != 'Sound':
        return False
    original_path = get_source_file_path(sound)
    if not original_path:
        return False
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
    parent_type = parent['type']
    if parent_type == 'WorkUnit' or parent_type == 'Folder':
        parent_name = parent['name']
        if parent_name == 'Actor-Mixer Hierarchy':
            return path
        if parent_name not in path:
            path = os.path.join(parent_name, path)
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


# 为语音添加临时的静音
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
        source = WAAPI.import_audio_file(new_wav_path, sound, language)
        return WAAPI.set_object_notes(source, 'Silence')

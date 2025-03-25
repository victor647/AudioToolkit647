from Libraries import WAAPI
from ObjectTools import AudioSourceTools


# 获取音频源文件语言
def get_sound_language(source: dict):
    source_type = source['type']
    if source_type != 'AudioFileSource' and source_type != 'Sound':
        return 'SFX'
    language = WAAPI.get_object_property(source, 'audioSource:language')
    if language is None:
        return 'SFX'
    return language['name']


# 获取默认语言
def get_default_language():
    return WAAPI.get_project_property('DefaultLanguage')


# 获取当前语言
def get_current_language():
    language_id = WAAPI.get_project_info('currentLanguageId')
    language = WAAPI.get_full_info_from_obj_id(language_id)
    return language['name'] if language else get_default_language()


# 获取全部语言名称
def get_all_language_names():
    language_names = []
    language_list = WAAPI.get_language_list()
    for language in language_list:
        name = language['name']
        if name != 'SFX' and name != 'External' and name != 'Mixed':
            language_names.append(name)
    return language_names


# 获取语音对象下某个语言的样本路径
def get_wave_path_for_language(sound: dict, language:str):
    sources = WAAPI.get_child_objects(sound)
    for source in sources:
        if source['type'] == 'AudioFileSource':
            source_langauge = get_sound_language(source)
            if source_langauge == language:
                return AudioSourceTools.get_source_file_path(source)
    return None


# 获取已有语言的源文件路径
def get_wave_path_for_any_existing_language(sound: dict):
    sources = WAAPI.get_child_objects(sound)
    for source in sources:
        source_path = AudioSourceTools.get_source_file_path(source)
        if source_path:
            language = get_sound_language(source)
            return source_path, language
    return None, None


# 尝试导入当前所有语音资源的本地化文件
def localize_languages(sound: dict):
    if sound['type'] != 'Sound':
        return False
    sources = WAAPI.get_child_objects(sound)
    if len(sources) == 0:
        return False
    existing_wav_path, existing_language = get_wave_path_for_any_existing_language(sound)
    imported = False
    for language in get_all_language_names():
        if language != existing_language:
            new_wav_path = existing_wav_path.replace(existing_language, language)
            source = WAAPI.import_audio_file(new_wav_path, sound, language)
            if source is not None:
                imported = True
    return imported


# 为语音对象的参考语言创建静音
def import_silence_for_ref_language(sound):
    if sound['type'] != 'Sound':
        return False
    ref_language = get_default_language()
    source_path = get_wave_path_for_language(sound, ref_language)
    if not source_path:
        return AudioSourceTools.add_silence(sound, 2, ref_language)
    return False


# 为语音对象的所有未导入语言创建静音
def import_silence_for_all_languages(sound):
    if sound['type'] != 'Sound':
        return False
    added = False
    for language in get_all_language_names():
        source_path = get_wave_path_for_language(sound, language)
        if not source_path:
            added |= AudioSourceTools.add_silence(sound, 2, language)
    return added

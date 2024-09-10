import os.path

from Libraries import WaapiTools, ScriptingTools


# 获取音频源文件语言
def get_sound_language(sound: dict):
    language = WaapiTools.get_object_property(sound, 'audioSource:language')
    if language is None:
        return 'SFX'
    return language['name']


# 检测音效是否丢失或缺失中英文中的某个语言
def sound_missing_or_not_localized(sound: dict):
    if get_sound_language(sound) == 'SFX':
        path = WaapiTools.get_object_property(sound, 'sound:originalWavFilePath')
        if not path:
            return True
        return not os.path.exists(path)
    else:
        children = WaapiTools.get_child_objects(sound, False)
        missing_languages = 2
        for child in children:
            language = get_sound_language(child)
            if 'Chinese' in language or 'English' in language:
                missing_languages -= 1
        return missing_languages > 0


# 尝试导入当前所有语音资源的本地化文件
def localize_languages(sound: dict):
    ScriptingTools.iterate_child_sound_objects(sound, localize_language)


# 对单个音效导入本地化资源
def localize_language(sound: dict):
    language_list = WaapiTools.get_language_list()
    sources = WaapiTools.get_child_objects(sound, False)
    if len(sources) == 0:
        return

    existing_language = ''
    existing_source = None
    for source in sources:
        existing_language = get_sound_language(source)
        existing_source = source
        break

    for language_obj in language_list:
        language = language_obj['name']
        if language != existing_language:
            original_file_path = WaapiTools.get_object_property(existing_source, 'sound:originalWavFilePath')
            WaapiTools.import_audio_file(original_file_path.replace(existing_language, language), sound, sound['name'],
                                         language)


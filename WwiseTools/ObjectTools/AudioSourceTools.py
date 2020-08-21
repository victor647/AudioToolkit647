from Libraries.SSWave import SWaveObject
from Libraries import WaapiTools, ScriptingTools
from QtDesign.ReplaceSourceFile_ui import Ui_ReplaceSourceFile
from PyQt5.QtWidgets import QDialog
import os


# 重命名替换音频源文件
class ReplaceSourceFile(QDialog, Ui_ReplaceSourceFile):

    def __init__(self, sound_objects):
        super().__init__()
        self.setupUi(self)
        self.soundObjects = sound_objects
        self.setup_triggers()

    def setup_triggers(self):
        self.btnDoReplace.clicked.connect(self.replace_source_files)

    def replace_source_files(self):
        old_name = self.iptFindName.text()
        new_name = self.iptReplaceName.text()
        for obj in self.soundObjects:
            if obj['type'] != 'Sound':
                continue
            original_path = WaapiTools.get_original_wave_path(obj)
            new_wave_path = original_path.replace(old_name, new_name)
            delete_audio_sources(obj)
            # 重命名声音文件
            new_sound_name = obj['name'].replace(old_name, new_name)
            WaapiTools.rename_object(obj, new_sound_name)
            WaapiTools.import_audio_file(new_wave_path, obj, new_sound_name)


# 获取当前Sound下面所有的AudioSource并删除
def delete_audio_sources(obj):
    audio_sources = WaapiTools.get_children_objects(obj, False)
    for audio_source in audio_sources:
        WaapiTools.delete_object(audio_source)


# 将Source Editor里编辑的信息写入源文件中
def apply_source_edit(obj):
    query_args = {
        'from': {
            'id': obj['id']
        },
        'options': {
            'return': ['sound:originalWavFilePath']
        }
    }
    # 获取所选object的类型
    query_result = WaapiTools.Client.call('ak.wwise.core.object.get', query_args)['return']
    change_source(obj, query_result['sound:originalWavFilePath'])
    reset_source_editor(obj)


# 重置所有的淡入淡出和裁剪
def reset_source_editor(sound_object):
    if sound_object['type'] != 'AudioFileSource':
        return
    WaapiTools.set_object_property(sound_object, 'FadeInDuration', 0)
    WaapiTools.set_object_property(sound_object, 'FadeOutDuration', 0)
    WaapiTools.set_object_property(sound_object, 'TrimBegin', -1)
    WaapiTools.set_object_property(sound_object, 'TrimEnd', -1)
    WaapiTools.set_object_property(sound_object, 'LoopBegin', -1)
    WaapiTools.set_object_property(sound_object, 'LoopEnd', -1)


# 将裁剪和淡入淡出覆盖写入源文件
def change_source(sound_object_id, original_wav_path):
    fade_info_args = {
        'from': {
            'id': sound_object_id
        },
        'options': {
            'return': ['@TrimBegin', '@TrimEnd', '@FadeInDuration', '@FadeOutDuration']
        }
    }
    # 获取淡入淡出和裁剪信息
    fade_info_result = WaapiTools.Client.call('ak.wwise.core.object.get', fade_info_args)['return']
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


# 将原始资源文件名字改为Wwise中资源名字
def rename_original_to_wwise(obj):
    if obj['type'] != 'Sound':
        return

    original_wave_path = WaapiTools.get_original_wave_path(obj)
    new_wave_name = obj['name'] + '.wav'

    if original_wave_path != '':
        original_wave_name = os.path.basename(original_wave_path)
        # 同名不用修改
        if original_wave_name == new_wave_name:
            return
        new_wave_path = original_wave_path.replace(original_wave_name, new_wave_name)
        # 重命名源文件
        if not os.path.exists(new_wave_path):
            os.rename(original_wave_path, new_wave_path)
        # 删除旧资源
        delete_audio_sources(obj)
    # 找不到源文件，直接导入新的
    else:
        new_wave_path = os.path.join(ScriptingTools.get_originals_folder(), WaapiTools.get_sound_language(obj), new_wave_name)
    # 导入新资源
    WaapiTools.import_audio_file(new_wave_path, obj, obj['name'])


# 清除工程中多余的akd文件
def delete_unused_akd_files():
    originals_folder = ScriptingTools.get_originals_folder()
    for root, dirs, files in os.walk(originals_folder):
        for file in files:
            if file.endswith(".akd"):
                full_path = os.path.join(root, file)
                wave_path = full_path.replace('.akd', '.wav')
                if not os.path.exists(wave_path):
                    os.remove(full_path)
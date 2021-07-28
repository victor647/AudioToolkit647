import os
import soundfile
from Libraries.SSWave import SWaveObject
from Libraries import WaapiTools, ScriptingTools, AudioEditTools
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem, QHeaderView
from QtDesign.AudioTailTrimmer_ui import Ui_AudioTailTrimmer
from Threading.BatchProcessor import BatchProcessor


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
    language = WaapiTools.get_sound_language(obj)
    # 当前不包含源文件，直接根据名称导入
    if language == '':
        if 'SFX' in original_wave_path:
            language = 'SFX'
        else:
            language = WaapiTools.get_default_language()

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
        if language != 'SFX':
            language = os.path.join('Voice', language)
        new_wave_path = os.path.join(ScriptingTools.get_originals_folder(), language, new_wave_name)
    # 导入新资源
    WaapiTools.import_audio_file(new_wave_path, obj, obj['name'], language)


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


# 裁剪音频文件尾巴的工具
class AudioTailTrimmer(QDialog, Ui_AudioTailTrimmer):

    def __init__(self, active_objects: list):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__thresholdLinear = 0
        self.__currentRow = 0
        self.__fadeDuration = 0
        self.__batchProcessor = None
        self.__soundFiles = []
        # 主窗口中有wwise对象，从中查找音频源文件
        if len(active_objects) > 0 and WaapiTools.Client:
            self.populate_from_wwise(active_objects)
        self.tblFileList.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def setup_triggers(self):
        self.btnImportFiles.clicked.connect(self.import_files)
        self.btnAnalyzeTails.clicked.connect(self.analyze_tails)
        self.btnStartTrim.clicked.connect(self.start_trimming)
        self.tblFileList.viewport().installEventFilter(self)

    # 从外界拖动文件到窗口中
    def eventFilter(self, source, event):
        if event.type() == QEvent.DragEnter:
            self.reset()
            for url in event.mimeData().urls():
                self.add_file(url.toLocalFile())
            return True
        return super().eventFilter(source, event)

    # 重置所有
    def reset(self):
        for sound_file in self.__soundFiles:
            sound_file.close()
        self.__soundFiles = []
        self.__batchProcessor = None
        self.tblFileList.setRowCount(0)

    # 根据主窗口的对象寻找音频文件
    def populate_from_wwise(self, objects: list):
        for obj in objects:
            if obj['type'] == 'Sound':
                self.add_file(WaapiTools.get_original_wave_path(obj))
            else:
                self.populate_from_wwise(WaapiTools.get_children_objects(obj, False))

    # 导入音频文件
    def import_files(self):
        self.reset()
        files = QFileDialog.getOpenFileNames(filter='WAV(*.wav)')
        file_count = len(files[0])
        if file_count == 0:
            return
        for file_path in files[0]:
            self.add_file(file_path)
        self.tblFileList.repaint()

    # 添加单个文件回调
    def add_file(self, file_path: str):
        # only accept wav files
        if not file_path.endswith('.wav'):
            return
        # update row count
        row = self.tblFileList.rowCount()
        self.tblFileList.setRowCount(row + 1)
        # get audio info
        sound_file = soundfile.SoundFile(file=file_path)
        self.__soundFiles.append(sound_file)
        # print to table
        self.tblFileList.setItem(row, 0, QTableWidgetItem(os.path.basename(file_path)))

    # 分析音尾时长
    def analyze_tails(self):
        self.__currentRow = 0
        self.__thresholdLinear = AudioEditTools.decibel_to_linear(self.spbCutThreshold.value())
        self.__batchProcessor = BatchProcessor(self.__soundFiles, self.analyze_file)
        self.__batchProcessor.start()

    # 分析单个音频文件回调
    def analyze_file(self, sound_file):
        sound_file.seek(0)
        audio_data = sound_file.read()
        # calculate total duration
        duration = round(sound_file.frames / sound_file.samplerate * 1.0, 3)
        self.tblFileList.setItem(self.__currentRow, 1, QTableWidgetItem(str(duration)))
        # calculate silence duration
        silence_frames = AudioEditTools.get_tail_silence_duration_frames(audio_data, 256, self.__thresholdLinear)
        silence_duration = round(silence_frames * 256 / sound_file.samplerate * 1.0, 3)
        self.tblFileList.setItem(self.__currentRow, 2, QTableWidgetItem(str(silence_duration)))
        if silence_duration > self.spbFadeDuration.value():
            status_item = QTableWidgetItem('可裁剪')
            status_item.setForeground(QColor(200, 0, 0))
        else:
            status_item = QTableWidgetItem('无需裁剪')
        self.tblFileList.setItem(self.__currentRow, 3, status_item)
        self.__currentRow += 1

    # 开始裁剪
    def start_trimming(self):
        self.__currentRow = 0
        self.__fadeDuration = self.spbFadeDuration.value()
        processor = BatchProcessor(self.__soundFiles, self.trim_file)
        processor.start()

    # 裁剪单个音频文件回调
    def trim_file(self, sound_file):
        silence_duration = float(self.tblFileList.item(self.__currentRow, 2).text())
        if silence_duration > self.__fadeDuration:
            sound_file.seek(0)
            audio_data = sound_file.read()
            trim_samples = int((silence_duration - self.__fadeDuration) * sound_file.samplerate)
            # 进行裁剪
            audio_data = audio_data[:len(audio_data) - trim_samples]
            # 把保留的静音时长做个淡出
            AudioEditTools.apply_fade(audio_data, int(self.__fadeDuration * sound_file.samplerate), -1)
            soundfile.write(file=sound_file.name, data=audio_data, samplerate=sound_file.samplerate)
            # 更新列表显示
            self.tblFileList.setItem(self.__currentRow, 2, QTableWidgetItem(str(self.__fadeDuration)))
            status_item = QTableWidgetItem('已裁剪')
            status_item.setForeground(QColor(0, 200, 0))
            self.tblFileList.setItem(self.__currentRow, 3, status_item)
        self.__currentRow += 1

    def closeEvent(self, close_event):
        self.reset()
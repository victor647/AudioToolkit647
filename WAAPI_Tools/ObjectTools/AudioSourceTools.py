import os
import soundfile
from Libraries import WaapiTools, ScriptingTools, AudioEditTools, FileTools
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QDialog, QFileDialog, QTableWidgetItem, QHeaderView
from QtDesign.AudioTailTrimmer_ui import Ui_AudioTailTrimmer
from Threading.BatchProcessor import BatchProcessor


# 获取当前Sound下面所有的AudioSource并删除
def delete_audio_sources(obj):
    audio_sources = WaapiTools.get_child_objects(obj, False)
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


# 将源文件编辑信息缓存
def backup_source_edits(sound_object):
    if sound_object['type'] != 'AudioFileSource':
        return
    data = [WaapiTools.get_object_property(sound_object, 'FadeInDuration'),
            WaapiTools.get_object_property(sound_object, 'FadeOutDuration'),
            WaapiTools.get_object_property(sound_object, 'TrimBegin'),
            WaapiTools.get_object_property(sound_object, 'TrimEnd'),
            WaapiTools.get_object_property(sound_object, 'LoopBegin'),
            WaapiTools.get_object_property(sound_object, 'LoopEnd')]
    return data


# 恢复缓存的源文件编辑信息
def restore_source_edits(sound_object, data: list):
    if sound_object['type'] != 'AudioFileSource':
        return
    WaapiTools.set_object_property(sound_object, 'FadeInDuration', data[0])
    WaapiTools.set_object_property(sound_object, 'FadeOutDuration', data[1])
    WaapiTools.set_object_property(sound_object, 'TrimBegin', data[2])
    WaapiTools.set_object_property(sound_object, 'TrimEnd', data[3])
    WaapiTools.set_object_property(sound_object, 'LoopBegin', data[4])
    WaapiTools.set_object_property(sound_object, 'LoopEnd', data[5])


# 将裁剪和淡入淡出覆盖写入源文件
def change_source(sound_object_id, original_wav_path):
    fade_info_args = {
        'from': {
            'id': sound_object_id
        },
        'options': {
            'return': ['TrimBegin', 'TrimEnd', 'FadeInDuration', 'FadeOutDuration']
        }
    }
    # 获取淡入淡出和裁剪信息
    fade_info_result = WaapiTools.Client.call('ak.wwise.core.object.get', fade_info_args)['return']
    trim_begin = fade_info_result['TrimBegin']
    fade_in_duration = fade_info_result['FadeInDuration']
    fade_out_duration = fade_info_result['FadeOutDuration']
    trim_end = fade_info_result['TrimEnd']
    sound_file = soundfile.SoundFile(file=original_wav_path)
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
    soundfile.write(file=original_wav_path.name, data=sound_data, samplerate=sample_rate)


# 替换样本文件
def replace_audio_file(sound_obj, new_wav_path, language):
    data = backup_source_edits(WaapiTools.get_audio_source_from_sound(sound_obj))
    delete_audio_sources(sound_obj)

    WaapiTools.import_audio_file(new_wav_path, sound_obj, sound_obj['name'], language)
    restore_source_edits(WaapiTools.get_audio_source_from_sound(sound_obj), data)


# 将原始资源文件名字改为Wwise中资源名字
def rename_original_to_wwise(obj):
    if obj['type'] != 'Sound':
        return

    original_wave_path = WaapiTools.get_object_property(obj, 'sound:originalWavFilePath')
    if original_wave_path is None:
        return

    new_wave_name = obj['name'] + '.wav'
    language = WaapiTools.get_sound_language(obj)
    original_wave_name = os.path.basename(original_wave_path)
    if original_wave_name != new_wave_name:
        new_wave_path = original_wave_path.replace(original_wave_name, new_wave_name)
        # 重命名源文件，若已存在则直接导入
        if not os.path.exists(new_wave_path):
            os.rename(original_wave_path, new_wave_path)
        replace_audio_file(obj, new_wave_path, language)


# 按照文件夹与WorkUnit整理源文件目录
def tidy_original_folders(obj):
    # 仅对ActorMixerHierarchy下的资源生效
    if not obj['path'].startswith('\\Actor-Mixer Hierarchy\\'):
        return
    obj_type = obj['type']
    children = WaapiTools.get_child_objects(obj, False)
    if obj_type == 'WorkUnit' or obj_type == 'Folder':
        # 递归查找所有文件夹与WorkUnit
        for child in children:
            tidy_original_folders(child)
    else:
        wav_sub_folder = get_wav_subfolder(obj)
        result_msg = tidy_children(obj, wav_sub_folder)
        return result_msg


# 找到所有Sound层级并整理audioFileSource
def tidy_children(obj, wav_sub_folder):
    result_msg = []
    base_folder = os.path.abspath(os.path.join(WaapiTools.get_project_directory(), '../Originals/'))
    children = WaapiTools.get_child_objects(obj, False)
    for child in children:
        if child['type'] == 'Sound':
            original_path = WaapiTools.get_object_property(child, 'sound:originalWavFilePath')
            file_name = os.path.basename(original_path)
            language = WaapiTools.get_sound_language(child)
            # 按照文件夹和WorkUnit得到新的样本路径
            new_path = os.path.join(base_folder, language, wav_sub_folder, file_name)
            if original_path != new_path:
                FileTools.move_file(original_path, new_path)
                replace_audio_file(child, new_path, language)
                result_msg.append(f'{child["name"]} from {original_path} -> {new_path}')
        # 递归查找下级所有对象
        elif child['type'] != 'AudioFileSource':
            tidy_children(child, wav_sub_folder)
    return result_msg


# 递归查找最近的Folder或WorkUnit
def get_wav_subfolder(obj, path=''):
    parent = WaapiTools.get_parent_objects(obj, False)
    if not parent:
        return path[22:]
    parent_type = parent['type']
    if parent_type == 'WorkUnit' or parent_type == 'Folder':
        path = os.path.join(parent['name'], path)
    return get_wav_subfolder(parent, path)


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


# 尝试导入当前所有语音资源的本地化文件
def localize_languages(obj):
    ScriptingTools.iterate_child_sound_objects(obj, localize_language)


# 对单个音效导入本地化资源
def localize_language(obj):
    language_list = WaapiTools.get_language_list()
    sources = WaapiTools.get_child_objects(obj, False)
    if len(sources) == 0:
        return

    existing_language = ''
    existing_source = None
    for source in sources:
        existing_language = WaapiTools.get_sound_language(source)
        existing_source = source
        break

    for language_obj in language_list:
        language = language_obj['name']
        if language != existing_language:
            original_file_path = WaapiTools.get_object_property(existing_source, 'sound:originalWavFilePath')
            WaapiTools.import_audio_file(original_file_path.replace(existing_language, language), obj, obj['name'],
                                         language)


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
        self.btnImportFolder.clicked.connect(self.import_folder)
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
                self.add_file(WaapiTools.get_object_property(obj, 'sound:originalWavFilePath'))
            else:
                self.populate_from_wwise(WaapiTools.get_child_objects(obj, False))

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

    # 导入文件夹中所有音频文件
    def import_folder(self):
        self.reset()
        folder = QFileDialog.getExistingDirectory()
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".wav"):
                    file_path = os.path.join(root, file)
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
        self.__batchProcessor = BatchProcessor(self.__soundFiles, self.analyze_file, '分析音频时长')
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
        processor = BatchProcessor(self.__soundFiles, self.trim_file, '裁剪音频末尾')
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
            AudioEditTools.fade(audio_data, int(self.__fadeDuration * sound_file.samplerate), -1)
            soundfile.write(file=sound_file.name, data=audio_data, samplerate=sound_file.samplerate)
            # 更新列表显示
            self.tblFileList.setItem(self.__currentRow, 2, QTableWidgetItem(str(self.__fadeDuration)))
            status_item = QTableWidgetItem('已裁剪')
            status_item.setForeground(QColor(0, 200, 0))
            self.tblFileList.setItem(self.__currentRow, 3, status_item)
        self.__currentRow += 1

    def closeEvent(self, close_event):
        self.reset()

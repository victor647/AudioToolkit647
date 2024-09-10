import os
import soundfile
from Libraries import WaapiTools, ScriptingTools, AudioEditTools, FileTools
from ObjectTools import LocalizationTools
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDialog, QFileDialog, QTableWidgetItem
from QtDesign.AudioTailTrimmer_ui import Ui_AudioTailTrimmer
from Threading.BatchProcessor import BatchProcessor


# 检查样本的裁剪末尾是否超出时长范围
def trim_out_of_range(audio_source: dict):
    trim_end = WaapiTools.get_object_property(audio_source, 'TrimEnd')
    if trim_end == -1:
        return False
    duration = WaapiTools.get_object_property(audio_source, 'playbackDuration')
    if duration:
        return trim_end > duration['playbackDurationMax']
    return False


# 检查源文件是否与Sound命名一致
def is_source_path_inconsistent(sound: dict):
    sound_name = sound['name']
    if sound_name.endswith('_1P') or sound_name.endswith('_3P'):
        sound_name = sound_name[:-3]
    elif sound_name.endswith('_3P_Enemy'):
        sound_name = sound_name[:-9]

    children = WaapiTools.get_child_objects(sound, False)
    for audio_source in children:
        source_path = WaapiTools.get_object_property(audio_source, 'sound:originalWavFilePath')
        if source_path:
            source_name = os.path.basename(source_path)[:-4]
            if sound_name != source_name:
                return True
    return False


# 获取当前Sound下面所有的AudioSource并删除
def delete_audio_sources(sound: dict):
    audio_sources = WaapiTools.get_child_objects(sound, False)
    for audio_source in audio_sources:
        WaapiTools.delete_object(audio_source)


# 将Source Editor里编辑的信息写入源文件中
def apply_source_edit(audio_source: dict):
    query_args = {
        'from': {
            'id': audio_source['id']
        },
        'options': {
            'return': ['sound:originalWavFilePath']
        }
    }
    # 获取所选object的类型
    query_result = WaapiTools.Client.call('ak.wwise.core.object.get', query_args)['return']
    change_source(audio_source, query_result['sound:originalWavFilePath'])
    reset_source_editor(audio_source)


# 重置所有的淡入淡出和裁剪
def reset_source_editor(audio_source: dict):
    if audio_source['type'] != 'AudioFileSource':
        return
    WaapiTools.set_object_property(audio_source, 'FadeInDuration', 0)
    WaapiTools.set_object_property(audio_source, 'FadeOutDuration', 0)
    WaapiTools.set_object_property(audio_source, 'TrimBegin', -1)
    WaapiTools.set_object_property(audio_source, 'TrimEnd', -1)
    WaapiTools.set_object_property(audio_source, 'LoopBegin', -1)
    WaapiTools.set_object_property(audio_source, 'LoopEnd', -1)


# 将源文件编辑信息缓存
def backup_source_edits(audio_source: dict):
    if audio_source['type'] != 'AudioFileSource':
        return
    data = [WaapiTools.get_object_property(audio_source, 'FadeInDuration'),
            WaapiTools.get_object_property(audio_source, 'FadeOutDuration'),
            WaapiTools.get_object_property(audio_source, 'TrimBegin'),
            WaapiTools.get_object_property(audio_source, 'TrimEnd'),
            WaapiTools.get_object_property(audio_source, 'LoopBegin'),
            WaapiTools.get_object_property(audio_source, 'LoopEnd')]
    return data


# 恢复缓存的源文件编辑信息
def restore_source_edits(audio_source: dict, data: list):
    if audio_source['type'] != 'AudioFileSource':
        return
    WaapiTools.set_object_property(audio_source, 'FadeInDuration', data[0])
    WaapiTools.set_object_property(audio_source, 'FadeOutDuration', data[1])
    WaapiTools.set_object_property(audio_source, 'TrimBegin', data[2])
    WaapiTools.set_object_property(audio_source, 'TrimEnd', data[3])
    WaapiTools.set_object_property(audio_source, 'LoopBegin', data[4])
    WaapiTools.set_object_property(audio_source, 'LoopEnd', data[5])


# 将裁剪和淡入淡出覆盖写入源文件
def change_source(audio_source: dict, original_wav_path: str):
    fade_info_args = {
        'from': {
            'id': audio_source['id']
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
    soundfile.write(file=original_wav_path, data=sound_data, samplerate=sample_rate)


# 替换样本文件
def replace_audio_file(sound: dict, new_wav_path: str, language: str):
    data = backup_source_edits(WaapiTools.get_audio_source_from_sound(sound))
    delete_audio_sources(sound)

    WaapiTools.import_audio_file(new_wav_path, sound, sound['name'], language)
    audio_file = WaapiTools.get_audio_source_from_sound(sound)
    if audio_file:
        restore_source_edits(WaapiTools.get_audio_source_from_sound(sound), data)


# 将原始资源文件名字改为Wwise中资源名字
def rename_original_to_wwise(sound: dict):
    if sound['type'] != 'Sound':
        return

    # 去除1P和3P后缀
    sound_name = sound['name']
    if sound_name.endswith('_1P') or sound_name.endswith('_3P'):
        sound_name = sound_name[:-3]
    elif sound_name.endswith('_3P_Enemy'):
        sound_name = sound_name[:-9]
    new_wave_name = sound_name + '.wav'

    children = WaapiTools.get_child_objects(sound, False)
    for audio_source in children:
        language = LocalizationTools.get_sound_language(audio_source)
        original_wave_path = WaapiTools.get_object_property(sound, 'sound:originalWavFilePath')
        if not original_wave_path:
            print(f'AudioFile of Sound [{sound_name}] missing at [{original_wave_path}]!')
            continue
        original_wave_name = os.path.basename(original_wave_path)
        if original_wave_name != new_wave_name:
            new_wave_path = original_wave_path.replace(original_wave_name, new_wave_name)
            # 重命名源文件，若已存在则直接导入
            if os.path.exists(original_wave_path) and not os.path.exists(new_wave_path):
                os.rename(original_wave_path, new_wave_path)
            replace_audio_file(sound, new_wave_path, language)








# 按照文件夹与WorkUnit整理源文件目录
def tidy_original_folders(obj: dict):
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
def tidy_children(obj: dict, wav_sub_folder: str):
    result_msg = []
    base_folder = os.path.abspath(os.path.join(WaapiTools.get_project_directory(), '../Originals/'))
    children = WaapiTools.get_child_objects(obj, False)
    for child in children:
        if child['type'] == 'Sound':
            original_path = WaapiTools.get_object_property(child, 'sound:originalWavFilePath')
            file_name = os.path.basename(original_path)
            language = LocalizationTools.get_sound_language(child)
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
def get_wav_subfolder(obj: dict, path=''):
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


# 检查样本是否是静音替代资源
def is_audio_source_silent(obj: dict):
    children = WaapiTools.get_child_objects(obj, False)
    for child in children:
        if child['type'] == 'AudioFileSource':
            path = WaapiTools.get_object_property(child, 'sound:originalWavFilePath')
            silent = AudioEditTools.is_sound_completely_silent(path)
            if silent:
                return True
    return False


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
        self.tblFileList.resizeColumnsToContents()

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
                    file_path = str(os.path.join(root, file))
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

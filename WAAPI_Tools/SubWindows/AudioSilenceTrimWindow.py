import os
import logging
import soundfile
from Libraries import WAAPI, AudioEditTools
from ObjectTools import AudioSourceTools
from PyQt6.QtGui import QColor, QDragEnterEvent
from PyQt6.QtWidgets import QDialog, QFileDialog, QTableWidgetItem
from QtDesign.AudioSilenceTrimmer_ui import Ui_AudioSilenceTrimmer
from Threading.BatchProcessor import BatchProcessor

Sound_Frame_Samples = 128


# 裁剪音频文件尾巴的工具
class AudioSilenceTrimWindow(QDialog, Ui_AudioSilenceTrimmer):

    def __init__(self, active_objects: list):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__thresholdLinear = 0
        self.__currentRow = 0
        self.__fadeInSeconds = 0
        self.__fadeOutSeconds = 0
        self.__batchProcessor = None
        self.__filePaths = []
        # 主窗口中有wwise对象，从中查找音频源文件
        if len(active_objects) > 0 and WAAPI.Client:
            self.populate_from_wwise(active_objects)
        self.tblFileList.resizeColumnsToContents()

    def setup_triggers(self):
        self.btnImportFiles.clicked.connect(self.import_files)
        self.btnImportFolder.clicked.connect(self.import_folder)
        self.btnAnalyzeAudio.clicked.connect(self.analyze_audio)
        self.btnStartTrimming.clicked.connect(self.start_trimming)
        self.tblFileList.viewport().installEventFilter(self)

    # 更新淡入淡出时间和静音阈值
    def update_settings(self):
        self.__fadeInSeconds = self.spbFadeInDuration.value() / 1000
        self.__fadeOutSeconds = self.spbFadeOutDuration.value() / 1000
        self.__thresholdLinear = AudioEditTools.decibel_to_linear(self.spbCutThreshold.value())

    # 从外界拖动文件到窗口中
    def eventFilter(self, source, event):
        if event.type() == QDragEnterEvent:
            self.reset()
            for url in event.mimeData().urls():
                self.add_file(url.toLocalFile())
            return True
        return super().eventFilter(source, event)

    # 重置所有
    def reset(self):
        self.__filePaths = []
        self.__batchProcessor = None
        self.tblFileList.setRowCount(0)

    # 根据主窗口的对象寻找音频文件
    def populate_from_wwise(self, objects: list):
        for obj in objects:
            if obj['type'] == 'AudioFileSource':
                self.add_file(AudioSourceTools.get_source_file_path(obj))
            else:
                self.populate_from_wwise(WAAPI.get_child_objects(obj))

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
        if not os.path.exists(file_path):
            logging.error(f'{file_path} does not exist!')
            return
        if not file_path.endswith('.wav'):
            return
        # 不要重复裁剪同一个文件
        if file_path in self.__filePaths:
            return
        row = self.tblFileList.rowCount()
        self.tblFileList.setRowCount(row + 1)
        self.__filePaths.append(file_path)
        self.tblFileList.setItem(row, 0, QTableWidgetItem(os.path.basename(file_path)))

    # 分析音尾时长
    def analyze_audio(self):
        self.__currentRow = 0
        self.update_settings()
        self.__batchProcessor = BatchProcessor(self.__filePaths, self.analyze_file, '分析音频时长')
        self.__batchProcessor.start()

    # 分析单个音频文件
    def analyze_file(self, file_path):
        sound_file = soundfile.SoundFile(file_path)
        audio_data = sound_file.read()
        # 计算音频长度
        duration = round(sound_file.frames / sound_file.samplerate * 1.0, 3)
        self.tblFileList.setItem(self.__currentRow, 1, QTableWidgetItem(str(duration)))
        if AudioEditTools.get_sound_frame_max_amp(audio_data) == 0:
            status_item = QTableWidgetItem('完全静音')
            status_item.setForeground(QColor(0, 0, 200))
            self.tblFileList.setItem(self.__currentRow, 2, QTableWidgetItem(str(duration)))
            self.tblFileList.setItem(self.__currentRow, 3, QTableWidgetItem(str(duration)))
        else:
            # 计算静音长度
            silence_frames_head = AudioEditTools.get_silence_duration_frames(audio_data, Sound_Frame_Samples, self.__thresholdLinear, False)
            silence_duration_head = round(silence_frames_head * Sound_Frame_Samples / sound_file.samplerate * 1.0, 3)
            self.tblFileList.setItem(self.__currentRow, 2, QTableWidgetItem(str(silence_duration_head)))
            silence_frames_tail = AudioEditTools.get_silence_duration_frames(audio_data, Sound_Frame_Samples, self.__thresholdLinear, True)
            silence_duration_tail = round(silence_frames_tail * Sound_Frame_Samples / sound_file.samplerate * 1.0, 3)
            self.tblFileList.setItem(self.__currentRow, 3, QTableWidgetItem(str(silence_duration_tail)))
            # 静音长度阈值
            if silence_duration_head > self.__fadeInSeconds or silence_duration_tail > self.__fadeOutSeconds:
                status_item = QTableWidgetItem('可裁剪')
                status_item.setForeground(QColor(200, 0, 0))
            else:
                status_item = QTableWidgetItem('无需裁剪')
        sound_file.close()
        self.tblFileList.setItem(self.__currentRow, 4, status_item)
        self.__currentRow += 1

    # 开始裁剪
    def start_trimming(self):
        self.__currentRow = 0
        self.update_settings()
        processor = BatchProcessor(self.__filePaths, self.trim_file, '裁剪音频末尾')
        processor.start()

    # 裁剪单个音频文件回调
    def trim_file(self, file_path):
        if self.tblFileList.item(self.__currentRow, 4).text() == '完全静音':
            return
        silence_duration_head = float(self.tblFileList.item(self.__currentRow, 2).text())
        silence_duration_tail = float(self.tblFileList.item(self.__currentRow, 3).text())
        # 计算需要剪掉的采样点数量
        trim_head = silence_duration_head > self.__fadeInSeconds and self.cbxTrimHead.isChecked()
        trim_tail = silence_duration_tail > self.__fadeOutSeconds and self.cbxTrimTail.isChecked()
        sound_file = soundfile.SoundFile(file_path)
        audio_data = sound_file.read()
        sample_rate = sound_file.samplerate
        write_path = sound_file.name
        sound_file.close()
        # 进行裁剪+淡入淡出
        if trim_head:
            audio_data = AudioEditTools.trim(audio_data, (silence_duration_head - self.__fadeInSeconds) * sample_rate, 0)
            AudioEditTools.fade(audio_data, int(self.__fadeInSeconds * sample_rate), 1)
            self.tblFileList.setItem(self.__currentRow, 2, QTableWidgetItem(str(self.__fadeInSeconds)))
        if trim_tail:
            audio_data = AudioEditTools.trim(audio_data, 0, (silence_duration_tail - self.__fadeOutSeconds) * sample_rate)
            AudioEditTools.fade(audio_data, int(self.__fadeOutSeconds * sample_rate), -1)
            self.tblFileList.setItem(self.__currentRow, 3, QTableWidgetItem(str(self.__fadeOutSeconds)))
        soundfile.write(file=write_path, data=audio_data, samplerate=sample_rate)
        # 更新列表显示
        status_item = QTableWidgetItem('已裁剪')
        status_item.setForeground(QColor(0, 200, 0))
        self.tblFileList.setItem(self.__currentRow, 4, status_item)
        self.__currentRow += 1

    def closeEvent(self, close_event):
        self.reset()

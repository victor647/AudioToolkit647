import os
import soundfile
from Libraries import WAAPI, AudioEditTools
from ObjectTools import AudioSourceTools
from PyQt6.QtCore import QEventLoop
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDialog, QFileDialog, QTableWidgetItem
from QtDesign.AudioTailTrimmer_ui import Ui_AudioTailTrimmer
from Threading.BatchProcessor import BatchProcessor


# 裁剪音频文件尾巴的工具
class AudioTailTrimWindow(QDialog, Ui_AudioTailTrimmer):

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
        if len(active_objects) > 0 and WAAPI.Client:
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
        if event.type() == QEventLoop.DragEnter:
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
                self.add_file(AudioSourceTools.get_source_file_path(obj))
            else:
                self.populate_from_wwise(WAAPI.get_child_objects(obj, False))

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

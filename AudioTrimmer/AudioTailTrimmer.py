import os
import sys
import soundfile
import Tools
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView

from QtDesign.AudioTailTrimmer_ui import Ui_AudioTailTrimmer


class AudioTailTrimmer(QMainWindow, Ui_AudioTailTrimmer):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setup_triggers()
        self.__soundFiles = []
        self.tblFileList.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def setup_triggers(self):
        self.btnImportFiles.clicked.connect(self.import_files)
        self.btnAnalyzeTails.clicked.connect(self.analyze_tails)
        self.btnStartTrim.clicked.connect(self.start_trimming)
        self.tblFileList.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.DragEnter:
            for url in event.mimeData().urls():
                self.add_file(url.toLocalFile())
            return True
        return super().eventFilter(source, event)

    def reset(self):
        self.__soundFiles = []
        self.tblFileList.setRowCount(0)

    def import_files(self):
        self.reset()

        files = QFileDialog.getOpenFileNames(filter='WAV(*.wav)')
        file_count = len(files[0])
        if file_count == 0:
            return
        for file_path in files[0]:
            self.add_file(file_path)
        self.tblFileList.repaint()

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

    def analyze_tails(self):
        row = 0
        samples_per_frame = 512
        threshold_linear = Tools.decibel_to_linear(self.spbCutThreshold.value())
        for sound_file in self.__soundFiles:
            audio_data = sound_file.read()
            # calculate total duration
            duration = round(sound_file.frames / sound_file.samplerate * 1.0, 3)
            self.tblFileList.setItem(row, 1, QTableWidgetItem(str(duration)))
            # calculate silence duration
            silence_frames = Tools.get_tail_silence_duration_frames(audio_data, samples_per_frame, threshold_linear)
            silence_duration = round(silence_frames * samples_per_frame / sound_file.samplerate * 1.0, 3)
            self.tblFileList.setItem(row, 2, QTableWidgetItem(str(silence_duration)))
            if silence_duration > self.spbFadeDuration.value():
                status_item = QTableWidgetItem('Detected')
                status_item.setForeground(QColor(200, 0, 0))
            else:
                status_item = QTableWidgetItem('Normal')
            self.tblFileList.setItem(row, 3, status_item)
            row += 1

    def start_trimming(self):
        row = 0
        fade_duration = self.spbFadeDuration.value()
        for sound_file in self.__soundFiles:
            silence_duration = float(self.tblFileList.item(row, 2).text())
            if silence_duration > fade_duration:
                sound_file.seek(0)
                audio_data = sound_file.read()
                trim_samples = int((silence_duration - fade_duration) * sound_file.samplerate)
                # trim audio
                audio_data = audio_data[:len(audio_data) - trim_samples]
                # fade out the remaining silence
                Tools.apply_fade(audio_data, int(fade_duration * sound_file.samplerate), -1)
                soundfile.write(file=sound_file.name, data=audio_data, samplerate=sound_file.samplerate)
                # update table
                self.tblFileList.setItem(row, 2, QTableWidgetItem(str(fade_duration)))
                status_item = QTableWidgetItem('Trimmed')
                status_item.setForeground(QColor(0, 200, 0))
                self.tblFileList.setItem(row, 3, status_item)
            row += 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = AudioTailTrimmer()
    main_window.show()
    sys.exit(app.exec_())
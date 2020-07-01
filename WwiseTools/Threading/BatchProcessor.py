from PyQt5.QtCore import pyqtSignal, QThread
from Threading.ProgressBar import ProgressBar
from ObjectTools import WaapiTools


# 处理线程
class BatchProcessor(QThread):
    progressBarCallback = pyqtSignal(int, str)
    finishedCallback = pyqtSignal()

    def __del__(self):
        self.work = False
        self.terminate()

    def __init__(self, objects, processor):
        super().__init__()
        progress_bar = ProgressBar(len(objects), self)
        progress_bar.show()
        self.progressBarCallback.connect(progress_bar.update_search_progress)
        self.finishedCallback.connect(progress_bar.destroy)
        self.__objects = objects
        self.__processor = processor

    def run(self):
        WaapiTools.begin_undo_group()
        index = 0
        for obj in self.__objects:
            index += 1
            self.progressBarCallback.emit(index, obj['name'])
            self.__processor(obj)
        self.finishedCallback.emit()
        WaapiTools.end_undo_group()

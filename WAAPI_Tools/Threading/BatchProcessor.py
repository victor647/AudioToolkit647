from PyQt5.QtCore import pyqtSignal, QThread
from Threading.ProgressBar import ProgressBar
from Libraries import WaapiTools


# 处理线程
class BatchProcessor(QThread):
    progressBarCallback = pyqtSignal(int, str)
    finishedCallback = pyqtSignal()

    def __del__(self):
        self.work = False
        self.terminate()

    def __init__(self, objects, processor, action_name):
        super().__init__()
        progress_bar = ProgressBar(len(objects), self)
        progress_bar.show()
        self.progressBarCallback.connect(progress_bar.update_search_progress)
        self.finishedCallback.connect(progress_bar.destroy)
        self.__objects = objects
        self.__processor = processor
        self.__actionName = action_name

    def run(self):
        if WaapiTools.Client is None:
            return
        WaapiTools.begin_undo_group()
        index = 0
        for obj in self.__objects:
            index += 1
            self.progressBarCallback.emit(index, obj.name if hasattr(obj, 'name') else obj['name'])
            self.__processor(obj)
        self.finishedCallback.emit()
        WaapiTools.end_undo_group(self.__actionName)

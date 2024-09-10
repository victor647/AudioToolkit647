from PyQt6.QtCore import pyqtSignal, QThread
from PyQt6.QtWidgets import QTableWidgetItem
from Threading.ProgressBar import ProgressBar
from Libraries import WaapiTools


# 处理线程
class BatchProcessor(QThread):
    progressBarCallback = pyqtSignal(int, str)
    finishedCallback = pyqtSignal()

    def __del__(self):
        self.work = False
        self.terminate()

    def __init__(self, objects, processor, action_name, finished_action=None):
        super().__init__()
        self.__progressBar = ProgressBar(len(objects), self)
        self.__progressBar.show()
        self.progressBarCallback.connect(self.__progressBar.update_search_progress)
        self.finishedCallback.connect(self.end)
        self.__objects = objects
        self.__processor = processor
        self.__actionName = action_name
        self.__finishAction = finished_action

    def run(self):
        if WaapiTools.Client is None:
            return
        WaapiTools.begin_undo_group(self.__actionName)
        index = 0
        for obj in self.__objects:
            index += 1
            text = ''
            if hasattr(obj, 'name'):
                text = obj.name
            elif isinstance(obj, QTableWidgetItem):
                text = obj.text()
            elif 'name' in obj:
                text = obj['name']
            self.progressBarCallback.emit(index, text)
            self.__processor(obj)
        self.finishedCallback.emit()
        WaapiTools.end_undo_group(self.__actionName)

    def end(self):
        self.__progressBar.destroy()
        if self.__finishAction:
            self.__finishAction()



from QtDesign.ProgressBar_ui import Ui_ProgressBar
from PyQt6.QtWidgets import QDialog


# 进度条显示
class ProgressBar(QDialog, Ui_ProgressBar):

    def __init__(self, total: int, progress):
        super().__init__()
        self.setupUi(self)
        self.__total = total
        self.__progress = progress

    def update_search_progress(self, index: int, obj_name: str):
        # 更新进度条显示
        self.pgbSearching.setValue(int(index / self.__total * 100))
        # 更新底部文字显示
        self.lblCurrentWorking.setText(obj_name + '(' + str(index) + '/' + str(self.__total) + ')')

    def finish_progress(self):
        self.close()

    # 关闭窗口停止进程
    def closeEvent(self, event):
        self.__progress.terminate()





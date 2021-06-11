import json
import os
import time
from PyQt5.QtWidgets import QFileDialog

use_filetypes = [('wwise tool save files', '.json')]
use_extension = '.json'


# 从文件导入
def import_from_file():
    file_path = QFileDialog.getOpenFileName(filter='JSON(*.json)')
    if file_path[0] == '':
        return None
    file = open(file_path[0], 'r')
    return json.load(file)


# 导出到文件
def export_to_file(dictobj):
    default_filename = "WwiseTool_Save_" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
    file_path = QFileDialog.getSaveFileName(filter='JSON(*.json)', caption=default_filename)
    if file_path[0] == '':
        return
    file = open(file_path[0], 'w')
    json.dump(dictobj, file)
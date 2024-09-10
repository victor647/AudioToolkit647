import json
import os
import shutil
from PyQt6.QtWidgets import QFileDialog

use_filetypes = [('wwise tool save files', '.json')]
use_extension = '.json'


# 从文件导入
def import_from_json():
    file_path = QFileDialog.getOpenFileName(filter='JSON(*.json)')
    if file_path[0] == '':
        return None
    file = open(file_path[0], 'r')
    return json.load(file)


# 导出到文件
def export_to_json(json_obj, file_name: str):
    file_path = QFileDialog.getSaveFileName(filter='JSON(*.json)', directory=file_name)
    if file_path[0] == '':
        return
    file = open(file_path[0], 'w')
    file.write(json.dumps(json_obj, indent=2))


# 移动文件
def move_file(old_path, new_path):
    if not os.path.exists(old_path):
        return
    folder = os.path.dirname(new_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    shutil.move(old_path, new_path)
    print(f'Moved file from {old_path} to {new_path}')
    # WaapiTools.add_to_source_control(new_path)

import os
import json
import csv
import shutil
import xml.etree.ElementTree as ElementTree
from PyQt6.QtWidgets import QFileDialog

use_filetypes = [('wwise tool save files', '.json')]
use_extension = '.json'


# 从json文件导入
def import_from_json():
    file_path = QFileDialog.getOpenFileName(filter='JSON(*.json)')
    if file_path[0] == '':
        return None
    file = open(file_path[0], 'r')
    return json.load(file)


# 导出到json文件
def export_to_json(json_obj, file_name: str):
    file_path = QFileDialog.getSaveFileName(filter='JSON(*.json)', directory=file_name)
    if file_path[0] == '':
        return
    file = open(file_path[0], 'w')
    file.write(json.dumps(json_obj, indent=2))


# 导出二维数组到csv文件
def export_to_csv(data: list, file_name: str):
    file_path = QFileDialog.getSaveFileName(filter='CSV(*.csv)', directory=file_name)
    if file_path[0] == '':
        return
    file = open(file_path[0], mode='w', newline='')
    writer = csv.writer(file)
    writer.writerows(data)


# 从csv文件导入
def import_from_csv():
    file_path = QFileDialog.getOpenFileName(filter='CSV(*.csv)')
    if file_path[0] == '':
        return None
    file = open(file_path[0], 'r')
    return list(csv.reader(file))


# 从xml或WorkUnit文件导入
def import_from_work_unit():
    file_path = QFileDialog.getOpenFileName(filter='XML(*.wwu)')
    if file_path[0] == '':
        return None, None
    tree = ElementTree.parse(file_path[0])
    root = tree.getroot()
    return root, file_path[0]


# 移动文件
def move_file(old_path, new_path):
    if not os.path.exists(old_path):
        return
    folder = os.path.dirname(new_path)
    if not os.path.exists(folder):
        os.makedirs(folder)
    shutil.move(old_path, new_path)
    print(f'Moved file from {old_path} to {new_path}')
    # WAAPI.add_to_source_control(new_path)

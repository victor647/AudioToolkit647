import itertools
import os

from PyQt5.QtWidgets import QDialog, QTableWidgetItem

from Libraries import ScriptingTools, WaapiTools
from QtDesign.BankAssignmentMatrix_ui import Ui_BankAssignmentMatrix


# 获取bank中的内容
def get_bank_inclusions(bank_obj):
    get_args = {
        'soundbank': bank_obj['id']
    }
    result = WaapiTools.Client.call('ak.wwise.core.soundbank.getInclusions', get_args)
    return result['inclusions']


# 清除Bank中所有内容
def clear_bank_inclusions(bank_obj):
    if bank_obj['type'] != 'SoundBank':
        return
    set_args = {
        'soundbank': bank_obj['id'],
        'operation': 'replace',
        'inclusions': []
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 为每个选中的对象创建一个SoundBank
def create_or_add_to_bank(obj):
    # 寻找或创建同名bank
    bank = WaapiTools.find_object_by_name_and_type(obj['name'], 'SoundBank')
    if bank is None:
        bank = create_sound_bank_by_name(obj['name'])

    # 为bank添加内容
    set_args = {
        'soundbank': bank['id'],
        'operation': 'add',
        'inclusions': [
            {
                'object': obj['id'],
                'filter': ['events', 'structures', 'media']
            }
        ]
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 根据名字创建SoundBank
def create_sound_bank_by_name(bank_name: str):
    work_unit = WaapiTools.get_object_from_path('\\SoundBanks\\Default Work Unit')
    new_bank = WaapiTools.create_object(bank_name, 'SoundBank', work_unit, 'fail')
    return new_bank


# 传统方式获取Bank大小
def get_bank_size(obj):
    wav_size = wem_size = used_files_count = 0
    unused_files = []
    for inclusion in get_bank_inclusions(obj):
        if 'media' in inclusion['filter']:
            bank_id = inclusion['object']
            get_args = {
                'waql': f'from object \"{bank_id}\" select descendants where type = \"AudioFileSource\"',
                'options': {
                    'return': ['name', 'originalWavFilePath', 'convertedWemFilePath', 'audioSourceLanguage']
                }
            }
            result = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)
            bank_name = obj['name']
            if len(result) == 0:
                print(f'Bank[{bank_name}]不包含任何资源！')
                return 5

            for audio_source in result['return']:
                language = audio_source['audioSourceLanguage']['name']
                if language == 'SFX' or language == 'Chinese':
                    wav_path = audio_source['originalWavFilePath']
                    if not os.path.exists(wav_path):
                        print(f'在Bank[{bank_name}]中找不到源文件[{wav_path}!]')
                        continue
                    wav_name = os.path.basename(wav_path)
                    wav_size += os.path.getsize(wav_path) / 1024
                    wem_path = audio_source['convertedWemFilePath']
                    if os.path.exists(wem_path):
                        wem_size += os.path.getsize(wem_path) / 1024
                        used_files_count += 1
                    else:
                        unused_files.append(wav_name)

    wav_size = round(wav_size / 1024, 2)
    wem_size = round(wem_size / 1024, 2)
    return wav_size, wem_size, used_files_count, unused_files


# 计算多个Bank合计大小
def get_total_bank_size(objects):
    total_wav_size = total_wem_size = total_used_files_count = 0
    total_unused_files = []
    for obj in objects:
        if obj['type'] == 'SoundBank':
            wav_size, wem_size, used_files_count, unused_files = get_bank_size(obj)
            total_wav_size += wav_size
            total_wem_size += wem_size
            total_used_files_count += used_files_count
            total_unused_files += unused_files
    return total_wav_size, total_wem_size, total_used_files_count, total_unused_files


# 把一批对象添加到的bank中，使用统一的inclusion
def add_objects_to_bank(bank_obj, objects: list, inclusion_type: list):
    inclusions = []
    for obj in objects:
        inclusion = {
            'object': obj['id'],
            'filter': inclusion_type
        }
        inclusions.append(inclusion)

    set_args = {
        'soundbank': bank_obj['id'],
        'operation': 'add',
        'inclusions': inclusions
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 把一批对象添加到的bank中，每个对象使用单独的inclusion
def add_objects_to_bank_with_individual_inclusion(bank_obj, objects):
    set_args = {
        'soundbank': bank_obj['id'],
        'operation': 'add',
        'inclusions': objects
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 设置SoundBank的包含内容
def set_inclusion_type(obj, inclusion_type: list):
    if obj['type'] != 'SoundBank':
        return
    get_args = {
        'soundbank': obj['id']
    }
    # 获取bank的内容并更改inclusion类别
    inclusions = WaapiTools.Client.call('ak.wwise.core.soundbank.getInclusions', get_args)['inclusions']
    for inclusion in inclusions:
        inclusion['filter'] = inclusion_type
    # 设置新的内容
    set_args = {
        'soundbank': obj['id'],
        'operation': 'replace',
        'inclusions': inclusions
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 资源和Bank矩阵分配
class BankAssignmentMatrix(QDialog, Ui_BankAssignmentMatrix):

    def __init__(self, main_window):
        super().__init__()
        self.setupUi(self)
        self.permutations = []
        self.setup_triggers()
        self.__mainWindow = main_window

    def setup_triggers(self):
        self.btnFillWithChildren.clicked.connect(self.get_children_from_selection)
        self.btnAddRow.clicked.connect(lambda: self.tblMatrix.setRowCount(self.tblMatrix.rowCount() + 1))
        self.btnRemoveRow.clicked.connect(lambda: self.tblMatrix.setRowCount(self.tblMatrix.rowCount() - 1))
        self.btnAddColumn.clicked.connect(lambda: self.tblMatrix.setColumnCount(self.tblMatrix.columnCount() + 1))
        self.btnRemoveColumn.clicked.connect(lambda: self.tblMatrix.setColumnCount(self.tblMatrix.columnCount() - 1))
        self.btnCreateBanks.clicked.connect(self.create_banks_by_matrix)
        self.btnAssignMedia.clicked.connect(self.assign_media_to_banks)

    # 从选中的对象的子对象填充列表
    def get_children_from_selection(self):
        selected_objects = WaapiTools.get_selected_objects()
        if len(selected_objects) == 0:
            return

        children = WaapiTools.get_child_objects(selected_objects[0], False)
        row = 0
        for child in children:
            if row >= self.tblMatrix.rowCount():
                self.tblMatrix.setRowCount(row + 1)
            self.tblMatrix.setItem(row, 0, QTableWidgetItem(child['name']))
            row += 1

    # 获取所有Bank名称排列组合
    def get_permutations(self):
        all_lists = []
        for column in range(self.tblMatrix.columnCount()):
            row_list = []
            for row in range(self.tblMatrix.rowCount()):
                item = self.tblMatrix.item(row, column)
                if item and item.text() != '':
                    row_list.append(item.text())
            if len(row_list) > 0:
                all_lists.append(row_list)
        self.permutations = list(itertools.product(*all_lists))

    # 根据矩阵内容创建Bank
    def create_banks_by_matrix(self):
        self.get_permutations()
        WaapiTools.begin_undo_group()
        for permutation in self.permutations:
            bank_name = self.get_bank_name(permutation)
            create_sound_bank_by_name(bank_name)
        WaapiTools.end_undo_group('Bank Matrix')

    # 通过关键字组合获得Bank名称
    @staticmethod
    def get_bank_name(permutation):
        bank_name = permutation[0]
        if len(permutation) >= 2:
            for index in range(1, len(permutation)):
                bank_name += '_' + permutation[index]
        return bank_name

    # 把所有对象添加到选中的bank中（只含media）
    def assign_media_to_banks(self):
        self.get_permutations()
        WaapiTools.begin_undo_group()
        for obj in self.__mainWindow.activeObjects:
            self.iterate_through_children(obj)
        WaapiTools.end_undo_group('Assign Bank Media')

    # 遍历每个子对象
    def iterate_through_children(self, obj):
        children = WaapiTools.get_child_objects(obj, False)
        for child in children:
            # 找不到就继续往里层找，直到Sound这一级为止
            if not self.find_matching_bank(child) and child['type'] != 'Sound':
                self.iterate_through_children(child)

    # 通过比对枚举找到对应的bank
    def find_matching_bank(self, obj):
        # 在每一种排列组合中搜索
        for permutation in self.permutations:
            match = True
            for item in permutation:
                if item not in obj['path']:
                    match = False
                    break
            # 找到符合名称的Bank
            if match:
                bank_name = self.get_bank_name(permutation)
                bank = WaapiTools.find_object_by_name_and_type(bank_name, 'SoundBank')
                # Wwise搜索会包含所有带有关键词的，需要精确搜索
                if bank and bank['name'] == bank_name:
                    set_args = {
                        'soundbank': bank['id'],
                        'operation': 'add',
                        'inclusions':
                            [
                                {
                                    'object': obj['id'],
                                    'filter': ['media']
                                }
                            ]
                    }
                    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)
                return True
        # 每一个组合都不符合，在下级继续找
        return False

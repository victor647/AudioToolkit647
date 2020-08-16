import win32api, os
from ObjectTools import WaapiTools, ScriptingTools
from QtDesign.BankAssignmentMatrix_ui import Ui_BankAssignmentMatrix
from PyQt5.QtWidgets import QDialog
from Threading.BatchProcessor import BatchProcessor
import itertools


# 为每个选中的对象创建一个SoundBank
def create_sound_bank_with_object_inclusion(obj):
    # 创建同名bank
    new_bank = create_sound_bank_by_name(obj['name'])
    if new_bank is None:
        return

    # 为bank添加内容
    set_args = {
        'soundbank': new_bank['id'],
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


# 获取选中的Bank的大小
def get_bank_size(objects):
    banks = ScriptingTools.filter_objects_by_type(objects, 'SoundBank')
    total_wav_size = total_wem_size = generated_file_count = total_file_count = 0
    unused_files = ''
    for obj in banks:
        get_args = {
            'soundbank': obj['id']
        }
        result = WaapiTools.Client.call('ak.wwise.core.soundbank.getInclusions', get_args)
        for inclusion in result['inclusions']:
            if 'media' in inclusion['filter']:
                get_args = {
                    'from': {
                        'id': [inclusion['object']]
                    },
                    'options': {
                        'return': ['name', 'sound:originalWavFilePath', 'sound:convertedWemFilePath', 'audioSource:language']
                    },
                    'transform': [
                        {
                            'select': ['descendants']
                        },
                        {
                            'where': ['type:isIn', ['AudioFileSource']]
                        }
                    ]
                }
                result = WaapiTools.Client.call('ak.wwise.core.object.get', get_args)
                for audio_source in result['return']:
                    language = audio_source['audioSource:language']['name']
                    if language == 'SFX' or language == 'Chinese':
                        total_file_count += 1
                        wav_path = audio_source['sound:originalWavFilePath']
                        wav_size = os.path.getsize(wav_path) / 1024
                        total_wav_size += wav_size
                        wem_path = audio_source['sound:convertedWemFilePath']
                        if os.path.exists(wem_path):
                            wem_size = os.path.getsize(wem_path) / 1024
                            total_wem_size += wem_size
                            generated_file_count += 1
                        else:
                            unused_files += '  ' + os.path.basename(wav_path) + '\n'
    total_wav_size = round(total_wav_size / 1024, 2)
    total_wem_size = round(total_wem_size / 1024, 2)
    message = f'Original Wav: {total_file_count} files, {total_wav_size}MB\nConverted Wem: {generated_file_count} files, {total_wem_size}MB'
    if unused_files != '':
        message += f'\nFiles or not used or haven\'t been generated:\n{unused_files}'
    win32api.MessageBox(0, message, 'Query Completed!')


# 把所有对象添加到选中的bank中（只含media）
def add_media_to_selected_bank(objects):
    banks = WaapiTools.get_selected_objects()
    if len(banks) == 0 or banks[0]['type'] != 'SoundBank':
        return

    bank = banks[0]
    inclusions = []
    for obj in objects:
        # 只添加Sound
        if obj['type'] != 'Sound':
            continue

        inclusion = {
            'object': obj['id'],
            'filter': ['media']
        }
        inclusions.append(inclusion)

    set_args = {
        'soundbank': bank['id'],
        'operation': 'add',
        'inclusions': inclusions
    }
    WaapiTools.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)


# 资源和Bank矩阵分配
class BankAssignmentMatrix(QDialog, Ui_BankAssignmentMatrix):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.permutations = []
        self.setup_triggers()

    def setup_triggers(self):
        self.btnAddRow.clicked.connect(lambda: self.tblMatrix.setRowCount(self.tblMatrix.rowCount() + 1))
        self.btnRemoveRow.clicked.connect(lambda: self.tblMatrix.setRowCount(self.tblMatrix.rowCount() - 1))
        self.btnAddColumn.clicked.connect(lambda: self.tblMatrix.setColumnCount(self.tblMatrix.columnCount() + 1))
        self.btnRemoveColumn.clicked.connect(lambda: self.tblMatrix.setColumnCount(self.tblMatrix.columnCount() - 1))
        self.btnCreateBanks.clicked.connect(self.create_banks_by_matrix)
        self.btnAssignMedia.clicked.connect(self.assign_media_to_banks)

    # 获取所有Bank名称排列组合
    def get_permutations(self):
        all_lists = []
        for column in range(self.tblMatrix.columnCount()):
            row_list = []
            for row in range(self.tblMatrix.rowCount()):
                item = self.tblMatrix.item(row, column)
                if item is not None:
                    row_list.append(item.text())
            all_lists.append(row_list)
        self.permutations = list(itertools.product(*all_lists))

    # 根据矩阵内容创建Bank
    def create_banks_by_matrix(self):
        self.get_permutations()
        for permutation in self.permutations:
            bank_name = self.get_bank_name(permutation)
            create_sound_bank_by_name(bank_name)

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
        # 获取选中对象下的所有子对象
        sounds_to_assign = []
        selected_objects = WaapiTools.get_selected_objects()
        for selected_obj in selected_objects:
            for descendant in WaapiTools.get_children_objects(selected_obj, True):
                if descendant['type'] == 'Sound':
                    sounds_to_assign.append(descendant)

        self.get_permutations()
        processor = BatchProcessor(sounds_to_assign, self.assign_media)
        processor.start()

    def assign_media(self, obj):
        # 在每一种排列组合中搜索
        for permutation in self.permutations:
            match = True
            for item in permutation:
                if item not in obj['name']:
                    match = False
                    break
            # 找到符合名称的Bank
            if match:
                bank_name = self.get_bank_name(permutation)
                bank = WaapiTools.get_object_from_name_and_type(bank_name, 'SoundBank')
                if bank:
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
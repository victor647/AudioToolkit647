import itertools
from Libraries import WAAPI, ProjectConventions
from ObjectTools import SoundBankTools
from PyQt6.QtWidgets import QDialog, QTableWidgetItem
from QtDesign.BankAssignmentMatrix_ui import Ui_BankAssignmentMatrix


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
        selection = WAAPI.get_selected_objects()
        if len(selection) == 0:
            return
        category = ProjectConventions.get_object_category(selection[0])
        self.tblMatrix.setRowCount(1)
        self.tblMatrix.setItem(0, 0, QTableWidgetItem(ProjectConventions.convert_category_to_acronym(category)))
        for row in range(len(selection)):
            obj = selection[row]
            self.tblMatrix.setItem(row, 1, QTableWidgetItem(obj['name']))
            self.tblMatrix.setRowCount(row + 2)
        self.tblMatrix.setRowCount(len(selection))

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
        WAAPI.begin_undo_group('Bank Matrix')
        for permutation in self.permutations:
            bank_name = self.get_bank_name(permutation)
            SoundBankTools.create_sound_bank_by_name(bank_name)
        WAAPI.end_undo_group('Bank Matrix')

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
        WAAPI.begin_undo_group('Assign Bank Media')
        for obj in self.__mainWindow.activeObjects:
            self.iterate_through_children(obj)
        WAAPI.end_undo_group('Assign Bank Media')

    # 遍历每个子对象
    def iterate_through_children(self, obj):
        children = WAAPI.get_child_objects(obj)
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
                if item.isupper():
                    item = ProjectConventions.convert_acronym_to_category(item)
                if item not in obj['path']:
                    match = False
                    break
            # 找到符合名称的Bank
            if match:
                bank_name = self.get_bank_name(permutation)
                bank = WAAPI.find_object_by_name_and_type(bank_name, 'SoundBank')
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
                    WAAPI.Client.call('ak.wwise.core.soundbank.setInclusions', set_args)
                return True
        # 每一个组合都不符合，在下级继续找
        return False

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UnityAssetManager.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_UnityAssetManager(object):
    def setupUi(self, UnityAssetManager):
        UnityAssetManager.setObjectName("UnityAssetManager")
        UnityAssetManager.resize(548, 574)
        self.verticalLayout = QtWidgets.QVBoxLayout(UnityAssetManager)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnSelectAssetFolder = QtWidgets.QPushButton(UnityAssetManager)
        self.btnSelectAssetFolder.setObjectName("btnSelectAssetFolder")
        self.horizontalLayout.addWidget(self.btnSelectAssetFolder)
        self.btnDeleteSelected = QtWidgets.QPushButton(UnityAssetManager)
        self.btnDeleteSelected.setObjectName("btnDeleteSelected")
        self.horizontalLayout.addWidget(self.btnDeleteSelected)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblFileList = QtWidgets.QTableWidget(UnityAssetManager)
        self.tblFileList.setDragEnabled(True)
        self.tblFileList.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.tblFileList.setObjectName("tblFileList")
        self.tblFileList.setColumnCount(4)
        self.tblFileList.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblFileList.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblFileList.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblFileList.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblFileList.setHorizontalHeaderItem(3, item)
        self.verticalLayout.addWidget(self.tblFileList)

        self.retranslateUi(UnityAssetManager)
        QtCore.QMetaObject.connectSlotsByName(UnityAssetManager)

    def retranslateUi(self, UnityAssetManager):
        _translate = QtCore.QCoreApplication.translate
        UnityAssetManager.setWindowTitle(_translate("UnityAssetManager", " Unity Wwise Asset管理"))
        self.btnSelectAssetFolder.setText(_translate("UnityAssetManager", "选择Wwise目录下ScriptableObject文件夹"))
        self.btnDeleteSelected.setText(_translate("UnityAssetManager", "删除选中资源"))
        self.tblFileList.setSortingEnabled(True)
        item = self.tblFileList.horizontalHeaderItem(0)
        item.setText(_translate("UnityAssetManager", "名称"))
        item = self.tblFileList.horizontalHeaderItem(1)
        item.setText(_translate("UnityAssetManager", "类型"))
        item = self.tblFileList.horizontalHeaderItem(2)
        item.setText(_translate("UnityAssetManager", "状态"))
        item = self.tblFileList.horizontalHeaderItem(3)
        item.setText(_translate("UnityAssetManager", "GUID"))
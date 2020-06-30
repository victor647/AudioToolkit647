# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1013, 464)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblWaapiPort = QtWidgets.QLabel(self.centralwidget)
        self.lblWaapiPort.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lblWaapiPort.setObjectName("lblWaapiPort")
        self.horizontalLayout.addWidget(self.lblWaapiPort)
        self.spbWaapiPort = QtWidgets.QSpinBox(self.centralwidget)
        self.spbWaapiPort.setMaximumSize(QtCore.QSize(80, 16777215))
        self.spbWaapiPort.setMinimum(1000)
        self.spbWaapiPort.setMaximum(9999)
        self.spbWaapiPort.setProperty("value", 8080)
        self.spbWaapiPort.setObjectName("spbWaapiPort")
        self.horizontalLayout.addWidget(self.spbWaapiPort)
        self.btnWaapiConnect = QtWidgets.QPushButton(self.centralwidget)
        self.btnWaapiConnect.setObjectName("btnWaapiConnect")
        self.horizontalLayout.addWidget(self.btnWaapiConnect)
        self.btnGetSelectedObjects = QtWidgets.QPushButton(self.centralwidget)
        self.btnGetSelectedObjects.setObjectName("btnGetSelectedObjects")
        self.horizontalLayout.addWidget(self.btnGetSelectedObjects)
        self.btnRemoveSelection = QtWidgets.QPushButton(self.centralwidget)
        self.btnRemoveSelection.setObjectName("btnRemoveSelection")
        self.horizontalLayout.addWidget(self.btnRemoveSelection)
        self.btnClearObjects = QtWidgets.QPushButton(self.centralwidget)
        self.btnClearObjects.setObjectName("btnClearObjects")
        self.horizontalLayout.addWidget(self.btnClearObjects)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblActiveObjects = QtWidgets.QTableWidget(self.centralwidget)
        self.tblActiveObjects.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tblActiveObjects.setObjectName("tblActiveObjects")
        self.tblActiveObjects.setColumnCount(3)
        self.tblActiveObjects.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tblActiveObjects.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblActiveObjects.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tblActiveObjects.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.tblActiveObjects)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.cbxKeepSelf = QtWidgets.QCheckBox(self.centralwidget)
        self.cbxKeepSelf.setMaximumSize(QtCore.QSize(80, 16777215))
        self.cbxKeepSelf.setObjectName("cbxKeepSelf")
        self.horizontalLayout_3.addWidget(self.cbxKeepSelf)
        self.cbxRecursiveFind = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxRecursiveFind.sizePolicy().hasHeightForWidth())
        self.cbxRecursiveFind.setSizePolicy(sizePolicy)
        self.cbxRecursiveFind.setChecked(True)
        self.cbxRecursiveFind.setObjectName("cbxRecursiveFind")
        self.horizontalLayout_3.addWidget(self.cbxRecursiveFind)
        self.btnFindParent = QtWidgets.QPushButton(self.centralwidget)
        self.btnFindParent.setObjectName("btnFindParent")
        self.horizontalLayout_3.addWidget(self.btnFindParent)
        self.btnFindChildren = QtWidgets.QPushButton(self.centralwidget)
        self.btnFindChildren.setObjectName("btnFindChildren")
        self.horizontalLayout_3.addWidget(self.btnFindChildren)
        self.cbbDescendantType = QtWidgets.QComboBox(self.centralwidget)
        self.cbbDescendantType.setObjectName("cbbDescendantType")
        self.horizontalLayout_3.addWidget(self.cbbDescendantType)
        self.btnFilterByType = QtWidgets.QPushButton(self.centralwidget)
        self.btnFilterByType.setObjectName("btnFilterByType")
        self.horizontalLayout_3.addWidget(self.btnFilterByType)
        self.iptSelectionFilter = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.iptSelectionFilter.sizePolicy().hasHeightForWidth())
        self.iptSelectionFilter.setSizePolicy(sizePolicy)
        self.iptSelectionFilter.setObjectName("iptSelectionFilter")
        self.horizontalLayout_3.addWidget(self.iptSelectionFilter)
        self.cbxCaseSensitive = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxCaseSensitive.sizePolicy().hasHeightForWidth())
        self.cbxCaseSensitive.setSizePolicy(sizePolicy)
        self.cbxCaseSensitive.setObjectName("cbxCaseSensitive")
        self.horizontalLayout_3.addWidget(self.cbxCaseSensitive)
        self.btnFilterByName = QtWidgets.QPushButton(self.centralwidget)
        self.btnFilterByName.setObjectName("btnFilterByName")
        self.horizontalLayout_3.addWidget(self.btnFilterByName)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1013, 23))
        self.menubar.setObjectName("menubar")
        self.mnuAudioSource = QtWidgets.QMenu(self.menubar)
        self.mnuAudioSource.setObjectName("mnuAudioSource")
        self.mnuLogicContainers = QtWidgets.QMenu(self.menubar)
        self.mnuLogicContainers.setObjectName("mnuLogicContainers")
        self.mnuSoundBank = QtWidgets.QMenu(self.menubar)
        self.mnuSoundBank.setObjectName("mnuSoundBank")
        self.mnuCommon = QtWidgets.QMenu(self.menubar)
        self.mnuCommon.setObjectName("mnuCommon")
        self.menuRename = QtWidgets.QMenu(self.mnuCommon)
        self.menuRename.setObjectName("menuRename")
        self.mnuWorkUnit = QtWidgets.QMenu(self.menubar)
        self.mnuWorkUnit.setObjectName("mnuWorkUnit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionEnable = QtWidgets.QAction(MainWindow)
        self.actionEnable.setObjectName("actionEnable")
        self.actionDisable = QtWidgets.QAction(MainWindow)
        self.actionDisable.setObjectName("actionDisable")
        self.actionEnable_2 = QtWidgets.QAction(MainWindow)
        self.actionEnable_2.setObjectName("actionEnable_2")
        self.actionDisable_2 = QtWidgets.QAction(MainWindow)
        self.actionDisable_2.setObjectName("actionDisable_2")
        self.actApplyEditsToOriginal = QtWidgets.QAction(MainWindow)
        self.actApplyEditsToOriginal.setObjectName("actApplyEditsToOriginal")
        self.actResetSourceEdits = QtWidgets.QAction(MainWindow)
        self.actResetSourceEdits.setObjectName("actResetSourceEdits")
        self.actAssignSwitchMappings = QtWidgets.QAction(MainWindow)
        self.actAssignSwitchMappings.setObjectName("actAssignSwitchMappings")
        self.actionEnable_3 = QtWidgets.QAction(MainWindow)
        self.actionEnable_3.setObjectName("actionEnable_3")
        self.actionDisable_3 = QtWidgets.QAction(MainWindow)
        self.actionDisable_3.setObjectName("actionDisable_3")
        self.actDeleteObjects = QtWidgets.QAction(MainWindow)
        self.actDeleteObjects.setObjectName("actDeleteObjects")
        self.actCalculateBankSize = QtWidgets.QAction(MainWindow)
        self.actCalculateBankSize.setObjectName("actCalculateBankSize")
        self.actCreateSoundBank = QtWidgets.QAction(MainWindow)
        self.actCreateSoundBank.setObjectName("actCreateSoundBank")
        self.actionPlay = QtWidgets.QAction(MainWindow)
        self.actionPlay.setObjectName("actionPlay")
        self.actionStop = QtWidgets.QAction(MainWindow)
        self.actionStop.setObjectName("actionStop")
        self.actionPause = QtWidgets.QAction(MainWindow)
        self.actionPause.setObjectName("actionPause")
        self.actionBreak = QtWidgets.QAction(MainWindow)
        self.actionBreak.setObjectName("actionBreak")
        self.actChangeToTitleCase = QtWidgets.QAction(MainWindow)
        self.actChangeToTitleCase.setObjectName("actChangeToTitleCase")
        self.actChangeToLowerCase = QtWidgets.QAction(MainWindow)
        self.actChangeToLowerCase.setObjectName("actChangeToLowerCase")
        self.actChangeToUpperCase = QtWidgets.QAction(MainWindow)
        self.actChangeToUpperCase.setObjectName("actChangeToUpperCase")
        self.actMultiEditor = QtWidgets.QAction(MainWindow)
        self.actMultiEditor.setObjectName("actMultiEditor")
        self.actBatchRenamer = QtWidgets.QAction(MainWindow)
        self.actBatchRenamer.setObjectName("actBatchRenamer")
        self.actConvertToWorkUnit = QtWidgets.QAction(MainWindow)
        self.actConvertToWorkUnit.setObjectName("actConvertToWorkUnit")
        self.mnuAudioSource.addAction(self.actApplyEditsToOriginal)
        self.mnuAudioSource.addAction(self.actResetSourceEdits)
        self.mnuLogicContainers.addAction(self.actAssignSwitchMappings)
        self.mnuSoundBank.addAction(self.actCalculateBankSize)
        self.mnuSoundBank.addAction(self.actCreateSoundBank)
        self.menuRename.addAction(self.actChangeToTitleCase)
        self.menuRename.addAction(self.actChangeToLowerCase)
        self.menuRename.addAction(self.actChangeToUpperCase)
        self.mnuCommon.addAction(self.actDeleteObjects)
        self.mnuCommon.addAction(self.menuRename.menuAction())
        self.mnuCommon.addAction(self.actMultiEditor)
        self.mnuCommon.addAction(self.actBatchRenamer)
        self.mnuWorkUnit.addAction(self.actConvertToWorkUnit)
        self.menubar.addAction(self.mnuCommon.menuAction())
        self.menubar.addAction(self.mnuAudioSource.menuAction())
        self.menubar.addAction(self.mnuLogicContainers.menuAction())
        self.menubar.addAction(self.mnuSoundBank.menuAction())
        self.menubar.addAction(self.mnuWorkUnit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WwiseTools"))
        self.lblWaapiPort.setText(_translate("MainWindow", "WAAPI Port"))
        self.btnWaapiConnect.setText(_translate("MainWindow", "Connect to Wwise"))
        self.btnGetSelectedObjects.setText(_translate("MainWindow", "Get Wwise Selection"))
        self.btnRemoveSelection.setText(_translate("MainWindow", "Remove Table Selection"))
        self.btnClearObjects.setText(_translate("MainWindow", "Clear List"))
        item = self.tblActiveObjects.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Name"))
        item = self.tblActiveObjects.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Type"))
        item = self.tblActiveObjects.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Path"))
        self.cbxKeepSelf.setText(_translate("MainWindow", "Keep Self"))
        self.cbxRecursiveFind.setText(_translate("MainWindow", "Recursive"))
        self.btnFindParent.setText(_translate("MainWindow", "Find Parent"))
        self.btnFindChildren.setText(_translate("MainWindow", "Find Children"))
        self.btnFilterByType.setText(_translate("MainWindow", "Filter by Type"))
        self.cbxCaseSensitive.setText(_translate("MainWindow", "Case Sensitive"))
        self.btnFilterByName.setText(_translate("MainWindow", "Filter by Name"))
        self.mnuAudioSource.setTitle(_translate("MainWindow", "AudioSource"))
        self.mnuLogicContainers.setTitle(_translate("MainWindow", "Containers"))
        self.mnuSoundBank.setTitle(_translate("MainWindow", "SoundBank"))
        self.mnuCommon.setTitle(_translate("MainWindow", "Common"))
        self.menuRename.setTitle(_translate("MainWindow", "Rename"))
        self.mnuWorkUnit.setTitle(_translate("MainWindow", "WorkUnit"))
        self.actionEnable.setText(_translate("MainWindow", "Enable"))
        self.actionDisable.setText(_translate("MainWindow", "Disable"))
        self.actionEnable_2.setText(_translate("MainWindow", "Enable"))
        self.actionDisable_2.setText(_translate("MainWindow", "Disable"))
        self.actApplyEditsToOriginal.setText(_translate("MainWindow", "Apply Edits to Original"))
        self.actResetSourceEdits.setText(_translate("MainWindow", "Reset Edits"))
        self.actAssignSwitchMappings.setText(_translate("MainWindow", "Assign Switch Mappings"))
        self.actionEnable_3.setText(_translate("MainWindow", "Enable"))
        self.actionDisable_3.setText(_translate("MainWindow", "Disable"))
        self.actDeleteObjects.setText(_translate("MainWindow", "Delete"))
        self.actCalculateBankSize.setText(_translate("MainWindow", "Calculate Size"))
        self.actCreateSoundBank.setText(_translate("MainWindow", "Create Per Object"))
        self.actionPlay.setText(_translate("MainWindow", "Play"))
        self.actionStop.setText(_translate("MainWindow", "Stop"))
        self.actionPause.setText(_translate("MainWindow", "Pause"))
        self.actionBreak.setText(_translate("MainWindow", "Break"))
        self.actChangeToTitleCase.setText(_translate("MainWindow", "Title Case"))
        self.actChangeToLowerCase.setText(_translate("MainWindow", "Lower Case"))
        self.actChangeToUpperCase.setText(_translate("MainWindow", "Upper Case"))
        self.actMultiEditor.setText(_translate("MainWindow", "Multi Editor"))
        self.actBatchRenamer.setText(_translate("MainWindow", "Batch Rename"))
        self.actConvertToWorkUnit.setText(_translate("MainWindow", "Convert to Work Unit"))

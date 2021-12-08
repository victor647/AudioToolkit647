# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(738, 578)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblWaapiPort = QtWidgets.QLabel(self.centralwidget)
        self.lblWaapiPort.setMaximumSize(QtCore.QSize(80, 16777215))
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
        self.btnMultiEditor = QtWidgets.QPushButton(self.centralwidget)
        self.btnMultiEditor.setObjectName("btnMultiEditor")
        self.horizontalLayout.addWidget(self.btnMultiEditor)
        self.btnBatchRename = QtWidgets.QPushButton(self.centralwidget)
        self.btnBatchRename.setObjectName("btnBatchRename")
        self.horizontalLayout.addWidget(self.btnBatchRename)
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
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.cbxKeepSelf = QtWidgets.QCheckBox(self.centralwidget)
        self.cbxKeepSelf.setMaximumSize(QtCore.QSize(80, 16777215))
        self.cbxKeepSelf.setObjectName("cbxKeepSelf")
        self.horizontalLayout_2.addWidget(self.cbxKeepSelf)
        self.cbxRecursiveFind = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxRecursiveFind.sizePolicy().hasHeightForWidth())
        self.cbxRecursiveFind.setSizePolicy(sizePolicy)
        self.cbxRecursiveFind.setChecked(True)
        self.cbxRecursiveFind.setObjectName("cbxRecursiveFind")
        self.horizontalLayout_2.addWidget(self.cbxRecursiveFind)
        self.btnFindParent = QtWidgets.QPushButton(self.centralwidget)
        self.btnFindParent.setObjectName("btnFindParent")
        self.horizontalLayout_2.addWidget(self.btnFindParent)
        self.btnFindChildren = QtWidgets.QPushButton(self.centralwidget)
        self.btnFindChildren.setObjectName("btnFindChildren")
        self.horizontalLayout_2.addWidget(self.btnFindChildren)
        self.btnRemoveSelection = QtWidgets.QPushButton(self.centralwidget)
        self.btnRemoveSelection.setObjectName("btnRemoveSelection")
        self.horizontalLayout_2.addWidget(self.btnRemoveSelection)
        self.btnClearObjects = QtWidgets.QPushButton(self.centralwidget)
        self.btnClearObjects.setObjectName("btnClearObjects")
        self.horizontalLayout_2.addWidget(self.btnClearObjects)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.cbbDescendantType = QtWidgets.QComboBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbbDescendantType.sizePolicy().hasHeightForWidth())
        self.cbbDescendantType.setSizePolicy(sizePolicy)
        self.cbbDescendantType.setObjectName("cbbDescendantType")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.cbbDescendantType.addItem("")
        self.gridLayout.addWidget(self.cbbDescendantType, 0, 0, 1, 1)
        self.gridLayout_9 = QtWidgets.QGridLayout()
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.gridLayout.addLayout(self.gridLayout_9, 4, 2, 1, 1)
        self.iptSelectionFilter = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.iptSelectionFilter.sizePolicy().hasHeightForWidth())
        self.iptSelectionFilter.setSizePolicy(sizePolicy)
        self.iptSelectionFilter.setMinimumSize(QtCore.QSize(200, 0))
        self.iptSelectionFilter.setInputMask("")
        self.iptSelectionFilter.setText("")
        self.iptSelectionFilter.setObjectName("iptSelectionFilter")
        self.gridLayout.addWidget(self.iptSelectionFilter, 0, 1, 1, 1)
        self.gridLayout_10 = QtWidgets.QGridLayout()
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.gridLayout.addLayout(self.gridLayout_10, 4, 3, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setMinimumSize(QtCore.QSize(250, 20))
        self.groupBox.setAutoFillBackground(False)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.radioBtn_group_key_name = QtWidgets.QRadioButton(self.groupBox)
        self.radioBtn_group_key_name.setGeometry(QtCore.QRect(0, 0, 81, 19))
        self.radioBtn_group_key_name.setFocusPolicy(QtCore.Qt.NoFocus)
        self.radioBtn_group_key_name.setChecked(True)
        self.radioBtn_group_key_name.setObjectName("radioBtn_group_key_name")
        self.radioBtn_group_key_path = QtWidgets.QRadioButton(self.groupBox)
        self.radioBtn_group_key_path.setGeometry(QtCore.QRect(100, 0, 81, 19))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioBtn_group_key_path.sizePolicy().hasHeightForWidth())
        self.radioBtn_group_key_path.setSizePolicy(sizePolicy)
        self.radioBtn_group_key_path.setObjectName("radioBtn_group_key_path")
        self.gridLayout.addWidget(self.groupBox, 1, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(250, 20))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.radioBtn_group_ope_include = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioBtn_group_ope_include.setGeometry(QtCore.QRect(0, 0, 81, 19))
        self.radioBtn_group_ope_include.setChecked(True)
        self.radioBtn_group_ope_include.setObjectName("radioBtn_group_ope_include")
        self.radioBtn_group_ope_exclude = QtWidgets.QRadioButton(self.groupBox_2)
        self.radioBtn_group_ope_exclude.setGeometry(QtCore.QRect(100, 0, 91, 19))
        self.radioBtn_group_ope_exclude.setObjectName("radioBtn_group_ope_exclude")
        self.gridLayout.addWidget(self.groupBox_2, 2, 1, 1, 1)
        self.cbxCaseSensitive = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxCaseSensitive.sizePolicy().hasHeightForWidth())
        self.cbxCaseSensitive.setSizePolicy(sizePolicy)
        self.cbxCaseSensitive.setObjectName("cbxCaseSensitive")
        self.gridLayout.addWidget(self.cbxCaseSensitive, 0, 2, 1, 1)
        self.cbxMatchWholeWord = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxMatchWholeWord.sizePolicy().hasHeightForWidth())
        self.cbxMatchWholeWord.setSizePolicy(sizePolicy)
        self.cbxMatchWholeWord.setSizeIncrement(QtCore.QSize(0, 0))
        self.cbxMatchWholeWord.setObjectName("cbxMatchWholeWord")
        self.gridLayout.addWidget(self.cbxMatchWholeWord, 1, 2, 1, 1)
        self.cbxUseRegularExpression = QtWidgets.QCheckBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxUseRegularExpression.sizePolicy().hasHeightForWidth())
        self.cbxUseRegularExpression.setSizePolicy(sizePolicy)
        self.cbxUseRegularExpression.setObjectName("cbxUseRegularExpression")
        self.gridLayout.addWidget(self.cbxUseRegularExpression, 2, 2, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("")
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 3, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 738, 23))
        self.menubar.setObjectName("menubar")
        self.mnuAudioSource = QtWidgets.QMenu(self.menubar)
        self.mnuAudioSource.setObjectName("mnuAudioSource")
        self.mnuLogicContainers = QtWidgets.QMenu(self.menubar)
        self.mnuLogicContainers.setObjectName("mnuLogicContainers")
        self.mnuSwitchContainer = QtWidgets.QMenu(self.mnuLogicContainers)
        self.mnuSwitchContainer.setObjectName("mnuSwitchContainer")
        self.mnuSoundBank = QtWidgets.QMenu(self.menubar)
        self.mnuSoundBank.setObjectName("mnuSoundBank")
        self.mnuSetInclusionTo = QtWidgets.QMenu(self.mnuSoundBank)
        self.mnuSetInclusionTo.setObjectName("mnuSetInclusionTo")
        self.mnuCommon = QtWidgets.QMenu(self.menubar)
        self.mnuCommon.setObjectName("mnuCommon")
        self.menuRename = QtWidgets.QMenu(self.mnuCommon)
        self.menuRename.setObjectName("menuRename")
        self.mnuConvertToType = QtWidgets.QMenu(self.mnuCommon)
        self.mnuConvertToType.setObjectName("mnuConvertToType")
        self.menuEvent = QtWidgets.QMenu(self.menubar)
        self.menuEvent.setObjectName("menuEvent")
        self.mnuFile = QtWidgets.QMenu(self.menubar)
        self.mnuFile.setObjectName("mnuFile")
        self.mnuEdit = QtWidgets.QMenu(self.menubar)
        self.mnuEdit.setObjectName("mnuEdit")
        self.mnuFilterByInclusion = QtWidgets.QMenu(self.mnuEdit)
        self.mnuFilterByInclusion.setObjectName("mnuFilterByInclusion")
        self.mnuSetInclusion = QtWidgets.QMenu(self.mnuEdit)
        self.mnuSetInclusion.setObjectName("mnuSetInclusion")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
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
        self.actCreateOrAddToBank = QtWidgets.QAction(MainWindow)
        self.actCreateOrAddToBank.setObjectName("actCreateOrAddToBank")
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
        self.actMoveListToSelection = QtWidgets.QAction(MainWindow)
        self.actMoveListToSelection.setObjectName("actMoveListToSelection")
        self.actUndo = QtWidgets.QAction(MainWindow)
        self.actUndo.setObjectName("actUndo")
        self.actRedo = QtWidgets.QAction(MainWindow)
        self.actRedo.setObjectName("actRedo")
        self.actCreatePlayEvent = QtWidgets.QAction(MainWindow)
        self.actCreatePlayEvent.setObjectName("actCreatePlayEvent")
        self.actReplaceSourceFiles = QtWidgets.QAction(MainWindow)
        self.actReplaceSourceFiles.setObjectName("actReplaceSourceFiles")
        self.actRemoveAllSwitchAssignments = QtWidgets.QAction(MainWindow)
        self.actRemoveAllSwitchAssignments.setObjectName("actRemoveAllSwitchAssignments")
        self.actConvertToWorkUnit = QtWidgets.QAction(MainWindow)
        self.actConvertToWorkUnit.setObjectName("actConvertToWorkUnit")
        self.actConvertToVirtualFolder = QtWidgets.QAction(MainWindow)
        self.actConvertToVirtualFolder.setObjectName("actConvertToVirtualFolder")
        self.actConvertToSwitchContainer = QtWidgets.QAction(MainWindow)
        self.actConvertToSwitchContainer.setObjectName("actConvertToSwitchContainer")
        self.actConvertToRandomSequenceContainer = QtWidgets.QAction(MainWindow)
        self.actConvertToRandomSequenceContainer.setObjectName("actConvertToRandomSequenceContainer")
        self.actConvertToBlendContainer = QtWidgets.QAction(MainWindow)
        self.actConvertToBlendContainer.setObjectName("actConvertToBlendContainer")
        self.actConvertToActorMixer = QtWidgets.QAction(MainWindow)
        self.actConvertToActorMixer.setObjectName("actConvertToActorMixer")
        self.actBankAssignmentMatrix = QtWidgets.QAction(MainWindow)
        self.actBankAssignmentMatrix.setObjectName("actBankAssignmentMatrix")
        self.actAddToSelectedBank = QtWidgets.QAction(MainWindow)
        self.actAddToSelectedBank.setObjectName("actAddToSelectedBank")
        self.actRenameOriginalToWwise = QtWidgets.QAction(MainWindow)
        self.actRenameOriginalToWwise.setObjectName("actRenameOriginalToWwise")
        self.actDeleteUnusedAKDFiles = QtWidgets.QAction(MainWindow)
        self.actDeleteUnusedAKDFiles.setObjectName("actDeleteUnusedAKDFiles")
        self.actClearInclusions = QtWidgets.QAction(MainWindow)
        self.actClearInclusions.setObjectName("actClearInclusions")
        self.actBreakContainer = QtWidgets.QAction(MainWindow)
        self.actBreakContainer.setObjectName("actBreakContainer")
        self.actAddToSameNameBank = QtWidgets.QAction(MainWindow)
        self.actAddToSameNameBank.setObjectName("actAddToSameNameBank")
        self.actSetInclusionToMediaOnly = QtWidgets.QAction(MainWindow)
        self.actSetInclusionToMediaOnly.setObjectName("actSetInclusionToMediaOnly")
        self.actIncludeMediaOnly = QtWidgets.QAction(MainWindow)
        self.actIncludeMediaOnly.setObjectName("actIncludeMediaOnly")
        self.actIncludeEventsAndStructures = QtWidgets.QAction(MainWindow)
        self.actIncludeEventsAndStructures.setObjectName("actIncludeEventsAndStructures")
        self.actIncludeAll = QtWidgets.QAction(MainWindow)
        self.actIncludeAll.setObjectName("actIncludeAll")
        self.actApplyFaderEditsDownstream = QtWidgets.QAction(MainWindow)
        self.actApplyFaderEditsDownstream.setObjectName("actApplyFaderEditsDownstream")
        self.actSplitByNetRole = QtWidgets.QAction(MainWindow)
        self.actSplitByNetRole.setObjectName("actSplitByNetRole")
        self.actImportFromFile = QtWidgets.QAction(MainWindow)
        self.actImportFromFile.setObjectName("actImportFromFile")
        self.actExportToFile = QtWidgets.QAction(MainWindow)
        self.actExportToFile.setObjectName("actExportToFile")
        self.actCopySelectionToList = QtWidgets.QAction(MainWindow)
        self.actCopySelectionToList.setObjectName("actCopySelectionToList")
        self.actWwiseSilenceAdd = QtWidgets.QAction(MainWindow)
        self.actWwiseSilenceAdd.setObjectName("actWwiseSilenceAdd")
        self.actWwiseSilenceRemove = QtWidgets.QAction(MainWindow)
        self.actWwiseSilenceRemove.setObjectName("actWwiseSilenceRemove")
        self.actReplaceEventNames = QtWidgets.QAction(MainWindow)
        self.actReplaceEventNames.setObjectName("actReplaceEventNames")
        self.actBatchReplaceTool = QtWidgets.QAction(MainWindow)
        self.actBatchReplaceTool.setObjectName("actBatchReplaceTool")
        self.actTrimTailSilence = QtWidgets.QAction(MainWindow)
        self.actTrimTailSilence.setObjectName("actTrimTailSilence")
        self.actFilterIncluded = QtWidgets.QAction(MainWindow)
        self.actFilterIncluded.setObjectName("actFilterIncluded")
        self.actSetIncluded = QtWidgets.QAction(MainWindow)
        self.actSetIncluded.setObjectName("actSetIncluded")
        self.actSetExcluded = QtWidgets.QAction(MainWindow)
        self.actSetExcluded.setObjectName("actSetExcluded")
        self.actFilterExcluded = QtWidgets.QAction(MainWindow)
        self.actFilterExcluded.setObjectName("actFilterExcluded")
        self.actTempTool = QtWidgets.QAction(MainWindow)
        self.actTempTool.setObjectName("actTempTool")
        self.actLocalizeLanguages = QtWidgets.QAction(MainWindow)
        self.actLocalizeLanguages.setObjectName("actLocalizeLanguages")
        self.mnuAudioSource.addAction(self.actApplyEditsToOriginal)
        self.mnuAudioSource.addAction(self.actResetSourceEdits)
        self.mnuAudioSource.addAction(self.actTrimTailSilence)
        self.mnuAudioSource.addSeparator()
        self.mnuAudioSource.addAction(self.actRenameOriginalToWwise)
        self.mnuAudioSource.addAction(self.actDeleteUnusedAKDFiles)
        self.mnuAudioSource.addAction(self.actLocalizeLanguages)
        self.mnuSwitchContainer.addAction(self.actAssignSwitchMappings)
        self.mnuSwitchContainer.addAction(self.actRemoveAllSwitchAssignments)
        self.mnuLogicContainers.addAction(self.actBreakContainer)
        self.mnuLogicContainers.addAction(self.actApplyFaderEditsDownstream)
        self.mnuLogicContainers.addAction(self.mnuSwitchContainer.menuAction())
        self.mnuLogicContainers.addAction(self.actSplitByNetRole)
        self.mnuSetInclusionTo.addAction(self.actIncludeMediaOnly)
        self.mnuSetInclusionTo.addAction(self.actIncludeEventsAndStructures)
        self.mnuSetInclusionTo.addAction(self.actIncludeAll)
        self.mnuSoundBank.addAction(self.actAddToSelectedBank)
        self.mnuSoundBank.addAction(self.actCreateOrAddToBank)
        self.mnuSoundBank.addAction(self.actBankAssignmentMatrix)
        self.mnuSoundBank.addSeparator()
        self.mnuSoundBank.addAction(self.actClearInclusions)
        self.mnuSoundBank.addAction(self.actCalculateBankSize)
        self.mnuSoundBank.addAction(self.mnuSetInclusionTo.menuAction())
        self.menuRename.addAction(self.actChangeToTitleCase)
        self.menuRename.addAction(self.actChangeToLowerCase)
        self.menuRename.addAction(self.actChangeToUpperCase)
        self.mnuConvertToType.addAction(self.actConvertToWorkUnit)
        self.mnuConvertToType.addAction(self.actConvertToVirtualFolder)
        self.mnuConvertToType.addAction(self.actConvertToActorMixer)
        self.mnuConvertToType.addAction(self.actConvertToBlendContainer)
        self.mnuConvertToType.addAction(self.actConvertToRandomSequenceContainer)
        self.mnuConvertToType.addAction(self.actConvertToSwitchContainer)
        self.mnuCommon.addAction(self.mnuConvertToType.menuAction())
        self.mnuCommon.addAction(self.menuRename.menuAction())
        self.mnuCommon.addSeparator()
        self.mnuCommon.addAction(self.actMoveListToSelection)
        self.mnuCommon.addAction(self.actCopySelectionToList)
        self.mnuCommon.addSeparator()
        self.mnuCommon.addAction(self.actBatchReplaceTool)
        self.menuEvent.addAction(self.actCreatePlayEvent)
        self.mnuFile.addAction(self.actImportFromFile)
        self.mnuFile.addAction(self.actExportToFile)
        self.mnuFilterByInclusion.addAction(self.actFilterIncluded)
        self.mnuFilterByInclusion.addAction(self.actFilterExcluded)
        self.mnuSetInclusion.addAction(self.actSetIncluded)
        self.mnuSetInclusion.addAction(self.actSetExcluded)
        self.mnuEdit.addAction(self.actUndo)
        self.mnuEdit.addAction(self.actRedo)
        self.mnuEdit.addSeparator()
        self.mnuEdit.addAction(self.mnuFilterByInclusion.menuAction())
        self.mnuEdit.addAction(self.mnuSetInclusion.menuAction())
        self.mnuEdit.addAction(self.actDeleteObjects)
        self.menu.addAction(self.actTempTool)
        self.menubar.addAction(self.mnuFile.menuAction())
        self.menubar.addAction(self.mnuEdit.menuAction())
        self.menubar.addAction(self.mnuCommon.menuAction())
        self.menubar.addAction(self.mnuAudioSource.menuAction())
        self.menubar.addAction(self.mnuLogicContainers.menuAction())
        self.menubar.addAction(self.menuEvent.menuAction())
        self.menubar.addAction(self.mnuSoundBank.menuAction())
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WAAPI工具集"))
        self.lblWaapiPort.setText(_translate("MainWindow", "WAAPI网络端口"))
        self.btnWaapiConnect.setText(_translate("MainWindow", "连接到Wwise工程"))
        self.btnGetSelectedObjects.setText(_translate("MainWindow", "获取Wwise工程选中对象"))
        self.btnMultiEditor.setText(_translate("MainWindow", "多项编辑器"))
        self.btnBatchRename.setText(_translate("MainWindow", "批量重命名"))
        item = self.tblActiveObjects.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "名称"))
        item = self.tblActiveObjects.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "类型"))
        item = self.tblActiveObjects.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "路径"))
        self.cbxKeepSelf.setText(_translate("MainWindow", "保留原始"))
        self.cbxRecursiveFind.setText(_translate("MainWindow", "递归查找"))
        self.btnFindParent.setText(_translate("MainWindow", "查找上级对象"))
        self.btnFindChildren.setText(_translate("MainWindow", "查找下级对象"))
        self.btnRemoveSelection.setText(_translate("MainWindow", "删除列表选中"))
        self.btnClearObjects.setText(_translate("MainWindow", "清空列表"))
        self.cbbDescendantType.setItemText(0, _translate("MainWindow", "全部类型"))
        self.cbbDescendantType.setItemText(1, _translate("MainWindow", "Action"))
        self.cbbDescendantType.setItemText(2, _translate("MainWindow", "ActorMixer"))
        self.cbbDescendantType.setItemText(3, _translate("MainWindow", "AudioFileSource"))
        self.cbbDescendantType.setItemText(4, _translate("MainWindow", "AuxBus"))
        self.cbbDescendantType.setItemText(5, _translate("MainWindow", "BlendContainer"))
        self.cbbDescendantType.setItemText(6, _translate("MainWindow", "Bus"))
        self.cbbDescendantType.setItemText(7, _translate("MainWindow", "Event"))
        self.cbbDescendantType.setItemText(8, _translate("MainWindow", "Folder"))
        self.cbbDescendantType.setItemText(9, _translate("MainWindow", "GameParameter"))
        self.cbbDescendantType.setItemText(10, _translate("MainWindow", "MusicPlaylistContainer"))
        self.cbbDescendantType.setItemText(11, _translate("MainWindow", "MusicSegment"))
        self.cbbDescendantType.setItemText(12, _translate("MainWindow", "MusicSwitchContainer"))
        self.cbbDescendantType.setItemText(13, _translate("MainWindow", "MusicTrack"))
        self.cbbDescendantType.setItemText(14, _translate("MainWindow", "RandomSequenceContainer"))
        self.cbbDescendantType.setItemText(15, _translate("MainWindow", "Sound"))
        self.cbbDescendantType.setItemText(16, _translate("MainWindow", "SoundBank"))
        self.cbbDescendantType.setItemText(17, _translate("MainWindow", "State"))
        self.cbbDescendantType.setItemText(18, _translate("MainWindow", "Switch"))
        self.cbbDescendantType.setItemText(19, _translate("MainWindow", "SwitchContainer"))
        self.cbbDescendantType.setItemText(20, _translate("MainWindow", "WorkUnit"))
        self.radioBtn_group_key_name.setText(_translate("MainWindow", "按名称"))
        self.radioBtn_group_key_path.setText(_translate("MainWindow", "按路径"))
        self.radioBtn_group_ope_include.setText(_translate("MainWindow", "筛选"))
        self.radioBtn_group_ope_exclude.setText(_translate("MainWindow", "筛除"))
        self.cbxCaseSensitive.setText(_translate("MainWindow", "区分大小写"))
        self.cbxMatchWholeWord.setText(_translate("MainWindow", "全字匹配"))
        self.cbxUseRegularExpression.setText(_translate("MainWindow", "使用正则表达式"))
        self.mnuAudioSource.setTitle(_translate("MainWindow", "AudioSource"))
        self.mnuLogicContainers.setTitle(_translate("MainWindow", "Container"))
        self.mnuSwitchContainer.setTitle(_translate("MainWindow", "Switch Container"))
        self.mnuSoundBank.setTitle(_translate("MainWindow", "SoundBank"))
        self.mnuSetInclusionTo.setTitle(_translate("MainWindow", "调整包含内容"))
        self.mnuCommon.setTitle(_translate("MainWindow", "通用"))
        self.menuRename.setTitle(_translate("MainWindow", "改变命名规则"))
        self.mnuConvertToType.setTitle(_translate("MainWindow", "改变类型为"))
        self.menuEvent.setTitle(_translate("MainWindow", "Event"))
        self.mnuFile.setTitle(_translate("MainWindow", "文件"))
        self.mnuEdit.setTitle(_translate("MainWindow", "编辑"))
        self.mnuFilterByInclusion.setTitle(_translate("MainWindow", "筛选"))
        self.mnuSetInclusion.setTitle(_translate("MainWindow", "设为"))
        self.menu.setTitle(_translate("MainWindow", "其他"))
        self.actionEnable.setText(_translate("MainWindow", "Enable"))
        self.actionDisable.setText(_translate("MainWindow", "Disable"))
        self.actionEnable_2.setText(_translate("MainWindow", "Enable"))
        self.actionDisable_2.setText(_translate("MainWindow", "Disable"))
        self.actApplyEditsToOriginal.setText(_translate("MainWindow", "应用剪辑至源文件"))
        self.actResetSourceEdits.setText(_translate("MainWindow", "重置剪辑"))
        self.actAssignSwitchMappings.setText(_translate("MainWindow", "自动分配"))
        self.actionEnable_3.setText(_translate("MainWindow", "Enable"))
        self.actionDisable_3.setText(_translate("MainWindow", "Disable"))
        self.actDeleteObjects.setText(_translate("MainWindow", "删除"))
        self.actCalculateBankSize.setText(_translate("MainWindow", "计算媒体资源大小"))
        self.actCreateOrAddToBank.setText(_translate("MainWindow", "为每个对象创建或加入Bank"))
        self.actionPlay.setText(_translate("MainWindow", "Play"))
        self.actionStop.setText(_translate("MainWindow", "Stop"))
        self.actionPause.setText(_translate("MainWindow", "Pause"))
        self.actionBreak.setText(_translate("MainWindow", "Break"))
        self.actChangeToTitleCase.setText(_translate("MainWindow", "首字母大写"))
        self.actChangeToLowerCase.setText(_translate("MainWindow", "全小写"))
        self.actChangeToUpperCase.setText(_translate("MainWindow", "全大写"))
        self.actMultiEditor.setText(_translate("MainWindow", "Multi Editor"))
        self.actBatchRenamer.setText(_translate("MainWindow", "Batch Rename"))
        self.actMoveListToSelection.setText(_translate("MainWindow", "列表移至工程选中"))
        self.actUndo.setText(_translate("MainWindow", "撤销"))
        self.actRedo.setText(_translate("MainWindow", "重做"))
        self.actCreatePlayEvent.setText(_translate("MainWindow", "创建播放事件"))
        self.actReplaceSourceFiles.setText(_translate("MainWindow", "Replace Source Files"))
        self.actRemoveAllSwitchAssignments.setText(_translate("MainWindow", "清空分配"))
        self.actConvertToWorkUnit.setText(_translate("MainWindow", "Work Unit"))
        self.actConvertToVirtualFolder.setText(_translate("MainWindow", "Virtual Folder"))
        self.actConvertToSwitchContainer.setText(_translate("MainWindow", "Switch Container"))
        self.actConvertToRandomSequenceContainer.setText(_translate("MainWindow", "Random/Sequence Container"))
        self.actConvertToBlendContainer.setText(_translate("MainWindow", "Blend Container"))
        self.actConvertToActorMixer.setText(_translate("MainWindow", "Actor Mixer"))
        self.actBankAssignmentMatrix.setText(_translate("MainWindow", "自动映射分配工具"))
        self.actAddToSelectedBank.setText(_translate("MainWindow", "添加列表到选中的Bank"))
        self.actRenameOriginalToWwise.setText(_translate("MainWindow", "重命名源文件"))
        self.actDeleteUnusedAKDFiles.setText(_translate("MainWindow", "删除多余AKD文件"))
        self.actClearInclusions.setText(_translate("MainWindow", "清除包含内容"))
        self.actBreakContainer.setText(_translate("MainWindow", "拆除结构"))
        self.actAddToSameNameBank.setText(_translate("MainWindow", "Add to Same Name Bank"))
        self.actSetInclusionToMediaOnly.setText(_translate("MainWindow", "Set Inclusion to Media Only"))
        self.actIncludeMediaOnly.setText(_translate("MainWindow", "仅媒体"))
        self.actIncludeEventsAndStructures.setText(_translate("MainWindow", "事件与结构"))
        self.actIncludeAll.setText(_translate("MainWindow", "全部"))
        self.actApplyFaderEditsDownstream.setText(_translate("MainWindow", "混音向下汇总"))
        self.actSplitByNetRole.setText(_translate("MainWindow", "按照1P/2P/3P拆分"))
        self.actImportFromFile.setText(_translate("MainWindow", "导入"))
        self.actExportToFile.setText(_translate("MainWindow", "导出"))
        self.actCopySelectionToList.setText(_translate("MainWindow", "复制工程选中到列表"))
        self.actWwiseSilenceAdd.setText(_translate("MainWindow", "添加Wwise Silence"))
        self.actWwiseSilenceRemove.setText(_translate("MainWindow", "删除Wwise Silence"))
        self.actReplaceEventNames.setText(_translate("MainWindow", "Replace Event Names"))
        self.actBatchReplaceTool.setText(_translate("MainWindow", "模板批量替换"))
        self.actTrimTailSilence.setText(_translate("MainWindow", "裁剪末尾冗余静音"))
        self.actFilterIncluded.setText(_translate("MainWindow", "启用"))
        self.actSetIncluded.setText(_translate("MainWindow", "启用"))
        self.actSetExcluded.setText(_translate("MainWindow", "禁用"))
        self.actFilterExcluded.setText(_translate("MainWindow", "禁用"))
        self.actTempTool.setText(_translate("MainWindow", "临时工具"))
        self.actLocalizeLanguages.setText(_translate("MainWindow", "导入本地化语言"))
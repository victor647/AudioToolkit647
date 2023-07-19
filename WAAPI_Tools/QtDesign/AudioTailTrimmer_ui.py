# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AudioTailTrimmer.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AudioTailTrimmer(object):
    def setupUi(self, AudioTailTrimmer):
        AudioTailTrimmer.setObjectName("AudioTailTrimmer")
        AudioTailTrimmer.resize(698, 609)
        self.verticalLayout = QtWidgets.QVBoxLayout(AudioTailTrimmer)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnImportFiles = QtWidgets.QPushButton(AudioTailTrimmer)
        self.btnImportFiles.setObjectName("btnImportFiles")
        self.horizontalLayout.addWidget(self.btnImportFiles)
        self.btnImportFolder = QtWidgets.QPushButton(AudioTailTrimmer)
        self.btnImportFolder.setObjectName("btnImportFolder")
        self.horizontalLayout.addWidget(self.btnImportFolder)
        self.btnAnalyzeTails = QtWidgets.QPushButton(AudioTailTrimmer)
        self.btnAnalyzeTails.setObjectName("btnAnalyzeTails")
        self.horizontalLayout.addWidget(self.btnAnalyzeTails)
        self.btnStartTrim = QtWidgets.QPushButton(AudioTailTrimmer)
        self.btnStartTrim.setObjectName("btnStartTrim")
        self.horizontalLayout.addWidget(self.btnStartTrim)
        self.lblCutThreshold = QtWidgets.QLabel(AudioTailTrimmer)
        self.lblCutThreshold.setObjectName("lblCutThreshold")
        self.horizontalLayout.addWidget(self.lblCutThreshold)
        self.spbCutThreshold = QtWidgets.QSpinBox(AudioTailTrimmer)
        self.spbCutThreshold.setMinimum(-96)
        self.spbCutThreshold.setMaximum(0)
        self.spbCutThreshold.setProperty("value", -48)
        self.spbCutThreshold.setObjectName("spbCutThreshold")
        self.horizontalLayout.addWidget(self.spbCutThreshold)
        self.lblFadeDuration = QtWidgets.QLabel(AudioTailTrimmer)
        self.lblFadeDuration.setObjectName("lblFadeDuration")
        self.horizontalLayout.addWidget(self.lblFadeDuration)
        self.spbFadeDuration = QtWidgets.QDoubleSpinBox(AudioTailTrimmer)
        self.spbFadeDuration.setMinimum(0.01)
        self.spbFadeDuration.setMaximum(1.0)
        self.spbFadeDuration.setSingleStep(0.01)
        self.spbFadeDuration.setProperty("value", 0.1)
        self.spbFadeDuration.setObjectName("spbFadeDuration")
        self.horizontalLayout.addWidget(self.spbFadeDuration)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tblFileList = QtWidgets.QTableWidget(AudioTailTrimmer)
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

        self.retranslateUi(AudioTailTrimmer)
        QtCore.QMetaObject.connectSlotsByName(AudioTailTrimmer)

    def retranslateUi(self, AudioTailTrimmer):
        _translate = QtCore.QCoreApplication.translate
        AudioTailTrimmer.setWindowTitle(_translate("AudioTailTrimmer", "尾部冗余静音裁剪工具"))
        self.btnImportFiles.setText(_translate("AudioTailTrimmer", "导入文件"))
        self.btnImportFolder.setText(_translate("AudioTailTrimmer", "导入文件夹"))
        self.btnAnalyzeTails.setText(_translate("AudioTailTrimmer", "分析冗余时长"))
        self.btnStartTrim.setText(_translate("AudioTailTrimmer", "开始裁剪音尾"))
        self.lblCutThreshold.setText(_translate("AudioTailTrimmer", "静音判断阈值"))
        self.spbCutThreshold.setSuffix(_translate("AudioTailTrimmer", "dB"))
        self.lblFadeDuration.setText(_translate("AudioTailTrimmer", "淡出时长"))
        self.spbFadeDuration.setSuffix(_translate("AudioTailTrimmer", "s"))
        item = self.tblFileList.horizontalHeaderItem(0)
        item.setText(_translate("AudioTailTrimmer", "音频文件名"))
        item = self.tblFileList.horizontalHeaderItem(1)
        item.setText(_translate("AudioTailTrimmer", "总时长"))
        item = self.tblFileList.horizontalHeaderItem(2)
        item.setText(_translate("AudioTailTrimmer", "尾部静音时长"))
        item = self.tblFileList.horizontalHeaderItem(3)
        item.setText(_translate("AudioTailTrimmer", "处理状态"))

# Form implementation generated from reading ui file 'WorkUnitImporter.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_WorkUnitImporter(object):
    def setupUi(self, WorkUnitImporter):
        WorkUnitImporter.setObjectName("WorkUnitImporter")
        WorkUnitImporter.resize(356, 166)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(WorkUnitImporter)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(parent=WorkUnitImporter)
        self.groupBox.setMaximumSize(QtCore.QSize(120, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.cbxImportEffects = QtWidgets.QCheckBox(parent=self.groupBox)
        self.cbxImportEffects.setGeometry(QtCore.QRect(31, 120, 68, 20))
        self.cbxImportEffects.setChecked(True)
        self.cbxImportEffects.setObjectName("cbxImportEffects")
        self.cbxImportSourceFile = QtWidgets.QCheckBox(parent=self.groupBox)
        self.cbxImportSourceFile.setGeometry(QtCore.QRect(31, 20, 71, 20))
        self.cbxImportSourceFile.setChecked(True)
        self.cbxImportSourceFile.setObjectName("cbxImportSourceFile")
        self.cbxImportConversion = QtWidgets.QCheckBox(parent=self.groupBox)
        self.cbxImportConversion.setGeometry(QtCore.QRect(31, 80, 71, 20))
        self.cbxImportConversion.setChecked(True)
        self.cbxImportConversion.setObjectName("cbxImportConversion")
        self.cbxImportAttenuation = QtWidgets.QCheckBox(parent=self.groupBox)
        self.cbxImportAttenuation.setGeometry(QtCore.QRect(31, 60, 71, 20))
        self.cbxImportAttenuation.setChecked(True)
        self.cbxImportAttenuation.setObjectName("cbxImportAttenuation")
        self.cbxImportBus = QtWidgets.QCheckBox(parent=self.groupBox)
        self.cbxImportBus.setGeometry(QtCore.QRect(31, 100, 68, 20))
        self.cbxImportBus.setChecked(True)
        self.cbxImportBus.setObjectName("cbxImportBus")
        self.cbxImportRTPC = QtWidgets.QCheckBox(parent=self.groupBox)
        self.cbxImportRTPC.setGeometry(QtCore.QRect(31, 40, 53, 20))
        self.cbxImportRTPC.setChecked(True)
        self.cbxImportRTPC.setObjectName("cbxImportRTPC")
        self.horizontalLayout_2.addWidget(self.groupBox)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblMissingAction = QtWidgets.QLabel(parent=WorkUnitImporter)
        self.lblMissingAction.setObjectName("lblMissingAction")
        self.horizontalLayout.addWidget(self.lblMissingAction)
        self.cbbMissingAction = QtWidgets.QComboBox(parent=WorkUnitImporter)
        self.cbbMissingAction.setObjectName("cbbMissingAction")
        self.cbbMissingAction.addItem("")
        self.cbbMissingAction.addItem("")
        self.cbbMissingAction.addItem("")
        self.horizontalLayout.addWidget(self.cbbMissingAction)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.btnStartImport = QtWidgets.QPushButton(parent=WorkUnitImporter)
        self.btnStartImport.setObjectName("btnStartImport")
        self.verticalLayout.addWidget(self.btnStartImport)
        self.lblCurrentObject = QtWidgets.QLabel(parent=WorkUnitImporter)
        self.lblCurrentObject.setObjectName("lblCurrentObject")
        self.verticalLayout.addWidget(self.lblCurrentObject)
        self.lblObjectCount = QtWidgets.QLabel(parent=WorkUnitImporter)
        self.lblObjectCount.setObjectName("lblObjectCount")
        self.verticalLayout.addWidget(self.lblObjectCount)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(WorkUnitImporter)
        QtCore.QMetaObject.connectSlotsByName(WorkUnitImporter)

    def retranslateUi(self, WorkUnitImporter):
        _translate = QtCore.QCoreApplication.translate
        WorkUnitImporter.setWindowTitle(_translate("WorkUnitImporter", "WorkUnit导入工具"))
        self.groupBox.setTitle(_translate("WorkUnitImporter", "导入内容"))
        self.cbxImportEffects.setText(_translate("WorkUnitImporter", "效果器"))
        self.cbxImportSourceFile.setText(_translate("WorkUnitImporter", "音频样本"))
        self.cbxImportConversion.setText(_translate("WorkUnitImporter", "压缩设置"))
        self.cbxImportAttenuation.setText(_translate("WorkUnitImporter", "衰减曲线"))
        self.cbxImportBus.setText(_translate("WorkUnitImporter", "输出Bus"))
        self.cbxImportRTPC.setText(_translate("WorkUnitImporter", "RTPC"))
        self.lblMissingAction.setText(_translate("WorkUnitImporter", "找不到同名对象时"))
        self.cbbMissingAction.setItemText(0, _translate("WorkUnitImporter", "创建"))
        self.cbbMissingAction.setItemText(1, _translate("WorkUnitImporter", "警告"))
        self.cbbMissingAction.setItemText(2, _translate("WorkUnitImporter", "忽略"))
        self.btnStartImport.setText(_translate("WorkUnitImporter", "选择文件并导入"))
        self.lblCurrentObject.setText(_translate("WorkUnitImporter", " "))
        self.lblObjectCount.setText(_translate("WorkUnitImporter", " "))

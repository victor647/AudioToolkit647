# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ReplaceSourceFile.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ReplaceSourceFile(object):
    def setupUi(self, ReplaceSourceFile):
        ReplaceSourceFile.setObjectName("ReplaceSourceFile")
        ReplaceSourceFile.resize(198, 97)
        self.verticalLayout = QtWidgets.QVBoxLayout(ReplaceSourceFile)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblFindText = QtWidgets.QLabel(ReplaceSourceFile)
        self.lblFindText.setMinimumSize(QtCore.QSize(75, 0))
        self.lblFindText.setObjectName("lblFindText")
        self.horizontalLayout.addWidget(self.lblFindText)
        self.iptFindName = QtWidgets.QLineEdit(ReplaceSourceFile)
        self.iptFindName.setObjectName("iptFindName")
        self.horizontalLayout.addWidget(self.iptFindName)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lblReplaceText = QtWidgets.QLabel(ReplaceSourceFile)
        self.lblReplaceText.setMinimumSize(QtCore.QSize(75, 0))
        self.lblReplaceText.setObjectName("lblReplaceText")
        self.horizontalLayout_2.addWidget(self.lblReplaceText)
        self.iptReplaceName = QtWidgets.QLineEdit(ReplaceSourceFile)
        self.iptReplaceName.setObjectName("iptReplaceName")
        self.horizontalLayout_2.addWidget(self.iptReplaceName)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.btnDoReplace = QtWidgets.QPushButton(ReplaceSourceFile)
        self.btnDoReplace.setObjectName("btnDoReplace")
        self.verticalLayout.addWidget(self.btnDoReplace)

        self.retranslateUi(ReplaceSourceFile)
        QtCore.QMetaObject.connectSlotsByName(ReplaceSourceFile)

    def retranslateUi(self, ReplaceSourceFile):
        _translate = QtCore.QCoreApplication.translate
        ReplaceSourceFile.setWindowTitle(_translate("ReplaceSourceFile", "ReplaceSourceFile"))
        self.lblFindText.setText(_translate("ReplaceSourceFile", "Find Text"))
        self.lblReplaceText.setText(_translate("ReplaceSourceFile", "Replace With"))
        self.btnDoReplace.setText(_translate("ReplaceSourceFile", "Execute"))

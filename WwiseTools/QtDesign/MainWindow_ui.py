# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(511, 315)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(10, 50, 181, 131))
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnCreateBanks = QtWidgets.QPushButton(self.groupBox)
        self.btnCreateBanks.setObjectName("btnCreateBanks")
        self.verticalLayout.addWidget(self.btnCreateBanks)
        self.btnGetBankSize = QtWidgets.QPushButton(self.groupBox)
        self.btnGetBankSize.setObjectName("btnGetBankSize")
        self.verticalLayout.addWidget(self.btnGetBankSize)
        self.btnApplySourceEdit = QtWidgets.QPushButton(self.groupBox)
        self.btnApplySourceEdit.setObjectName("btnApplySourceEdit")
        self.verticalLayout.addWidget(self.btnApplySourceEdit)
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 491, 25))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblWaapiPort = QtWidgets.QLabel(self.layoutWidget)
        self.lblWaapiPort.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lblWaapiPort.setObjectName("lblWaapiPort")
        self.horizontalLayout.addWidget(self.lblWaapiPort)
        self.spbWaapiPort = QtWidgets.QSpinBox(self.layoutWidget)
        self.spbWaapiPort.setMaximumSize(QtCore.QSize(60, 16777215))
        self.spbWaapiPort.setMinimum(1000)
        self.spbWaapiPort.setMaximum(9999)
        self.spbWaapiPort.setProperty("value", 8080)
        self.spbWaapiPort.setObjectName("spbWaapiPort")
        self.horizontalLayout.addWidget(self.spbWaapiPort)
        self.btnWaapiConnect = QtWidgets.QPushButton(self.layoutWidget)
        self.btnWaapiConnect.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btnWaapiConnect.setObjectName("btnWaapiConnect")
        self.horizontalLayout.addWidget(self.btnWaapiConnect)
        self.lblWaapiStatus = QtWidgets.QLabel(self.layoutWidget)
        self.lblWaapiStatus.setMinimumSize(QtCore.QSize(150, 0))
        self.lblWaapiStatus.setObjectName("lblWaapiStatus")
        self.horizontalLayout.addWidget(self.lblWaapiStatus)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 511, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btnCreateBanks.clicked.connect(MainWindow.create_bank_per_object)
        self.btnGetBankSize.clicked.connect(MainWindow.calculate_bank_size)
        self.btnWaapiConnect.clicked.connect(MainWindow.connect_to_wwise)
        self.btnApplySourceEdit.clicked.connect(MainWindow.apply_source_edits)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "WwiseTools"))
        self.groupBox.setTitle(_translate("MainWindow", "Selection Batch Process"))
        self.btnCreateBanks.setText(_translate("MainWindow", "Create Bank per Object"))
        self.btnGetBankSize.setText(_translate("MainWindow", "Calculate Bank Size"))
        self.btnApplySourceEdit.setText(_translate("MainWindow", "Apply Edits to Source Files"))
        self.lblWaapiPort.setText(_translate("MainWindow", "WAAPI Port"))
        self.btnWaapiConnect.setText(_translate("MainWindow", "Connect"))
        self.lblWaapiStatus.setText(_translate("MainWindow", "Wwise not connected..."))

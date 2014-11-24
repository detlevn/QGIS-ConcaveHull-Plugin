# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_concavehull.ui'
#
# Created: Mon Nov 24 16:14:13 2014
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ConcaveHull(object):
    def setupUi(self, ConcaveHull):
        ConcaveHull.setObjectName(_fromUtf8("ConcaveHull"))
        ConcaveHull.resize(327, 319)
        self.verticalLayout = QtGui.QVBoxLayout(ConcaveHull)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(ConcaveHull)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 60))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 62))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.horizontalSlider = QtGui.QSlider(self.groupBox)
        self.horizontalSlider.setMinimum(2)
        self.horizontalSlider.setMaximum(25)
        self.horizontalSlider.setPageStep(5)
        self.horizontalSlider.setProperty("value", 3)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.horizontalSlider.setTickInterval(2)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))
        self.horizontalLayout.addWidget(self.horizontalSlider)
        self.sb_neighbors = QtGui.QSpinBox(self.groupBox)
        self.sb_neighbors.setMinimum(2)
        self.sb_neighbors.setMaximum(25)
        self.sb_neighbors.setProperty("value", 3)
        self.sb_neighbors.setObjectName(_fromUtf8("sb_neighbors"))
        self.horizontalLayout.addWidget(self.sb_neighbors)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ConcaveHull)
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.ls_layers = QtGui.QListWidget(self.groupBox_2)
        self.ls_layers.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.ls_layers.setObjectName(_fromUtf8("ls_layers"))
        self.verticalLayout_2.addWidget(self.ls_layers)
        self.cb_selected_only = QtGui.QCheckBox(self.groupBox_2)
        self.cb_selected_only.setObjectName(_fromUtf8("cb_selected_only"))
        self.verticalLayout_2.addWidget(self.cb_selected_only)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(ConcaveHull)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.cb_output = QtGui.QComboBox(self.groupBox_3)
        self.cb_output.setEditable(True)
        self.cb_output.setObjectName(_fromUtf8("cb_output"))
        self.verticalLayout_3.addWidget(self.cb_output)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.buttonBox = QtGui.QDialogButtonBox(ConcaveHull)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ConcaveHull)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConcaveHull.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConcaveHull.reject)
        QtCore.QObject.connect(self.horizontalSlider, QtCore.SIGNAL(_fromUtf8("sliderMoved(int)")), self.sb_neighbors.setValue)
        QtCore.QObject.connect(self.sb_neighbors, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.horizontalSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(ConcaveHull)

    def retranslateUi(self, ConcaveHull):
        ConcaveHull.setWindowTitle(_translate("ConcaveHull", "ConcaveHull", None))
        self.groupBox.setTitle(_translate("ConcaveHull", "Anzahl Nachbarn", None))
        self.groupBox_2.setTitle(_translate("ConcaveHull", "Eingabe", None))
        self.cb_selected_only.setText(_translate("ConcaveHull", "nur selektierte Objekte", None))
        self.groupBox_3.setTitle(_translate("ConcaveHull", "Ergebnis", None))
        self.cb_output.setToolTip(_translate("ConcaveHull", "Layername eingeben oder einen Layer aus der Liste wählen", None))


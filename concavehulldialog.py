# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ConcaveHullDialog
                                 A QGIS plugin
 Computes a concave hull containing a set of features
                             -------------------
        begin                : 2014-11-11
        copyright            : (C) 2014 by Detlev Neumann, Dr. Neumann Consulting - Geospatial Services 
        email                : dneumann@geospatial-services.de 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_concavehull import Ui_ConcaveHull

import os

class ConcaveHullDialog(QtGui.QDialog, Ui_ConcaveHull):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # enable Ok button only if at least one input layer is selected
        self.ls_layers.itemSelectionChanged.connect(self.ls_layers_changed)

        # connect events to handlers to ensure proper behaviour
        self.bt_file_browser.clicked.connect(self.file_browser)
        self.rb_shapefile.toggled.connect(self.rb_shapefile_toggled)
        self.rb_existing_layer.toggled.connect(self.rb_existing_layer_toggled)
        self.rb_new_memory_layer.toggled.connect(self.rb_new_memory_layer_toggled)
        self.ed_memory_layer.textChanged.connect(self.rb_new_memory_layer_toggled)
        self.ed_output_layer.textChanged.connect(self.rb_shapefile_toggled)

    def ls_layers_changed(self):
        if self.ls_layers.selectedItems():
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    def rb_shapefile_toggled(self):
        if self.rb_shapefile.isChecked():
            if self.ed_output_layer.text() and self.ls_layers.selectedItems():
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    def rb_existing_layer_toggled(self):
        if self.rb_existing_layer.isChecked():
            if self.cb_output.currentIndex() > -1 and self.ls_layers.selectedItems():
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    def rb_new_memory_layer_toggled(self):
        if self.rb_new_memory_layer.isChecked():
            if self.ed_memory_layer.text() and self.ls_layers.selectedItems():
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    def file_browser(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Open file", "", "Shapefile (*.shp);;All files (*)")
        filename = os.path.splitext(str(filename))[0]+".shp"
        layer_name = os.path.splitext(os.path.basename(str(filename)))[0]
        if layer_name == ".shp":
            return
        self.ed_output_layer.setText(filename)

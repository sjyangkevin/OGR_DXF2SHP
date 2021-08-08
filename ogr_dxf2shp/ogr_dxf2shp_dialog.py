# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OGR_DXF2SHPDialog
                                 A QGIS plugin
 load and process DXF file and output it as Shapefile
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2021-08-06
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Shijin (Kevin) Yang
        email                : kevinsjy997@gmail.com
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

import os

from PyQt5.QtWidgets import QFileDialog, QListWidgetItem, QDialogButtonBox

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.core import QgsProject, QgsVectorLayer
from .modules.drivers import DXF2SHP_Driver
from osgeo import osr

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ogr_dxf2shp_dialog_base.ui'))


class OGR_DXF2SHPDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(OGR_DXF2SHPDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.Input_File_Select_PushButton.clicked.connect(self.open_file)
        self.Input_File_LineEdit.textChanged.connect(self.input_file_change_handler)
        
        self.Output_Dir_Select_PushButton.clicked.connect(self.save_file)
        self.Output_Dir_LineEdit.textChanged.connect(self.output_dir_change_handler)

        self.Output_File_Name_LineEdit.textChanged.connect(self.output_name_change_handler)

        self.Original_Projection_SelectWidget.crsChanged.connect(self.original_projection_change_handler)
        self.Target_Projection_SelectWidget.crsChanged.connect(self.target_projection_change_handler)

        self.Loaded_Layers_SelectAll_PushButton.clicked.connect(self.set_listwidget_item_all_select)
        self.Loaded_Layers_UnSelectAll_PushButton.clicked.connect(self.clear_listwidget_item_selection)
        
        # multi-selection
        self.Loaded_Layers_ListWidget.setSelectionMode(2)
        self.Loaded_Layers_ListWidget.itemSelectionChanged.connect(self.listwidget_selection_change_handler)

        self.Attribute_File_PushButton.clicked.connect(self.open_attribute_file)
        self.Attribute_File_LineEdit.textChanged.connect(self.attribute_file_change_handler)
        
        # single-selection
        self.Attr_Index_Selection_ListWidget.setSelectionMode(1)
        self.Attr_Index_Selection_ListWidget.itemSelectionChanged.connect(self.attribute_listwidget_selection_change_handler)

        self.Attr_Index_Validate_PushButton.setEnabled(False)
        self.Attr_Index_Validate_PushButton.clicked.connect(self.validate_attribute_file_handler)

        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)

        self.DXF2SHP_Driver = DXF2SHP_Driver() 
    

    def open_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select an DXF file",
            "",
            "All Files (*);;DXF Files (*.dxf)"
        )

        self.Input_File_LineEdit.setText(file_path)


    def open_attribute_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select an DXF file",
            ""
        )
        self.DXF2SHP_Driver.ATTRIBUTE_FILE = file_path
        self.Attribute_File_LineEdit.setText(file_path)

        self.Attr_Index_Validate_Label.setText("Please Click 'Validate' when 'Attribute File' is Used")
        self.Attr_Index_Validate_Label.setStyleSheet("color: black")

        self.validate_input()


    def save_file(self):
        file_path = QFileDialog.getExistingDirectory(
            self,
            "Select an Output Directory",
            ""
        )
        self.Output_Dir_LineEdit.setText(file_path)


    def input_file_change_handler(self):
        file_path = self.Input_File_LineEdit.text()
        valid_flag = False
        self.clear_listwidget_item_selection()
        self.Loaded_Layers_ListWidget.clear()

        if file_path == "":
            self.Input_File_Validate_Label.setText("(Required)")
            self.Input_File_Validate_Label.setStyleSheet("color: red")
        else:
            if os.path.exists(file_path) and \
                os.path.basename(file_path).split('.')[1] == 'dxf' or \
                os.path.basename(file_path).split('.')[1] == 'DXF':
                
                self.Input_File_Validate_Label.setText("(Valid)")
                self.Input_File_Validate_Label.setStyleSheet("color: green")

                valid_flag = True
            else:
                self.Input_File_Validate_Label.setText("(Invalid)")
                self.Input_File_Validate_Label.setStyleSheet("color: red")
        
        if valid_flag:
            self.DXF2SHP_Driver.set_input_file(file_path)
            self.DXF2SHP_Driver.create_dxf_source()
            self.DXF2SHP_Driver.set_dxf_layers()

            self.DXF2SHP_Driver.set_dxf_layers()
            for i in range(len(self.DXF2SHP_Driver.DXF_LAYERS)):
                item = QListWidgetItem(self.DXF2SHP_Driver.DXF_LAYERS[i], self.Loaded_Layers_ListWidget)
                self.Loaded_Layers_ListWidget.addItem(item)
                item.setSelected(True)
            
            self.DXF2SHP_Driver.SELECTED_DXF_LAYERS = self.Loaded_Layers_ListWidget.selectedItems()

        else:
            self.DXF2SHP_Driver.input_file = None
            self.DXF2SHP_Driver.DXF_SOURCE = None
            self.DXF2SHP_Driver.DXF_LAYERS = []
            self.DXF2SHP_Driver.SELECTED_DXF_LAYERS = []

        self.validate_input()


    def output_dir_change_handler(self):
        file_path = self.Output_Dir_LineEdit.text()
        valid_flag = False 

        if file_path == "":
            self.Output_Dir_Validate_Label.setText("(Required)")
            self.Output_Dir_Validate_Label.setStyleSheet("color: red")
        else:
            if os.path.isdir(file_path):
                self.Output_Dir_Validate_Label.setText("(Valid)")
                self.Output_Dir_Validate_Label.setStyleSheet("color: green")

                valid_flag = True
            else:
                self.Output_Dir_Validate_Label.setText("(Invalid)")
                self.Output_Dir_Validate_Label.setStyleSheet("color: red")

        if valid_flag:
            
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            self.DXF2SHP_Driver.set_output_dir(file_path)

            if os.path.exists(file_path):
                self.DXF2SHP_Driver.ESRI_DRIVER.DeleteDataSource(file_path)

            self.DXF2SHP_Driver.create_esri_source()
        else:
            self.DXF2SHP_Driver.set_output_dir(None)
            self.DXF2SHP_Driver.ESRI_SOURCE = None

        self.validate_input()


    def output_name_change_handler(self):
        output_name = self.Output_File_Name_LineEdit.text()
        self.DXF2SHP_Driver.set_output_name(output_name)

        self.validate_input()

    def attribute_file_change_handler(self):
        file_path = self.Attribute_File_LineEdit.text()
        valid_flag = False
        self.Attr_Index_Selection_ListWidget.clear()

        if file_path == "":
            self.Attribute_File_Validate_Label.setText("(Optional)")
            self.Attribute_File_Validate_Label.setStyleSheet("color: black")
        else:
            if os.path.basename(file_path).split('.')[1] == "csv":
                self.Attribute_File_Validate_Label.setText("(Valid)")
                self.Attribute_File_Validate_Label.setStyleSheet("color: green")

                valid_flag = True
            else:
                self.Attribute_File_Validate_Label.setText("(Need CSV)")
                self.Attribute_File_Validate_Label.setStyleSheet("color: red")
                self.DXF2SHP_Driver.set_attribute_file(None)

        if valid_flag:
            self.DXF2SHP_Driver.set_attribute_file(file_path)
            self.Attr_Index_Validate_PushButton.setEnabled(True)

            attr_cols, _ = self.DXF2SHP_Driver.read_attribute_file()
        
            self.Attr_Index_Selection_ListWidget.addItems(attr_cols)
        else:
            self.DXF2SHP_Driver.set_attribute_file(None)
            self.DXF2SHP_Driver.SELECTED_ATTRIBUTE_COLUMN = None
            self.Attr_Index_Validate_PushButton.setEnabled(False)

        self.validate_input()


    def original_projection_change_handler(self):
        if self.Original_Projection_SelectWidget.crs().isValid():
            self.Original_Projection_Validate_Label.setText("(Valid)")
            self.Original_Projection_Validate_Label.setStyleSheet("color: green")

            EPSG_ID = int(self.Original_Projection_SelectWidget.crs().authid().split(':')[1])
            self.DXF2SHP_Driver.ORIGINAL_PROJECTION.ImportFromEPSG(EPSG_ID)

        else:
            self.Target_Projection_Validate_Label.setText("(Invalid)")
            self.Target_Projection_Validate_Label.setStyleSheet("color: red")
            self.DXF2SHP_Driver.ORIGINAL_PROJECTION = osr.SpatialReference()

        self.validate_input()


    def target_projection_change_handler(self):
        if self.Target_Projection_SelectWidget.crs().isValid():
            self.Target_Projection_Validate_Label.setText("(Valid)")
            self.Target_Projection_Validate_Label.setStyleSheet("color: green")

            EPSG_ID = int(self.Target_Projection_SelectWidget.crs().authid().split(':')[1])
            self.DXF2SHP_Driver.TARGET_PROJECTION.ImportFromEPSG(EPSG_ID)

        else:
            self.Target_Projection_Validate_Label.setText("(Invalid)")
            self.Target_Projection_Validate_Label.setStyleSheet("color: red")
            self.DXF2SHP_Driver.TARGET_PROJECTION = osr.SpatialReference()

        self.validate_input()

    def clear_listwidget_item_selection(self):
        for i in range(self.Loaded_Layers_ListWidget.count()):
            item = self.Loaded_Layers_ListWidget.item(i)
            item.setSelected(False)
        self.Loaded_Layers_ListWidget.setFocus()
            
    
    def set_listwidget_item_all_select(self):
        for i in range(self.Loaded_Layers_ListWidget.count()):
            item = self.Loaded_Layers_ListWidget.item(i)
            item.setSelected(True)
        self.Loaded_Layers_ListWidget.setFocus()

    
    def listwidget_selection_change_handler(self):
        self.DXF2SHP_Driver.SELECTED_DXF_LAYERS = [item.text() for item in self.Loaded_Layers_ListWidget.selectedItems()]
        self.Attr_Index_Validate_Label.setText("Please Click 'Validate' when 'Attribute File' is Used")
        self.Attr_Index_Validate_Label.setStyleSheet("color: black")

        self.validate_input()


    def attribute_listwidget_selection_change_handler(self):
        # only allow to select a single item, this function return a list, get the first one
        if len(self.Attr_Index_Selection_ListWidget.selectedItems()) > 0:
            self.DXF2SHP_Driver.SELECTED_ATTRIBUTE_COLUMN = self.Attr_Index_Selection_ListWidget.selectedItems()[0].text()
            self.Attr_Index_Validate_Label.setText("Please Click 'Validate' when 'Attribute File' is Used")
            self.Attr_Index_Validate_Label.setStyleSheet("color: black")

        self.validate_input()


    def validate_attribute_file_handler(self):
        
        column = self.DXF2SHP_Driver.SELECTED_ATTRIBUTE_COLUMN
        _, attr_data = self.DXF2SHP_Driver.read_attribute_file()

        if len(attr_data) != len(self.DXF2SHP_Driver.SELECTED_DXF_LAYERS):
            self.Attr_Index_Validate_Label.setText("number of records not match")
            self.Attr_Index_Validate_Label.setStyleSheet("color: red")
            return

        if len(self.DXF2SHP_Driver.SELECTED_DXF_LAYERS) == 0 and len(attr_data) > 0:
            self.Attr_Index_Validate_Label.setText("please select DXF layers")
            self.Attr_Index_Validate_Label.setStyleSheet("color: red")
            return

        if self.Attribute_File_Validate_Label.text() == "(Valid)" and \
            self.DXF2SHP_Driver.SELECTED_ATTRIBUTE_COLUMN is None:
            self.Attr_Index_Validate_Label.setText("please select a column for mapping")
            self.Attr_Index_Validate_Label.setStyleSheet("color: red")
            return

        for row in attr_data:
            if row[column] not in self.DXF2SHP_Driver.SELECTED_DXF_LAYERS:
                self.Attr_Index_Validate_Label.setText("records and layers not match")
                self.Attr_Index_Validate_Label.setStyleSheet("color: red")
                return

        self.Attr_Index_Validate_Label.setText("Valid")
        self.Attr_Index_Validate_Label.setStyleSheet("color: green")

        self.validate_input()


    def validate_input(self):
        valid_flag = True

        if self.Input_File_Validate_Label.text() != "(Valid)":
            valid_flag = False
        
        if self.Output_Dir_Validate_Label.text() != "(Valid)":
            valid_flag = False

        if self.Original_Projection_Validate_Label.text() != "(Valid)":
            valid_flag = False

        if self.Target_Projection_Validate_Label.text() != "(Valid)":
            valid_flag = False

        if self.Attribute_File_Validate_Label.text() == "(Valid)":
            if self.Attr_Index_Validate_Label.text() != "Valid":
                valid_flag = False
        
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(valid_flag)

    def add_to_layers(self):
        if self.Add_Output_To_Layers_CheckBox.isChecked():
            shapefile = QgsVectorLayer(self.DXF2SHP_Driver.output_dir, self.DXF2SHP_Driver.output_name, "ogr")
            QgsProject.instance().addMapLayer(shapefile)
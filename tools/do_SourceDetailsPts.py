# -*- coding: utf-8 -*-
"""
/***************************************************************************
 opeNoise

 Qgis Plugin to compute noise levels

                             -------------------
        begin                : March 2014
        copyright            : (C) 2014 by Arpa Piemonte
        email                : s.masera@arpa.piemonte.it
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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *

import os, imp
import traceback

from ui_SourceDetailsPts import Ui_SourceDetailsPts_window


import on_Settings

# import VectorWriter
try:
    # Qgis from 2.0 to 2.4
    from processing.core.VectorWriter import VectorWriter
except:
    # Qgis from 2.6
    from processing.tools.vector import VectorWriter


class Dialog(QDialog,Ui_SourceDetailsPts_window):
    
    def __init__(self, iface,layer_name):
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.layer_name = layer_name
        
        # start definition
        self.POWER_P_emission_comboBoxes_dict = {'POWER_P_gen' : self.POWER_P_L_gen_comboBox, 
                                    'POWER_P_day' : self.POWER_P_L_day_comboBox, 
                                    'POWER_P_eve' : self.POWER_P_L_eve_comboBox, 
                                    'POWER_P_nig' : self.POWER_P_L_nig_comboBox
                                    }

        self.all_emission_comboBoxes = [self.POWER_P_L_gen_comboBox, self.POWER_P_L_day_comboBox, self.POWER_P_L_eve_comboBox, self.POWER_P_L_nig_comboBox]
           
        self.source_checkBoxes = [self.POWER_P_L_gen_checkBox,self.POWER_P_L_day_checkBox,self.POWER_P_L_eve_checkBox,self.POWER_P_L_nig_checkBox]
           
        self.source_POWER_P_period_checkBoxes = [self.POWER_P_L_day_checkBox,self.POWER_P_L_eve_checkBox,self.POWER_P_L_nig_checkBox]
        # end definitions        
        
        self.source_fields_update() 

        for source_checkBox in self.source_checkBoxes:
            source_checkBox.setChecked(0)
            QObject.connect(source_checkBox, SIGNAL("toggled(bool)"), self.source_checkBox_update)
            
        QObject.connect(self.POWER_P_L_gen_checkBox, SIGNAL("toggled(bool)"), self.source_checkBox_update)
        
        self.setToolTips()
        
        self.reload_settings()
        
        
    def source_fields_update(self):
        
        source_layer = QgsMapLayerRegistry.instance().mapLayersByName(self.layer_name)[0]
        source_layer_fields = list(source_layer.dataProvider().fields())

        source_layer_fields_labels = [""]

        for f in source_layer_fields:
#            if f.type() == QVariant.Int or f.type() == QVariant.Double:         
                source_layer_fields_labels.append(unicode(f.name()))
        
        
        for comboBox in self.all_emission_comboBoxes:
            comboBox.clear()
            comboBox.setEnabled(False)
        
            for label in source_layer_fields_labels:
                comboBox.addItem(label)


    def source_checkBox_update(self):

        # POWER_P
        if self.POWER_P_L_gen_checkBox.isChecked():
            self.POWER_P_L_gen_comboBox.setEnabled(True)   
        else:
            self.POWER_P_L_gen_comboBox.setEnabled(False)    
        if self.POWER_P_L_day_checkBox.isChecked():
            self.POWER_P_L_day_comboBox.setEnabled(True) 
        else:
            self.POWER_P_L_day_comboBox.setEnabled(False)    
        if self.POWER_P_L_eve_checkBox.isChecked():
            self.POWER_P_L_eve_comboBox.setEnabled(True)    
        else:
            self.POWER_P_L_eve_comboBox.setEnabled(False)    
        if self.POWER_P_L_nig_checkBox.isChecked():
            self.POWER_P_L_nig_comboBox.setEnabled(True)    
        else:
            self.POWER_P_L_nig_comboBox.setEnabled(False)    
       
        self.setToolTips()


    def setToolTips(self):  
        
        for comboBox in self.all_emission_comboBoxes:
            
            if comboBox.isEnabled() == True:
                string = "Choose from a numeric field of the source layer"
                comboBox.setToolTip(string)
            else:
                comboBox.setToolTip("")
        

    def check(self):
        
        for comboBox in self.all_emission_comboBoxes:
            
            if comboBox.isEnabled() == True and comboBox.currentText() == "":
                QMessageBox.information(self, self.tr("opeNoise - Calculate Noise Levels"), self.tr("Please select a field."))
                return False

        count = 0
        for key in self.POWER_P_emission_comboBoxes_dict.keys():
            comboBox = self.POWER_P_emission_comboBoxes_dict[key]
            if comboBox.isEnabled():
                count = 1
        if count == 0:
            QMessageBox.information(self, self.tr("opeNoise - Calculate Noise Levels"), self.tr("Please specify at least one power for a reference period."))
            return False

        return True
    

    def write_settings(self):
        
        settings = {}
        
        settings['implementation_pts'] = 'True'
                
        if self.POWER_P_L_gen_checkBox.isChecked():
            settings['period_pts_gen'] = 'True'
        else:
            settings['period_pts_gen'] = 'False'
        if self.POWER_P_L_day_checkBox.isChecked():
            settings['period_pts_day'] = 'True'
        else:
            settings['period_pts_day'] = 'False'
        if self.POWER_P_L_eve_checkBox.isChecked():
            settings['period_pts_eve'] = 'True'
        else:
            settings['period_pts_eve'] = 'False'
        if self.POWER_P_L_nig_checkBox.isChecked():
            settings['period_pts_nig'] = 'True'
        else:
            settings['period_pts_nig'] = 'False'


        for key in self.POWER_P_emission_comboBoxes_dict.keys():
            if self.POWER_P_emission_comboBoxes_dict[key].isEnabled():
                settings[key] = self.POWER_P_emission_comboBoxes_dict[key].currentText()
            else:
                settings[key] = ''
           
        on_Settings.setSettings(settings)


    def reload_settings(self):

        try:
            settings = on_Settings.getAllSettings()  
            
            if settings['period_pts_gen'] == "True":
                self.POWER_P_L_gen_checkBox.setChecked(1)
            if settings['period_pts_day'] == "True":
                self.POWER_P_L_day_checkBox.setChecked(1)
            if settings['period_pts_eve'] == "True":
                self.POWER_P_L_eve_checkBox.setChecked(1)
            if settings['period_pts_nig'] == "True":
                self.POWER_P_L_nig_checkBox.setChecked(1)
    
            for key in self.POWER_P_emission_comboBoxes_dict.keys():
                if settings[key] is not None:
                    idx = self.POWER_P_emission_comboBoxes_dict[key].findText(settings[key])
                    self.POWER_P_emission_comboBoxes_dict[key].setCurrentIndex(idx)        
        
            self.source_checkBox_update()

        except:
            
            QMessageBox.information(self, self.tr("opeNoise - Calculate Noise Levels"), self.tr("Sorry, but somethigs wrong in import last settings."))
            
            
    def accept(self):
        
        if self.check() == False:
            return
        
        self.write_settings()
       
        self.close()

   

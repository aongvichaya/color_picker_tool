################################################################################
## Color Picker Tool
## Created by Aong Pipeline 2023/08/04
##
## Description
## For select color from color palette and assign it to geo or face
## With utilites button Reassign Preview Shade and Delete Unused Nodes
################################################################################

#Standard Lib
import os
import maya.cmds as cmds
import math

##GUI Modules
try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import QUiLoader
    from shiboken2 import wrapInstance


except:
    from PySide import QtCore, QtGui
    from PySide.QtGui import *
    from PySide.QtUiTools import QUiLoader
    from PySide.QtCore import *
    from shiboken import wrapInstance

##Snow Modules
from snow.common.lib import web_browser
from snow.common.lib import config as snow_config
from snow.maya.lib.widgets import Maya_Main_Window
from snow.common.lib import code_logging
from snow.maya.tools.color_gpu import color_gpu
import color_picker_helper as helper

#Global Var
logger = code_logging.create_log(__name__)
module_path = os.path.abspath(os.path.join(__file__, "../"))
YAML_PATH = snow_config.get_tool_config(
                                module=__file__,
                                filename='color_shd_list.yaml')
ICON_PATH = 'P:/pipeline/icons'
MANUAL_URL = 'https://igloostudioth.atlassian.net/l/cp/eU8pCMXn'
data = snow_config.yaml.read(YAML_PATH)

class ColorPicker(QtWidgets.QWidget):
    def __init__(self, parent= None):
        super(ColorPicker, self).__init__(parent)
        self.path = "{}/color_picker.ui".format(module_path)
        self.ui_file = QtCore.QFile(self.path)
        self.ui_file.open(QtCore.QFile.ReadOnly)
        self.loader = QUiLoader()
        self.window = self.loader.load(self.ui_file, parent)
        self.ui_file.close()
        
        # set ui 
        self.cbb_type = data.get('Shading Type')
        self.basic_color_list=data['Color Palatte']['Basic Color']
        self.trans_color_list=data['Color Palatte']['Trans Color']
        self.second_layout = self.window.findChild(QVBoxLayout,'second_layout')
        self.create_button(columns=6,color_list=self.basic_color_list,grpbox='first_groupbox',grpbox_layout='gridLayout_5',trans=False)
        self.create_button(columns=6,color_list=self.trans_color_list,grpbox='second_groupbox',grpbox_layout='gridLayout_2',trans=True)      
        self.third_groupbox = self.window.findChild(QGroupBox,'third_groupbox')
        self.third_groupbox_layout = self.window.findChild(QVBoxLayout,'verticalLayout_2')
        self.third_groupbox.setLayout(self.third_groupbox_layout)    
        self.second_layout.addWidget(self.third_groupbox)
        self.window.shadetype_box.addItems(self.cbb_type)
        self.manual_icon = QIcon(ICON_PATH + "/snow_layer_manager/help.png")
        self.window.manual_btn.setFlat(True)
        self.window.manual_btn.setIcon(self.manual_icon)
        self.window.manual_btn.setIconSize(QSize(25, 25))
        #connect signal
        self.window.manual_btn.clicked.connect(self.open_manual)
        self.window.del_unused_nodes_btn.clicked.connect(self.delete_nodes)
        self.window.return_prev_btn.clicked.connect(self.return_prev_shd)
        self.window.color_gpu_btn.clicked.connect(self.color_gpu)

        
    def open_manual(self):
        """
        open manual page
        """
        web_browser.open_browser(MANUAL_URL)

    def shade_assign(self,trans,color_name):
        """to assign shade using helper.create_shader and check trans bool and get color name from button

        Args:
            trans (bool): check transparency condition if true color will be Trans Color in YAML
            color_name (str): color name from YAML use set name of button and using in finding color rgb
        """
        logger.info('Assign Color:[{}] '.format(color_name))
        curr_shade_type = self.window.shadetype_box.currentText()
        if trans :
            color = data['Color Palatte']['Trans Color'][color_name]
            helper.create_shader(color_name, meshes=cmds.ls(sl=True), trans=True, node_type=curr_shade_type,color=color)
        else:
            color = data['Color Palatte']['Basic Color'][color_name]
            helper.create_shader(color_name, meshes=cmds.ls(sl=True), trans=False, node_type=curr_shade_type,color=color)

    def delete_nodes(self):
        """to delete unused nodes
        """
        helper.delete_unused_nodes()
    
    def return_prev_shd(self):
        """to return shd to orignal shade from reference
        """
        helper.return_original_shd()
    
    def color_gpu(self):
        """to generate color for gpu
        """
        color_gpu.color_gpu()
    
    def create_button(self,columns,color_list,grpbox,grpbox_layout,trans):
        """To create button using for loop with rows and columns as range to add button in style of row and column

        Args:
            columns (int): to set the column of button that we want 
            color_list (dict): color key and values as dict Reading from color_shd_list YAML file
            grpbox (str): name of groupbox in ui
            grpbox_layout (str): name of groupbox layout in ui
            trans (bool): to send trans to check if have trans or not
        """
        i=0
        rows_from_len = float(len(color_list)) / columns
        rows= int(math.ceil(rows_from_len))
        for row in range(rows):
            for column in range(columns):
                self.btn_color=color_list.values()
                self.rgb_code = tuple([x * 255.0 for x in self.btn_color[i]])
                self.buttons = QPushButton(color_list.keys()[i],self)
                self.buttons.clicked.connect(lambda x=color_list.keys()[i],y=trans: self.shade_assign(y,x))
                self.buttons.setStyleSheet('background-color:rgb{};color:transparent;width: 10px;height: 10px;'.format(self.rgb_code))
                self.groupbox = self.window.findChild(QGroupBox, grpbox)
                self.groupbox_layout = self.window.findChild(QGridLayout, grpbox_layout)    
                self.groupbox_layout.addWidget(self.buttons,row+1, column)
                i += 1
                if i == len(color_list) : break
            self.groupbox.setLayout(self.groupbox_layout)
            self.groupbox_layout.setContentsMargins(0,0,0,0)
            self.groupbox_layout.setSpacing(0)
            self.second_layout.addWidget(self.groupbox)
    
def main():
    global ui
    app = Maya_Main_Window

    try:
        ui.window.destroy()
        ui.window.close()
        ui.window.deleteLater()
    except:
        pass

    ui = ColorPicker(app)
    ui.window.setWindowFlag(QtCore.Qt.Window)
    ui.window.show()          
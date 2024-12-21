import sys

import maya.cmds as cmds
from maya import OpenMayaUI as omui

from importlib import reload

from germ.utils import qtpyside
from germ.node_editor import scene
for module in [qtpyside, scene]:
    reload(module)
version, shiboken, wrapInstance, PySide, PySide.QtCore, PySide.QtWidgets, PySide.QtGui = qtpyside.get_version()

from PySide.QtCore import Qt
from PySide.QtWidgets import (
    QWidget,
    QMainWindow,
    )


class Interface(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        NAME = "GERM"
        self.check_existing_uis(UI_NAME=NAME)

        # parent to maya interface
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)

        self.setWindowTitle(NAME)
        self.setObjectName(NAME)

        self.init_ui()

    def init_ui(self):
        canvas = scene.GraphScene()
        editor = scene.GraphEditor(canvas)

        self.setCentralWidget(editor)

        self.setWindowTitle("GERM")
        self.resize(800, 800)

    def check_existing_uis(self, UI_NAME):
        if cmds.window(UI_NAME, exists=True):
            cmds.deleteUI(UI_NAME, window=True)

def show_interface():
    ui = Interface()
    ui.show()
    return ui


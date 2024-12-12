import sys

import maya.cmds as cmds
from maya import OpenMayaUI as omui

import importlib

pyside_versions = ["PySide6", "PySide2"]

for version in pyside_versions:
    print("Trying pyside version:", version)
    try:
        sys.modules["PySide"] = importlib.import_module(version)
        sys.modules["PySide.QtCore"] = importlib.import_module(f"{version}.QtCore")
        sys.modules["PySide.QtWidgets"] = importlib.import_module(f"{version}.QtWidgets")
        shiboken = importlib.import_module(f"shiboken{version[-1]}")
        wrapInstance = shiboken.wrapInstance

        print("Successful import of", version)
        break
    except ModuleNotFoundError:
        continue
else:
    raise ModuleNotFoundError("No PySide module found.")

from PySide.QtCore import Qt, QObject, SIGNAL, QPointF, QRectF
from PySide.QtWidgets import (
    QWidget,
    QGraphicsView,
    QGraphicsScene,
    QMainWindow,
    QGraphicsLineItem,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsProxyWidget,
    QShortcut
    )
from PySide.QtGui import (
        QBrush,
        QPen,
        QColor,
        QPainter,
        QKeySequence
        )

class Interface(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # parent to maya interface
        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(int(mayaMainWindowPtr), QWidget)
        self.setParent(mayaMainWindow)
        self.setWindowFlags(Qt.Window)

        self.setWindowTitle("GERM")

        self.init_ui()

    def init_ui(self):
        scene = GraphScene()
        editor = GraphEditor(scene)

        self.setCentralWidget(editor)

        self.setWindowTitle("GERM")
        self.resize(800, 800)


class GraphEditor(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)

        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setRenderHint(QPainter.TextAntialiasing)

        self.setScene(scene)


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        node1 = Node(0, 0, 150, 100, "Node 1")
        node2 = Node(200, 0, 150, 100, "Node 2")
        node3 = Node(100, 200, 150, 100, "Node 3")

        self.addItem(node1)
        self.addItem(node2)
        self.addItem(node3)

        # make edge connections
        edge = Edge(node1.outputs[0], node2.inputs[0])
        self.addItem(edge)

        # shortcut = QKeySequence(Qt.CTRL + Qt.Key_M)
        # self.add_node = QShortcut(shortcut, self, None, self.make_node)
        # self.add_node.activated.connect(self.make_node)

        self.update()

    def make_node(self):
        node = Node(0, 0, 150, 100, "Node")
        self.addItem(node)
        self.update()


class Node(QGraphicsRectItem):
    def __init__(self, x, y, width, height, name):
        super().__init__(0, 0, width, height)
        
        self.setPos(x, y)
        self.width = width
        self.height = height

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setBrush(QColor(161, 3, 252))
        self.setPen(QPen(QColor(0, 0, 0), 1))
        
        self.name_label = QGraphicsTextItem(name, self)
        self.name_label.setPos(10, 10)
        
        self.inputs = []
        self.outputs = []
        self.edges = []
        
        self.create_ports()

    def create_ports(self):
        input_port = Port(self, "input", 0, self.height / 2)
        output_port = Port(self, "output", self.width, self.height / 2)
        self.inputs.append(input_port)
        self.outputs.append(output_port)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        painter.setBrush(QColor(161, 3, 252))
        painter.drawRect(0, 0, self.width, self.height)
        self.name_label.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.name_label.setFlag(QGraphicsItem.ItemIsSelectable)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for edge in self.edges:
                edge.update_position()
        return super().itemChange(change, value)


class Port(QGraphicsEllipseItem):
    def __init__(self, parent, port_type, x, y):
        radius = 8
        super().__init__(x - radius, y - radius, radius * 2, radius * 2, parent)

        self.setBrush(QBrush(QColor(0, 255, 0) if port_type == "input" else QColor(255, 0, 0)))
        self.setPen(QPen(Qt.black))

        self.port_type = port_type
        self.connected_edge = None
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        # self.setFlag(QGraphicsItem.ItemIsMovable)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print(f"port {self.port_type} clicked")


class Edge(QGraphicsLineItem):
    def __init__(self, source_port, target_port):
        super().__init__()

        self.source_port = source_port
        self.target_port = target_port

        self.setPen(QPen(Qt.black, 2))
        self.update_position()

    def update_position(self):
        start_pos = self.source_port.scenePos() + QPointF(self.source_port.rect().center())
        end_pos = self.target_port.scenePos() + QPointF(self.target_port.rect().center())
        self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
    
    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        self.update_position()
        painter.drawLine(self.line())

def main():
    ui = Interface()
    ui.show()

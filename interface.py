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
        sys.modules["PySide.QtGui"] = importlib.import_module(f"{version}.QtGui")
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
    QGraphicsPathItem
    )
from PySide.QtGui import (
        QBrush,
        QPen,
        QColor,
        QPainter,
        QKeyEvent,
        QPainterPath
        )

if version == "PySide6":
    from PySide.QtWidgets import QMouseEvent
elif version == "PySide2":
    from PySide.QtGui import QMouseEvent

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
        
        if version == "PySide6":
            self.setRenderHint(int(QPainter.Antialiasing))
            self.setRenderHint(int(QPainter.SmoothPixmapTransform))
            self.setRenderHint(int(QPainter.TextAntialiasing))

        self.selected_port = None
        self.temp_edge = None

        self.setScene(scene)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_A and event.modifiers() == Qt.ShiftModifier:
            self.add_new_node()
        else:
            super().keyPressEvent(event)

    def add_new_node(self):
        x = 100
        y = 100
        width = 100
        height = 50
        name = "node"

        new_node = Node(x, y, width, height, name)
        self.scene().addItem(new_node)
    
    def find_port_at_position(self, scene_pos):
        for item in self.scene().items(scene_pos):
            if isinstance(item, Port):
                return item
        return None

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.find_port_at_position(scene_pos)
        print(f"clicked item: {item}, type: {type(item)}")

        if isinstance(item, QGraphicsLineItem) and item == self.temp_edge:
            print("clicked on temp edge, ignoring")
            return
        
        if isinstance(item, Port):
            print(f"clicked port: {item}")
            print(f"selected_port: {self.selected_port}")
            if self.selected_port is None:
                self.selected_port = item
                print(f"selected_port set to: {self.selected_port}")
                print("first port selected")
                self.temp_edge = QGraphicsLineItem()
                self.temp_edge.setPen(QPen(QColor(0, 0, 255), 2))
                self.scene().addItem(self.temp_edge)

            else:
                print("connecting final port")
                self.create_edge(self.selected_port, item)
                self.selected_port = None
                if self.temp_edge:
                    self.scene().removeItem(self.temp_edge)
                    self.temp_edge = None
        else:
            print("clicked on something else")
            if self.temp_edge:
                print("removing temporary edge")
                self.scene().removeItem(self.temp_edge)
                self.temp_edge = None
            self.selected_port = None

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.selected_port and self.temp_edge:
            # Update the temporary edge while moving the cursor
            mouse_pos = self.mapToScene(event.pos())
            p1_pos = self.selected_port.mapToScene(self.selected_port.rect().center())
            self.temp_edge.setLine(p1_pos.x(), p1_pos.y(), mouse_pos.x(), mouse_pos.y())
        super().mouseMoveEvent(event)

    def create_edge(self, port1, port2):
        print("create_edge run")
        edge = Edge(port1, port2)
        self.scene().addItem(edge)
        
        source_node = port1.parentItem()
        target_node = port2.parentItem()
        print(source_node)

        source_node.edges.append(edge)
        target_node.edges.append(edge)

class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.update()

    def make_node(self):
        print("make_node made")
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

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.itemChange(QGraphicsItem.ItemPositionChange, self.pos())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            # print("POSITION CHANGES")
            # print(self.edges)
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
        event.setAccepted(True)

    def contains(self, pos):
        return super().contains(pos)


class Edge(QGraphicsPathItem):
    def __init__(self, source_port, target_port):
        super().__init__()

        self.source_port = source_port
        self.target_port = target_port

        self.source_node = self.source_port.parentItem()
        self.target_node = self.target_port.parentItem()

        self.setPen(QPen(Qt.black, 2))
        self.update_position()

    def update_position(self):
        source_pos = self.source_port.mapToScene(self.source_port.rect().center())
        target_pos = self.target_port.mapToScene(self.target_port.rect().center())
        # self.setLine(source_pos.x(), source_pos.y(), target_pos.x(), target_pos.y())

        dx = abs(target_pos.x() - source_pos.x()) / 2
        control_point1 = QPointF(source_pos.x() + dx, source_pos.y())
        control_point2 = QPointF(target_pos.x() - dx, target_pos.y())

        path = QPainterPath()
        path.moveTo(source_pos)
        path.cubicTo(control_point1, control_point2, target_pos)

        self.setPath(path)

    def paint(self, painter, option, widget=None):
        painter.setPen(self.pen())
        self.update_position()
        # painter.drawLine(self.line())
        super().paint(painter, option, widget)

def main():
    ui = Interface()
    ui.show()

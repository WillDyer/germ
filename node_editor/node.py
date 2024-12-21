from germ.utils import qtpyside
version, shiboken, wrapInstance, PySide, PySide.QtCore, PySide.QtWidgets, PySide.QtGui = qtpyside.get_version()

from PySide.QtCore import Qt, QRectF
from PySide.QtWidgets import (
        QGraphicsItem,
        QGraphicsTextItem,
        QGraphicsRectItem
        )
from PySide.QtGui import (
        QPen,
        QColor
        )

from importlib import reload
from germ.node_editor import pin
reload(pin)

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
        input_port = pin.Port(self, "input", 0, self.height / 2)
        output_port = pin.Port(self, "output", self.width, self.height / 2)
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

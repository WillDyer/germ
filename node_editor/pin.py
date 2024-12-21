from germ.utils import qtpyside
version, shiboken, wrapInstance, PySide, PySide.QtCore, PySide.QtWidgets, PySide.QtGui = qtpyside.get_version()

from PySide.QtCore import Qt
from PySide.QtWidgets import(
        QGraphicsItem,
        QGraphicsEllipseItem
        )
from PySide.QtGui import (
        QBrush,
        QColor,
        QPen
        )


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


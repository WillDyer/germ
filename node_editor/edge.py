from germ.utils import qtpyside
version, shiboken, wrapInstance, PySide, PySide.QtCore, PySide.QtWidgets, PySide.QtGui = qtpyside.get_version()

from PySide.QtCore import Qt, QPointF
from PySide.QtWidgets import (
        QGraphicsPathItem
        )
from PySide.QtGui import (
        QPen,
        QPainterPath
        )


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


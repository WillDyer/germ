from germ.utils import qtpyside
version, shiboken, wrapInstance, PySide, PySide.QtCore, PySide.QtWidgets, PySide.QtGui = qtpyside.get_version()

from PySide.QtCore import Qt
from PySide.QtWidgets import (
        QGraphicsScene,
        QGraphicsView,
        QGraphicsLineItem
        )
from PySide.QtGui import (
        QPainter,
        QKeyEvent,
        QPen,
        QColor
        )

if version == "PySide6":
    from PySide.QtWidgets import QMouseEvent
elif version == "PySide2":
    from PySide.QtGui import QMouseEvent

from importlib import reload
from germ.node_editor import node, edge, pin
for module in [node, edge, pin]:
    reload(module)


class GraphScene(QGraphicsScene):
    def __init__(self):
        super().__init__()

        self.update()

    def make_node(self):
        print("make_node made")
        node_instance = node.Node(0, 0, 150, 100, "Node")
        self.addItem(node_instance)
        self.update()


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

        new_node = node.Node(x, y, width, height, name)
        self.scene().addItem(new_node)
    
    def find_port_at_position(self, scene_pos):
        for item in self.scene().items(scene_pos):
            if isinstance(item, pin.Port):
                return item
        return None

    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        item = self.find_port_at_position(scene_pos)
        print(f"clicked item: {item}, type: {type(item)}")

        if isinstance(item, QGraphicsLineItem) and item == self.temp_edge:
            print("clicked on temp edge, ignoring")
            return
        
        if isinstance(item, pin.Port):
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
        new_edge = edge.Edge(port1, port2)
        self.scene().addItem(new_edge)
        
        source_node = port1.parentItem()
        target_node = port2.parentItem()
        print(source_node)

        source_node.edges.append(new_edge)
        target_node.edges.append(new_edge)

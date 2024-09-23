from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QGuiApplication, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import QApplication, QDockWidget, QHBoxLayout, QMainWindow, QPushButton, QSizePolicy, QWidget


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.initUI()
        self._drawbox = []

    def initUI(self):
        self.setGeometry(100, 100, 400, 400)
        self.setWindowTitle("Drawing Example")
        self.pen = QPen(QColor(0, 0, 0))  # 创建一个黑色画笔
        self.startPos = None  # 方框的起始点
        self.endPos = None  # 方框的结束点
        self.show()

    def paintEvent(self, event):
        # painter = QPainter(self)
        # painter.setPen(self.pen)
        if self._drawbox:
            # rect = QRect(self.startPos, self.endPos)
            # painter.drawRect(rect)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)  # 开启抗锯齿
            pen_color = QColor(45, 65, 86)  # 边框线颜色 #2d4156
            painter.setPen(QPen(pen_color, 2))
            brush_color = QColor(125, 179, 238, 76)  # 内部颜色 #7db3ee 30%透明度
            painter.setBrush(brush_color)
            rect = QRect(*self._drawbox)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        # if event.button() == Qt.LeftButton:
        #     self.startPos = event.pos()
        #     self.endPos = event.pos()
        #     self.update()  # 触发绘图

        self.dragStartPosX = event.position().x()
        self.dragStartPosY = event.position().y()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # self.endPos = event.pos()
            self.DrawBox(event)
            self.update()  # 触发绘图

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # self.startPos = None
            # self.endPos = None
            self._drawbox = []
            self.update()  # 触发绘图

    def DrawBox(self, event: QMouseEvent):
        tolerance = 2
        pt = event.position()
        dx = pt.x() - self.dragStartPosX
        dy = pt.y() - self.dragStartPosY
        if abs(dx) <= tolerance and abs(dy) <= tolerance:
            return None
        self._drawbox = [self.dragStartPosX, self.dragStartPosY, dx, dy]


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("机器人通用平台")
        primary_screen = QGuiApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.9, primary_screen.height() * 0.9)
        self.canva = MyWidget(self)
        self.setCentralWidget(self.canva)
        self.centerOnScreen()
        """创建一个操作栏dock窗口"""
        dock_set_tool = QDockWidget("操作栏", self)
        dock_set_tool.setAllowedAreas(Qt.TopDockWidgetArea)  # 允许停靠在顶部
        dock_set_tool_size = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        dock_set_tool.setSizePolicy(dock_set_tool_size)
        # 将dock窗口添加到主窗口
        self.addDockWidget(Qt.TopDockWidgetArea, dock_set_tool)
        # 将水平布局添加到dock
        dock_set_tool_widget = QWidget()
        dock_set_tool.setWidget(dock_set_tool_widget)
        dock_set_tool_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout_set_tool = QHBoxLayout()
        dock_set_tool_widget.setLayout(hlayout_set_tool)
        """botton样式"""
        botton_size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        botton_size_policy.setHorizontalStretch(0)
        botton_size_policy.setVerticalStretch(0)
        botton_size_policy.setHeightForWidth(True)
        """添加 botton 到操作栏水平布局"""
        self.load_step_model = QPushButton("加载模型", self)
        self.load_step_model.setObjectName("loadFile")
        self.load_step_model.setSizePolicy(botton_size_policy)
        hlayout_set_tool.addWidget(self.load_step_model)

    # end alternate constructor
    def centerOnScreen(self):
        # 获取屏幕的尺寸
        primary_screen = QGuiApplication.primaryScreen().size()
        size = self.geometry()
        x = (primary_screen.width() - size.width()) // 2
        y = 0.7 * (primary_screen.height() - size.height()) // 2
        # 移动主窗口到中心位置
        self.move(x, y)

    # end def


if __name__ == "__main__":
    app = QApplication([])
    ex = MainWindow()
    ex.show()
    app.exec()

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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
        if self.startPos and self.endPos:
            # rect = QRect(self.startPos, self.endPos)
            # painter.drawRect(rect)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)  # 开启抗锯齿
            pen_color = QColor(45, 65, 86)  # 边框线颜色 #2d4156
            painter.setPen(QPen(pen_color, 2))
            brush_color = QColor(125, 179, 238, 76)  # 内部颜色 #7db3ee 30%透明度
            painter.setBrush(brush_color)
            rect = QRect(self.startPos, self.endPos)
            painter.drawRect(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPos = event.pos()
            self.endPos = event.pos()
            self.update()  # 触发绘图

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.endPos = event.pos()
            self.update()  # 触发绘图

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.startPos = None
            self.endPos = None
            self.update()  # 触发绘图


if __name__ == "__main__":
    app = QApplication([])
    ex = MyWidget()
    app.exec()

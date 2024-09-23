# PySide6
from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QEvent, QRect, QSize, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractButton,
    QApplication,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QStyle,
    QStyleOptionHeader,
    QStylePainter,
    QTableView,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class TableView(QtWidgets.QTableView):
    """QTableView specialization that can e.g. paint the top left corner header."""

    def __init__(self, nw_heading, parent=None):
        super(TableView, self).__init__(parent)

        # 存储左上角按钮的文本
        self.__nw_heading = nw_heading

        # 查找子对象中的 QAbstractButton，通常代表左上角的按钮
        btn = self.findChild(QtWidgets.QAbstractButton)

        # 设置按钮的文本和工具提示
        btn.setText(self.__nw_heading)
        btn.setToolTip("Toggle selecting all table cells")

        # 安装事件过滤器，用于处理按钮的绘制事件
        btn.installEventFilter(self)

        # 获取按钮的样式选项
        opt = QtWidgets.QStyleOptionHeader()
        opt.text = btn.text()

        # 计算按钮的最小宽度并将其设置为垂直表头的最小宽度
        # s = QtCore.QSize(
        #     btn.style()
        #     .sizeFromContents(QtWidgets.QStyle.CT_HeaderSection, opt, QtCore.QSize(), btn)
        #     .expandedTo(QtWidgets.QApplication)
        # )
        # 使用 sizeHint 获取按钮的大小
        size_hint = btn.sizeHint()
        vertical_header_min_width = size_hint.width()

        # 设置垂直表头的最小宽度
        if size_hint.isValid():
            self.verticalHeader().setMinimumWidth(size_hint.width())
        self.verticalHeader().setMinimumWidth(50)

    def eventFilter(self, obj, event):
        """事件过滤器用于处理按钮的绘制事件"""

        if event.type() != QtCore.QEvent.Paint or not isinstance(obj, QtWidgets.QAbstractButton):
            return False

        # 手动绘制按钮 (参考自 QTableCornerButton)
        opt = QtWidgets.QStyleOptionHeader()
        opt.initFrom(obj)
        styleState = QtWidgets.QStyle.State_None
        if obj.isEnabled():
            styleState |= QtWidgets.QStyle.State_Enabled
        if obj.isActiveWindow():
            styleState |= QtWidgets.QStyle.State_Active
        if obj.isDown():
            styleState |= QtWidgets.QStyle.State_Sunken
        opt.state = styleState
        opt.rect = obj.rect()
        # 这一行是与 QTableCornerButton 的唯一不同之处
        opt.text = obj.text()
        opt.position = QtWidgets.QStyleOptionHeader.OnlyOneSection
        painter = QtWidgets.QStylePainter(obj)
        painter.drawControl(QtWidgets.QStyle.CE_Header, opt)

        return True


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Table 测试")
        self.setGeometry(100, 100, 600, 400)

        # 创建表格
        self.create_table()

    def create_table(self):
        # 创建表格模型
        model = QStandardItemModel(self)

        # 设置表头
        model.setHorizontalHeaderLabels(["I", "II", "III"])

        # 填充表格数据
        for row in range(3):
            for col in range(3):
                item = QStandardItem(str(row * 3 + col + 1))
                model.setItem(row, col, item)

        # 创建表格视图
        table_view = TableView("abc", self)
        table_view.setModel(model)

        # 隐藏行表头
        # table_view.verticalHeader().setVisible(False)

        # 设置表格内容居中显示
        table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_view.setVerticalScrollMode(QTableView.ScrollPerPixel)
        table_view.setHorizontalScrollMode(QTableView.ScrollPerPixel)
        table_view.setShowGrid(False)
        table_view.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        table_view.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        # 禁用编辑
        table_view.setEditTriggers(QTableWidget.NoEditTriggers)

        # 调整列宽和行高
        table_view.resizeColumnsToContents()
        table_view.resizeRowsToContents()

        # 设置水平表头
        header = table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # 设置垂直表头
        v_header = table_view.verticalHeader()
        v_header.setSectionResizeMode(QHeaderView.Stretch)

        # 设置表格视图为主窗口的中央部件
        self.setCentralWidget(table_view)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()

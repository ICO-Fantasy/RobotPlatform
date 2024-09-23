import time

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QVBoxLayout, QWidget


class WorkerThread(QThread):
    signal_done = Signal()

    def run(self):
        time.sleep(2)  # 模拟耗时操作
        self.signal_done.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("多线程测试")
        primary_screen = QApplication.primaryScreen().size()
        self.setGeometry(0, 0, primary_screen.width() * 0.8, primary_screen.height() * 0.8)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.setup_ui()
        self.centerOnScreen()

    def setup_ui(self):
        layout = QGridLayout()

        font = QFont()
        font.setPointSize(200)
        self.label = QLabel("0", self)
        self.label.setFont(font)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.label, 0, 0, 1, 2, alignment=Qt.AlignCenter)

        self.button = QPushButton("+1", self)
        self.button.clicked.connect(self.increment_value)
        layout.addWidget(self.button, 1, 0, 1, 2, alignment=Qt.AlignCenter)

        self.timer_label = QLabel("Time: 0", self)
        layout.addWidget(self.timer_label, 2, 0, 1, 2, alignment=Qt.AlignCenter)

        self.central_widget.setLayout(layout)

        # 创建计时器
        self.timer = QTimer()
        self.current_time = 0
        self.timer.timeout.connect(self.update_value)

    def increment_value(self):
        # 启动计时器（在主线程中）
        self.timer.start(10)
        # 启动子线程执行耗时操作
        worker_thread = WorkerThread()
        worker_thread.signal_done.connect(self.thread_done)
        worker_thread.run()

    def thread_done(self):
        self.timer.stop()
        current_value = int(self.label.text())
        new_value = current_value + 1
        self.label.setText(str(new_value))

    def update_value(self):
        # 启动计时器
        self.current_time += 10
        self.timer_label.setText(f"Time: {self.current_time} ms")

    def centerOnScreen(self):
        # 获取屏幕的尺寸
        primary_screen = QGuiApplication.primaryScreen().size()
        size = self.geometry()
        x = (primary_screen.width() - size.width()) // 2
        y = 0.7 * (primary_screen.height() - size.height()) // 2
        # 移动主窗口到中心位置
        self.move(x, y)


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()

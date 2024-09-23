from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication, QMainWindow, QProgressBar, QPushButton, QVBoxLayout, QWidget


class WorkerThread(QThread):
    # 通过信号与槽机制，实现线程中任务的通信
    progress_signal = Signal(int)
    progress_done_signal = Signal()

    def run(self):
        for i in range(1, 101):
            self.progress_signal.emit(i)  # 发送进度信号
            self.msleep(10)  # 模拟耗时任务
        self.progress_done_signal.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("子线程示例")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.start_button = QPushButton("开始任务", self)
        self.start_button.clicked.connect(self.start_task)
        layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(10, 10, 300, 25)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        self.central_widget.setLayout(layout)

        # 创建子线程
        self.worker_thread = WorkerThread()
        self.worker_thread.progress_signal.connect(self.update_progress)  # 连接进度信号
        self.worker_thread.progress_done_signal.connect(self.hide_progress_bar)  # 连接进度信号

    def start_task(self):
        # 启动子线程
        if not self.worker_thread.isRunning():
            # 显示进度条
            self.progress_bar.show()
            self.worker_thread.start()

    def update_progress(self, value):
        # 更新进度条的值
        self.progress_bar.setValue(value)

    def hide_progress_bar(self):
        self.progress_bar.hide()


if __name__ == "__main__":
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    app.exec()

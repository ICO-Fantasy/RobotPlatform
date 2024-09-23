import os
import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    # qmlRegisterType("OpenCascade", 7, 3, "OcctView")
    # 需要引入一个 quickItem
    engine.load(r"qml/mainQuick.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
# end main

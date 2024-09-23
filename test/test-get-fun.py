import inspect

from PySide6.QtWidgets import QApplication

from myViewer3d import myViewer3d
from qtViewer3d import qtViewer3dWidget

app = QApplication([])
for name, member in inspect.getmembers(qtViewer3dWidget(), predicate=inspect.ismethod):
    print(name, "\nmember: ", member)

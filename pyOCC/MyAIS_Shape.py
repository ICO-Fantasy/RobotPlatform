from OCC.Core.AIS import AIS_Shape
from OCC.Core.StdSelect import TopoDS_Shape
from OCC.Core.TopoDS import TopoDS_Shape


class MyAIS_Shape(AIS_Shape):
    def __init__(self, shap: TopoDS_Shape) -> None:
        if isinstance(shap, AIS_Shape):
            super().__init__(shap)
        elif isinstance(shap, list):
            super().__init__(shap[0])
            self.shapes = [AIS_Shape(item) for item in shap]

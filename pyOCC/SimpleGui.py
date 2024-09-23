import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from OCC.Core.AIS import AIS_Trihedron, AIS_ViewCube
from OCC.Core.Aspect import Aspect_TOTP_RIGHT_LOWER
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCC.Core.Geom import Geom_Axis2Placement
from OCC.Core.Prs3d import Prs3d_DatumAspect
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_BLACK, Quantity_NOC_WHITE
from OCC.Core.V3d import V3d_ZBUFFER
from OCC.Display.OCCViewer import Viewer3d
from OCC.Display.SimpleGui import init_display

from . import LocalCONFIG, createTrihedron, getColor

# 使用配置值
X_AXIS_DIRECTION = LocalCONFIG.X_AXIS_DIRECTION
Y_AXIS_DIRECTION = LocalCONFIG.Y_AXIS_DIRECTION
Z_AXIS_DIRECTION = LocalCONFIG.Z_AXIS_DIRECTION
X_AXIS_COLOR = LocalCONFIG.X_AXIS_COLOR
Y_AXIS_COLOR = LocalCONFIG.Y_AXIS_COLOR
Z_AXIS_COLOR = LocalCONFIG.Z_AXIS_COLOR


def displayViewTrihedron(display: Viewer3d):
    """显示视图坐标轴"""
    display.View.TriedronDisplay(
        Aspect_TOTP_RIGHT_LOWER,  # 显示位置
        Quantity_Color(Quantity_NOC_BLACK),  # 字体颜色
        0.1,  # 图像大小
        V3d_ZBUFFER,  # 显示模式
    )  # 显示视图坐标轴


def displayViewCube(display: Viewer3d):
    """显示视图立方体"""
    a_view_cube = AIS_ViewCube()  # 视图立方体
    # 修改坐标轴文字颜色
    aDrawer = a_view_cube.Attributes()
    aDrawer.SetDatumAspect(Prs3d_DatumAspect())  # 动态设置
    aDatumAsp = aDrawer.DatumAspect()  # 获取 Prs3d_DatumAspect 对象指针
    aDatumAsp.TextAspect(X_AXIS_DIRECTION).SetColor(X_AXIS_COLOR)
    aDatumAsp.TextAspect(Y_AXIS_DIRECTION).SetColor(Y_AXIS_COLOR)
    aDatumAsp.TextAspect(Z_AXIS_DIRECTION).SetColor(Z_AXIS_COLOR)
    # 显示视图立方体
    display.Context.Display(a_view_cube, True)


def displayOriginTrihedron(display: Viewer3d):
    """显示原点坐标轴"""
    a_origin_trihedron = createTrihedron()
    display.Context.Display(a_origin_trihedron, True)


def initDisplay(
    size=(1920, 980),
    display_view_triedron=False,
    display_view_cube=True,
    display_origin_trihedron=True,
):
    """display, start_display, add_menu, add_function_to_menu"""
    display, start_display, add_menu, add_function_to_menu = init_display(size=size, display_triedron=False)
    if display_view_triedron:
        displayViewTrihedron(display)
    if display_view_cube:
        displayViewCube(display)
    if display_origin_trihedron:
        displayOriginTrihedron(display)

    return display, start_display, add_menu, add_function_to_menu


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = initDisplay(
        display_view_triedron=True,
        display_view_cube=True,
        display_origin_trihedron=True,
    )
    start_display()

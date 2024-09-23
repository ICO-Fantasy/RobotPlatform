import math
import os
import random
import sys
import time
from enum import Enum
from itertools import cycle
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 全局日志设置
from loguru import logger

if sys.stderr:
    logger.remove()
    # logger.add(sys.stderr, level="WARNING")
    logger.add(sys.stderr, level="DEBUG")
# end if

from OCC.Core.AIS import (
    AIS_DisplayMode,
    AIS_InteractiveContext,
    AIS_InteractiveObject,
    AIS_ListOfInteractive,
    AIS_Manipulator,
    AIS_ManipulatorMode,
    AIS_NArray1OfEntityOwner,
    AIS_RubberBand,
    AIS_Shape,
    AIS_TextLabel,
    AIS_TexturedShape,
    AIS_ViewCube,
)
from OCC.Core.Aspect import (
    Aspect_GradientFillMethod,
    Aspect_TOL_DOT,
    Aspect_TOL_SOLID,
    Aspect_TOTP_RIGHT_LOWER,
    Aspect_TypeOfTriedronPosition,
)
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRep import BRep_Builder, BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepAlgoAPI import (
    BRepAlgoAPI_Cut,
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Section,
    BRepAlgoAPI_Splitter,
)
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeShell,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Sewing,
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepFeat import BRepFeat_SplitShape
from OCC.Core.BRepFilletAPI import (
    BRepFilletAPI_MakeChamfer,
    BRepFilletAPI_MakeFillet,
    BRepFilletAPI_MakeFillet2d,
)
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

# pyOCC
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeSphere,
)
from OCC.Core.BRepTools import BRepTools_WireExplorer, breptools
from OCC.Core.GC import GC_MakeSegment
from OCC.Core.gp import (
    gp_Ax1,
    gp_Ax2,
    gp_Circ,
    gp_Dir,
    gp_Dir2d,
    gp_EulerSequence,
    gp_Pln,
    gp_Pnt,
    gp_Pnt2d,
    gp_Quaternion,
    gp_Trsf,
    gp_Trsf2d,
    gp_Vec,
    gp_Vec2d,
)
from OCC.Core.Graphic3d import (
    Graphic3d_Camera,
    Graphic3d_GraduatedTrihedron,
    Graphic3d_MaterialAspect,
    Graphic3d_NameOfMaterial,
    Graphic3d_NOM_ALUMINIUM,
    Graphic3d_NOM_BRASS,
    Graphic3d_NOM_STEEL,
    Graphic3d_PBRMaterial,
    Graphic3d_RenderingParams,
    Graphic3d_RM_RASTERIZATION,
    Graphic3d_StereoMode_QuadBuffer,
    Graphic3d_StructureManager,
    Graphic3d_TransformPers,
    Graphic3d_TransModeFlags,
    Graphic3d_Vec2i,
)
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.Interface import Interface_Static, Interface_Static_SetCVal
from OCC.Core.IntTools import IntTools_FaceFace
from OCC.Core.Message import Message_ProgressRange
from OCC.Core.NCollection import NCollection_List, NCollection_TListIterator
from OCC.Core.Prs3d import Prs3d_DatumAspect
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.RWMesh import RWMesh_CoordinateSystem_Zup
from OCC.Core.RWObj import RWObj_CafReader
from OCC.Core.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCC.Core.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCC.Core.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCC.Core.TopAbs import (
    TopAbs_COMPOUND,
    TopAbs_COMPSOLID,
    TopAbs_EDGE,
    TopAbs_FACE,
    TopAbs_SHAPE,
    TopAbs_ShapeEnum,
    TopAbs_SHELL,
    TopAbs_SOLID,
    TopAbs_VERTEX,
    TopAbs_WIRE,
    topabs,
)
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import (
    TopoDS_Compound,
    TopoDS_Edge,
    TopoDS_Shape,
    TopoDS_Shell,
    TopoDS_Wire,
    topods,
)
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.V3d import (
    V3d_AmbientLight,
    V3d_DirectionalLight,
    V3d_PositionalLight,
    V3d_SpotLight,
    V3d_TypeOfOrientation,
    V3d_View,
    V3d_Viewer,
    V3d_Xneg,
    V3d_Xpos,
    V3d_XposYnegZpos,
    V3d_Yneg,
    V3d_Ypos,
    V3d_ZBUFFER,
    V3d_Zneg,
    V3d_Zpos,
)
from OCC.Core.XCAFApp import XCAFApp_Application
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool
from OCC.Display.OCCViewer import Viewer3d
from OCC.Display.SimpleGui import init_display

# PySide6
from PySide6.QtCore import QRect, Qt, Signal, Slot
from PySide6.QtGui import QGuiApplication, QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

# local
from AIS_Shape_Tri import AIS_Shape_Tri
from mainGUI import MainWindow
from printTools import (
    get_gp_matrix,
    get_Trsf_value,
    print_gp_Pnt,
    print_gp_Vec,
    print_Trsf,
    print_Trsf_XYZWPR,
    print_Var_Name,
)
from pyOCC import COLOR, color_list, createTrihedron, read_step, readStepWithColor
from qtViewer3d import qtViewer3dWidget
from qtViewer3d_manipulator import qtViewer3dWidgetManipulator

# from qtViewer3dWithoutLight import qtViewer3dWidget

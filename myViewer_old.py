import itertools
import math
import os
import sys
import time

import OCC
from OCC.Core.AIS import (
    AIS_InteractiveContext,
    AIS_Shaded,
    AIS_Shape,
    AIS_Shape_SelectionMode,
    AIS_TextLabel,
    AIS_TexturedShape,
    AIS_WireFrame,
)
from OCC.Core.Aspect import Aspect_FM_NONE, Aspect_FM_STRETCH, Aspect_GFM_VER, Aspect_TOTP_RIGHT_LOWER
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeEdge2d,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
)
from OCC.Core.Geom import Geom_Curve, Geom_Surface
from OCC.Core.Geom2d import Geom2d_Curve
from OCC.Core.gp import gp_Dir, gp_Pnt, gp_Pnt2d, gp_Trsf, gp_Vec
from OCC.Core.Graphic3d import (
    Graphic3d_Camera,
    Graphic3d_GraduatedTrihedron,
    Graphic3d_MaterialAspect,
    Graphic3d_NameOfMaterial,
    Graphic3d_NOM_NEON_GNC,
    Graphic3d_NOT_ENV_CLOUDS,
    Graphic3d_RenderingParams,
    Graphic3d_RM_RASTERIZATION,
    Graphic3d_RM_RAYTRACING,
    Graphic3d_StereoMode_QuadBuffer,
    Graphic3d_Structure,
    Graphic3d_TextureEnv,
    Graphic3d_TOSM_FRAGMENT,
    Handle_Graphic3d_TextureEnv_Create,
)
from OCC.Core.Prs3d import Prs3d_Arrow, Prs3d_Text, Prs3d_TextAspect
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NOC_BLACK,
    Quantity_NOC_BLUE1,
    Quantity_NOC_CYAN1,
    Quantity_NOC_GREEN,
    Quantity_NOC_ORANGE,
    Quantity_NOC_RED,
    Quantity_NOC_WHITE,
    Quantity_NOC_YELLOW,
    Quantity_TOC_RGB,
)
from OCC.Core.TCollection import TCollection_AsciiString, TCollection_ExtendedString
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID, TopAbs_VERTEX
from OCC.Core.V3d import (
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
from OCC.Core.Visualization import Display3d

from pyOCC import getColor

# Shaders and Units definition must be found by occ
# the fastest way to get done is to set the CASROOT env variable
# it must point to the /share folder.
"""确保 OCCT 能够找到并使用所需的着色器和单位定义，从而确保图形渲染和单位转换等功能能够正常运作"""
if sys.platform == "win32":
    # do the same for Units
    if "CASROOT" in os.environ:
        casroot_path = os.environ["CASROOT"]
        # raise an error, force the user to correctly set the variable
        err_msg = "Please set the CASROOT env variable (%s is not ok)" % casroot_path
        if not os.path.isdir(casroot_path):
            raise AssertionError(err_msg)
    else:  # on miniconda or anaconda or whatever conda
        occ_package_path = os.path.dirname(OCC.__file__)
        casroot_path = os.path.join(occ_package_path, "..", "..", "..", "Library", "share", "oce")
        # we check that all required files are at the right place
        shaders_dict_found = os.path.isdir(os.path.join(casroot_path, "src", "Shaders"))
        unitlexicon_found = os.path.isfile(os.path.join(casroot_path, "src", "UnitsAPI", "Lexi_Expr.dat"))
        unitsdefinition_found = os.path.isfile(os.path.join(casroot_path, "src", "UnitsAPI", "Units.dat"))
        if shaders_dict_found and unitlexicon_found and unitsdefinition_found:
            os.environ["CASROOT"] = casroot_path


# def get_color_from_name(color_name):
#     """from the string 'WHITE', returns Quantity_Color
#     WHITE.
#     color_name is the color name, case insensitive.
#     """
#     enum_name = "Quantity_NOC_%s" % color_name.upper()
#     if enum_name in globals():
#         color_num = globals()[enum_name]
#     elif enum_name + "1" in globals():
#         color_num = globals()[enum_name + "1"]
#         print("Many colors for color name %s, using first." % color_name)
#     else:
#         color_num = Quantity_NOC_WHITE
#         print("Color name not defined. Use White by default")
#     return Quantity_Color(color_num)


def to_string(_string):
    return TCollection_ExtendedString(_string)


class myViewer3d(Display3d):
    def __init__(self):
        Display3d.__init__(self)
        self._parent = None  # the parent openGL GUI container

        self._inited = False
        self._local_context_opened = False

        self.Context: AIS_InteractiveContext = self.GetContext()
        self.Viewer: V3d_Viewer = self.GetViewer()
        self.View: V3d_View = self.GetView()

        self.default_drawer = None
        self._structure_manager = None
        self._is_offscreen = None

        self.selected_aiss = []
        self._select_callbacks = []
        self._overlay_items = []

        self._window_handle = None
        self.camera = None

    def get_parent(self):
        return self._parent

    def register_overlay_item(self, overlay_item):
        self._overlay_items.append(overlay_item)
        self.View.MustBeResized()
        self.View.Redraw()

    def register_select_callback(self, callback):
        """注册一个当 AIS 对象被选择时调用的回调函数"""
        if not callable(callback):
            raise AssertionError("必须输入一个可执行的函数")
        # elif not self.check_func_para(callback):
        #     raise AssertionError("输入的函数入参应该满足 (ais: AIS_Shape, X: float, Y: float)")
        self._select_callbacks.append(callback)

    # 编写一个函数，检查可调用对象是否符合输入格式
    from typing import Callable, Type

    @staticmethod
    def check_func_para(a_func: Callable) -> bool:
        import inspect

        # 获取函数的签名信息
        signature = inspect.signature(a_func)

        # 定义期望的参数类型
        expected_params = [
            inspect.Parameter("ais", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation="OCC.Core.AIS.AIS_Shape"),
            inspect.Parameter("X", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=float),
            inspect.Parameter("Y", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=float),
        ]
        # a_a = list(signature.parameters.values())
        # 检查函数的参数是否符合期望
        return list(signature.parameters.values()) == expected_params

    def unregister_callback(self, callback):
        """从回调函数列表中删除输入的回调函数"""
        if not callback in self._select_callbacks:
            raise AssertionError("该函数未被注册")
        self._select_callbacks.remove(callback)

    def MoveTo(self, X, Y):
        self.Context.MoveTo(X, Y, self.View, True)

    def FitAll(self):
        self.View.ZFitAll()
        self.View.FitAll()

    def Create(
        self,
        window_handle=None,
        parent=None,
        create_default_lights=True,
        draw_face_boundaries=True,
        phong_shading=True,
        display_glinfo=False,
    ):
        self._window_handle = window_handle
        self._parent = parent

        if self._window_handle is None:
            self.InitOffscreen(640, 480)
            self._is_offscreen = True
        else:
            self.Init(self._window_handle)
            self._is_offscreen = False

        # display OpenGl Information
        if display_glinfo:
            self.GlInfo()

        if create_default_lights:
            self.Viewer.SetDefaultLights()
            self.Viewer.SetLightOn()

        self.camera = self.View.Camera()
        self.default_drawer = self.Context.DefaultDrawer()

        # draw black contour edges, like other famous CAD packages
        if draw_face_boundaries:
            self.default_drawer.SetFaceBoundaryDraw(True)

        # turn up tessellation defaults, which are too conversative...
        chord_dev = self.default_drawer.MaximalChordialDeviation() / 10.0
        self.default_drawer.SetMaximalChordialDeviation(chord_dev)

        if phong_shading:
            # gouraud shading by default, prefer phong instead
            self.View.SetShadingModel(Graphic3d_TOSM_FRAGMENT)

        # necessary for text rendering
        self._structure_manager = self.Context.MainPrsMgr().StructureManager()

        # turn self._inited flag to True
        self._inited = True

    def OnResize(self):
        self.View.MustBeResized()

    def ResetView(self):
        self.View.Reset()

    def Repaint(self):
        self.Viewer.Redraw()

    def SetModeWireFrame(self):
        self.View.SetComputedMode(False)
        self.Context.SetDisplayMode(AIS_WireFrame, True)

    def SetModeShaded(self):
        self.View.SetComputedMode(False)
        self.Context.SetDisplayMode(AIS_Shaded, True)

    def SetModeHLR(self):
        self.View.SetComputedMode(True)

    def SetOrthographicProjection(self):
        self.camera.SetProjectionType(Graphic3d_Camera.Projection_Orthographic)

    def SetPerspectiveProjection(self):
        self.camera.SetProjectionType(Graphic3d_Camera.Projection_Perspective)

    def View_Top(self):
        self.View.SetProj(V3d_Zpos)

    def View_Bottom(self):
        self.View.SetProj(V3d_Zneg)

    def View_Left(self):
        self.View.SetProj(V3d_Xneg)

    def View_Right(self):
        self.View.SetProj(V3d_Xpos)

    def View_Front(self):
        self.View.SetProj(V3d_Yneg)

    def View_Rear(self):
        self.View.SetProj(V3d_Ypos)

    def View_Iso(self):
        self.View.SetProj(V3d_XposYnegZpos)

    def EnableTextureEnv(self, name_of_texture=Graphic3d_NOT_ENV_CLOUDS):
        """enable environment mapping. Possible modes are
        Graphic3d_NOT_ENV_CLOUDS
        Graphic3d_NOT_ENV_CV
        Graphic3d_NOT_ENV_MEDIT
        Graphic3d_NOT_ENV_PEARL
        Graphic3d_NOT_ENV_SKY1
        Graphic3d_NOT_ENV_SKY2
        Graphic3d_NOT_ENV_LINES
        Graphic3d_NOT_ENV_ROAD
        Graphic3d_NOT_ENV_UNKNOWN
        """
        texture_env = Graphic3d_TextureEnv(name_of_texture)
        self.View.SetTextureEnv(texture_env)
        self.View.Redraw()

    def DisableTextureEnv(self):
        a_null_texture = Handle_Graphic3d_TextureEnv_Create()
        self.View.SetTextureEnv(a_null_texture)  # Passing null handle to clear the texture data
        self.View.Redraw()

    def SetRenderingParams(
        self,
        Method=Graphic3d_RM_RASTERIZATION,
        RaytracingDepth=3,
        IsShadowEnabled=True,
        IsReflectionEnabled=False,
        IsAntialiasingEnabled=False,
        IsTransparentShadowEnabled=False,
        StereoMode=Graphic3d_StereoMode_QuadBuffer,
        AnaglyphFilter=Graphic3d_RenderingParams.Anaglyph_RedCyan_Optimized,
        ToReverseStereo=False,
    ):
        """Default values are :
        Method=Graphic3d_RM_RASTERIZATION,
        RaytracingDepth=3,
        IsShadowEnabled=True,
        IsReflectionEnabled=False,
        IsAntialiasingEnabled=False,
        IsTransparentShadowEnabled=False,
        StereoMode=Graphic3d_StereoMode_QuadBuffer,
        AnaglyphFilter=Graphic3d_RenderingParams.Anaglyph_RedCyan_Optimized,
        ToReverseStereo=False)
        """
        self.ChangeRenderingParams(
            Method,
            RaytracingDepth,
            IsShadowEnabled,
            IsReflectionEnabled,
            IsAntialiasingEnabled,
            IsTransparentShadowEnabled,
            StereoMode,
            AnaglyphFilter,
            ToReverseStereo,
        )

    def SetRasterizationMode(self):
        """to enable rasterization mode, just call the SetRenderingParams
        with default values
        """
        self.SetRenderingParams()

    def SetRaytracingMode(self, depth=3):
        """enables the raytracing mode"""
        self.SetRenderingParams(
            Method=Graphic3d_RM_RAYTRACING,
            RaytracingDepth=depth,
            IsAntialiasingEnabled=True,
            IsShadowEnabled=True,
            IsReflectionEnabled=True,
            IsTransparentShadowEnabled=True,
        )

    def ExportToImage(self, image_filename):
        self.View.Dump(image_filename)

    def display_graduated_trihedron(self):
        a_trihedron_data = Graphic3d_GraduatedTrihedron()
        self.View.GraduatedTrihedronDisplay(a_trihedron_data)

    def display_triedron(self):
        """Show a black triedron in lower right corner"""
        self.View.TriedronDisplay(
            Aspect_TOTP_RIGHT_LOWER,
            Quantity_Color(Quantity_NOC_BLACK),
            0.1,
            V3d_ZBUFFER,
        )

    def hide_triedron(self):
        """Show a black triedron in lower right corner"""
        self.View.TriedronErase()

    def set_bg_gradient_color(self, color1, color2, fill_method=Aspect_GFM_VER):
        """set a bg vertical gradient color.
        color1 is [R1, G1, B1], each being bytes or an instance of Quantity_Color
        color2 is [R2, G2, B2], each being bytes or an instance of Quantity_Color
        fill_method is one of Aspect_GFM_VER value Aspect_GFM_NONE, Aspect_GFM_HOR,
        Aspect_GFM_VER, Aspect_GFM_DIAG1, Aspect_GFM_DIAG2, Aspect_GFM_CORNER1, Aspect_GFM_CORNER2,
        Aspect_GFM_CORNER3, Aspect_GFM_CORNER4
        """
        if isinstance(color1, list) and isinstance(color2, list):
            R1, G1, B1 = color1
            R2, G2, B2 = color2
            color1 = getColor(float(R1) / 255.0, float(G1) / 255.0, float(B1) / 255.0)
            color2 = getColor(float(R2) / 255.0, float(G2) / 255.0, float(B2) / 255.0)
        elif not isinstance(color1, Quantity_Color) and isinstance(color2, Quantity_Color):
            raise AssertionError("color1 and color2 mmust be either [R, G, B] lists or a Quantity_Color")
        self.View.SetBgGradientColors(color1, color2, fill_method, True)

    def SetBackgroundImage(self, image_filename, stretch=True):
        """displays a background image (jpg, png etc.)"""
        if not os.path.isfile(image_filename):
            raise IOError("image file %s not found." % image_filename)
        if stretch:
            self.View.SetBackgroundImage(image_filename, Aspect_FM_STRETCH, True)
        else:
            self.View.SetBackgroundImage(image_filename, Aspect_FM_NONE, True)

    def DisplayVector(self, vec, pnt, update=False):
        """displays a vector as an arrow"""
        if self._inited:
            aStructure = Graphic3d_Structure(self._structure_manager)

            pnt_as_vec = gp_Vec(pnt.X(), pnt.Y(), pnt.Z())
            start = pnt_as_vec + vec
            pnt_start = gp_Pnt(start.X(), start.Y(), start.Z())

            Prs3d_Arrow.Draw(
                aStructure.CurrentGroup(),
                pnt_start,
                gp_Dir(vec),
                math.radians(20),
                vec.Magnitude(),
            )
            aStructure.Display()
            # it would be more coherent if a AIS_InteractiveObject
            # would be returned
            if update:
                self.Repaint()
            return aStructure

    # def DisplayMessage(
    #     self,
    #     point: gp_Pnt,
    #     text: str,
    #     font_style="SimSun",
    #     font_height=14.0,
    #     text_color=(0.0, 0.0, 0.0),
    #     update=False,
    # ):
    #     """在 point 位置显示文字

    #     Parameters
    #     ----------
    #     point : gp_Pnt
    #         要显示的位置
    #     text : str
    #         要显示的文字
    #     font_style : str, optional
    #         字体，by default "SimSun"
    #     font_height : float, optional
    #         文字高度，by default 14.0
    #     text_color : tuple, optional
    #         文字颜色，by default (0.0, 0.0, 0.0)
    #     update : bool, optional
    #         是否更新，by default False
    #     """
    #     aStructure = Graphic3d_Structure(self._structure_manager)

    #     text_aspect = Prs3d_TextAspect()
    #     text_aspect.SetColor(getColor(*text_color))
    #     text_aspect.SetFont(font_style)
    #     text_aspect.SetHeight(font_height)
    #     if isinstance(point, gp_Pnt2d):
    #         point = gp_Pnt(point.X(), point.Y(), 0)

    #     Prs3d_Text.Draw(aStructure.CurrentGroup(), text_aspect, to_string(text), point)
    #     aStructure.Display()
    #     # @TODO: it would be more coherent if a AIS_InteractiveObject
    #     # is be returned
    #     if update:
    #         self.Repaint()
    #     return aStructure

    def DisplayMessage(
        self,
        text: str,
        pnt: gp_Pnt = gp_Pnt(0, 0, 0),
        font_style="SimSun",
        font_height=14.0,
        text_color=(0.0, 0.0, 0.0),
        update=False,
    ):
        """在指定位置显示文字 (基准为文字左下角，文字始终平行于屏幕)

        Parameters
        ----------
        text : str
            需要显示的文字
        pnt : gp_Pnt, optional
            文字的位置，by default gp_Pnt(0, 0, 0)
        font_style : str, optional
            字体，by default "SimSun"
        font_height : float, optional
            文字高度，by default 14.0
        text_color : tuple, optional
            字体颜色，by default (0.0, 0.0, 0.0)
        update : bool, optional
            是否立即更新，by default False

        Returns
        -------
        AIS_TextLabel
            AIS 文字对象
        """
        # 创建一个 AIS_TextLabel 对象
        text_label = AIS_TextLabel()
        t_text = TCollection_ExtendedString(text, True)  # 文字容器
        text_label.SetText(t_text)
        text_label.SetFont(font_style)
        text_label.SetHeight(font_height)
        text_label.SetColor(getColor(*text_color))
        text_translate = gp_Trsf()
        text_translate.SetTranslation(gp_Vec(gp_Pnt(), pnt))
        text_label.SetLocalTransformation(text_translate)
        self.Context.Display(text_label, update)
        return text_label

    # def DisplayShape(
    #     self,
    #     shapes,
    #     material=None,
    #     texture=None,
    #     color=None,
    #     transparency=None,
    #     update=False,
    # ):
    #     """display one or a set of displayable objects"""
    #     ais_shapes = []  # the list of all displayed shapes

    #     if issubclass(shapes.__class__, gp_Pnt):
    #         # if a gp_Pnt is passed, first convert to vertex
    #         vertex = BRepBuilderAPI_MakeVertex(shapes)
    #         shapes = [vertex.Shape()]
    #     elif isinstance(shapes, gp_Pnt2d):
    #         vertex = BRepBuilderAPI_MakeVertex(gp_Pnt(shapes.X(), shapes.Y(), 0))
    #         shapes = [vertex.Shape()]
    #     elif isinstance(shapes, Geom_Surface):
    #         bounds = True
    #         toldegen = 1e-6
    #         face = BRepBuilderAPI_MakeFace()
    #         face.Init(shapes, bounds, toldegen)
    #         face.Build()
    #         shapes = [face.Shape()]
    #     elif isinstance(shapes, Geom_Curve):
    #         edge = BRepBuilderAPI_MakeEdge(shapes)
    #         shapes = [edge.Shape()]
    #     elif isinstance(shapes, Geom2d_Curve):
    #         edge2d = BRepBuilderAPI_MakeEdge2d(shapes)
    #         shapes = [edge2d.Shape()]
    #     # if only one shapes, create a list with a single shape
    #     if not isinstance(shapes, list):
    #         shapes = [shapes]
    #     # build AIS_Shapes list
    #     for shape in shapes:
    #         if material or texture:
    #             if texture:
    #                 shape_to_display = AIS_TexturedShape(shape)
    #                 (
    #                     filename,
    #                     toScaleU,
    #                     toScaleV,
    #                     toRepeatU,
    #                     toRepeatV,
    #                     originU,
    #                     originV,
    #                 ) = texture.GetProperties()
    #                 shape_to_display.SetTextureFileName(TCollection_AsciiString(filename))
    #                 shape_to_display.SetTextureMapOn()
    #                 shape_to_display.SetTextureScale(True, toScaleU, toScaleV)
    #                 shape_to_display.SetTextureRepeat(True, toRepeatU, toRepeatV)
    #                 shape_to_display.SetTextureOrigin(True, originU, originV)
    #                 shape_to_display.SetDisplayMode(3)
    #             elif material:
    #                 shape_to_display = AIS_Shape(shape)
    #                 if isinstance(material, Graphic3d_NameOfMaterial):
    #                     shape_to_display.SetMaterial(Graphic3d_MaterialAspect(material))
    #                 else:
    #                     shape_to_display.SetMaterial(material)
    #         else:
    #             # TODO: can we use .Set to attach all TopoDS_Shapes
    #             # to this AIS_Shape instance?
    #             shape_to_display = AIS_Shape(shape)

    #         ais_shapes.append(shape_to_display)

    #     # if not SOLO:
    #     #     # computing graphic properties is expensive
    #     #     # if an iterable is found, so cluster all TopoDS_Shape under
    #     #     # an AIS_MultipleConnectedInteractive
    #     #     #shape_to_display = AIS_MultipleConnectedInteractive()
    #     #     for ais_shp in ais_shapes:
    #     #         # TODO : following line crashes with oce-0.18
    #     #         # why ? fix ?
    #     #         #shape_to_display.Connect(i)
    #     #         self.Context.Display(ais_shp, False)
    #     # set the graphic properties
    #     if material is None:
    #         # The default material is too shiny to show the object
    #         # color well, so I set it to something less reflective
    #         for shape_to_display in ais_shapes:
    #             shape_to_display.SetMaterial(Graphic3d_MaterialAspect(Graphic3d_NOM_NEON_GNC))
    #     if color:
    #         if isinstance(color, str):
    #             color = get_color_from_name(color)
    #         elif isinstance(color, int):
    #             color = Quantity_Color(color)
    #         for shp in ais_shapes:
    #             self.Context.SetColor(shp, color, False)
    #     if transparency:
    #         for shape_to_display in ais_shapes:
    #             shape_to_display.SetTransparency(transparency)
    #     # display the shapes
    #     for shape_to_display in ais_shapes:
    #         self.Context.Display(shape_to_display, False)
    #     if update:
    #         # especially this call takes up a lot of time...
    #         self.FitAll()
    #         self.Repaint()

    #     return ais_shapes

    # def DisplayColoredShape(
    #     self,
    #     shapes,
    #     color="YELLOW",
    #     update=False,
    # ):
    #     if isinstance(color, str):
    #         dict_color = {
    #             "WHITE": Quantity_NOC_WHITE,
    #             "BLUE": Quantity_NOC_BLUE1,
    #             "RED": Quantity_NOC_RED,
    #             "GREEN": Quantity_NOC_GREEN,
    #             "YELLOW": Quantity_NOC_YELLOW,
    #             "CYAN": Quantity_NOC_CYAN1,
    #             "BLACK": Quantity_NOC_BLACK,
    #             "ORANGE": Quantity_NOC_ORANGE,
    #         }
    #         clr = dict_color[color]
    #     elif isinstance(color, Quantity_Color):
    #         clr = color
    #     else:
    #         raise ValueError('color should either be a string ( "BLUE" ) or a Quantity_Color(0.1, 0.8, 0.1) got %s' % color)

    #     return self.DisplayShape(shapes, color=clr, update=update)

    def EnableAntiAliasing(self):
        self.SetNbMsaaSample(4)

    def DisableAntiAliasing(self):
        self.SetNbMsaaSample(0)

    def EraseAll(self):
        self.Context.EraseAll(True)

    def Tumble(self, num_images, animation=True):
        self.View.Tumble(num_images, animation)

    def Pan(self, dx, dy):
        self.View.Pan(dx, dy)

    def SetSelectionMode(self, mode=None):
        """根据点击依次选择"""
        self.Context.Deactivate()
        # some thing we'll need later
        modes = itertools.cycle([TopAbs_FACE, TopAbs_EDGE, TopAbs_VERTEX, TopAbs_SHELL, TopAbs_SOLID])
        topo_level = next(modes)
        if mode is None:
            self.Context.Activate(AIS_Shape_SelectionMode(topo_level), True)
        else:
            self.Context.Activate(AIS_Shape_SelectionMode(mode), True)
        self.Context.UpdateSelected(True)

    def SetSelectionModeVertex(self):
        """选择点"""
        self.SetSelectionMode(TopAbs_VERTEX)

    def SetSelectionModeEdge(self):
        """选择边"""
        self.SetSelectionMode(TopAbs_EDGE)

    def SetSelectionModeFace(self):
        """选择面"""
        self.SetSelectionMode(TopAbs_FACE)

    def SetSelectionModeShape(self):
        """选择体"""
        self.Context.Deactivate()

    # def SetSelectionModeNeutral(self):
    #     self.Context.Deactivate()

    def GetSelectedShapes(self):
        return self.selected_aiss

    def GetSelectedShape(self):
        return self.Context.SelectedShape()

    def SelectArea(self, Xmin, Ymin, Xmax, Ymax):
        self.Context.Select(Xmin, Ymin, Xmax, Ymax, self.View, True)
        self.Context.InitSelected()
        # reinit the selected_shapes list
        self.selected_aiss = []
        while self.Context.MoreSelected():
            if self.Context.HasSelectedShape():
                self.selected_aiss.append(self.Context.SelectedShape())
            self.Context.NextSelected()
        # callbacks
        for callback in self._select_callbacks:
            callback(self.selected_aiss, Xmin, Ymin, Xmax, Ymax)

    def Select(self, X, Y):
        """选择之后执行回调函数"""
        self.Context.Select(True)
        self.Context.InitSelected()

        self.selected_aiss = []
        if self.Context.MoreSelected():
            if self.Context.HasSelectedShape():
                # self.selected_shapes.append(self.Context.SelectedShape())
                self.selected_aiss.append(self.Context.SelectedInteractive())
        # callbacks
        for callback in self._select_callbacks:
            callback(self.selected_aiss, X, Y)

    def ShiftSelect(self, X, Y):
        self.Context.ShiftSelect(True)
        self.Context.InitSelected()

        self.selected_aiss = []
        while self.Context.MoreSelected():
            if self.Context.HasSelectedShape():
                self.selected_aiss.append(self.Context.SelectedShape())
            self.Context.NextSelected()
        # highlight newly selected unhighlight those no longer selected
        self.Context.UpdateSelected(True)
        # callbacks
        for callback in self._select_callbacks:
            callback(self.selected_aiss, X, Y)

    def Rotation(self, X, Y):
        self.View.Rotation(X, Y)

    def DynamicZoom(self, X1, Y1, X2, Y2):
        self.View.Zoom(X1, Y1, X2, Y2)

    def ZoomFactor(self, zoom_factor):
        self.View.SetZoom(zoom_factor)

    def ZoomArea(self, X1, Y1, X2, Y2):
        self.View.WindowFit(X1, Y1, X2, Y2)

    def Zoom(self, X, Y):
        self.View.Zoom(X, Y)

    def StartRotation(self, X, Y):
        self.View.StartRotation(X, Y)


class OffscreenRenderer(myViewer3d):
    """The offscreen renderer is inherited from Viewer3d.
    The DisplayShape method is overridden to export to image
    each time it is called.
    """

    def __init__(self, screen_size=(640, 480)):
        myViewer3d.__init__(self)
        # create the renderer
        self.Create()
        self.SetSize(screen_size[0], screen_size[1])
        self.SetModeShaded()
        self.set_bg_gradient_color([206, 215, 222], [128, 128, 128])
        self.display_triedron()
        self.capture_number = 0

    def DisplayShape(
        self,
        shapes,
        material=None,
        texture=None,
        color=None,
        transparency=None,
        update=True,
    ):
        # call the "original" DisplayShape method
        r = super(OffscreenRenderer, self).DisplayShape(shapes, material, texture, color, transparency, update)  # always update
        if os.getenv("PYTHONOCC_OFFSCREEN_RENDERER_DUMP_IMAGE") == "1":  # dump to jpeg file
            timestamp = ("%f" % time.time()).split(".")[0]
            self.capture_number += 1
            image_filename = "capture-%i-%s.jpeg" % (
                self.capture_number,
                timestamp.replace(" ", "-"),
            )
            if os.getenv("PYTHONOCC_OFFSCREEN_RENDERER_DUMP_IMAGE_PATH"):
                path = os.getenv("PYTHONOCC_OFFSCREEN_RENDERER_DUMP_IMAGE_PATH")
                if not os.path.isdir(path):
                    raise IOError("%s is not a valid path" % path)
            else:
                path = os.getcwd()
            image_full_name = os.path.join(path, image_filename)
            self.View.Dump(image_full_name)
            if not os.path.isfile(image_full_name):
                raise IOError("OffscreenRenderer failed to render image to file")
            print("OffscreenRenderer content dumped to %s" % image_full_name)
        return r

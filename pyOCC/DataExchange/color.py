from itertools import cycle

from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB


def check_RGB(value):
    if isinstance(value, int):
        if value >= 0 and value <= 255:
            return True
    return False


# end def


def check_Alpha(value):
    if isinstance(value, float):
        if value >= 0 and value <= 1.0:
            return True
    return False


# end def


class COLOR:
    OCC_RED = Quantity_Color(1, 0, 0, Quantity_TOC_RGB)
    OCC_GREEN = Quantity_Color(0, 1, 0, Quantity_TOC_RGB)
    OCC_BLUE = Quantity_Color(0, 0, 1, Quantity_TOC_RGB)
    OCC_GRAY = Quantity_Color(125.0 / 255.0, 125.0 / 255.0, 125.0 / 255.0, Quantity_TOC_RGB)
    OCC_XAix = OCC_GREEN
    OCC_YAix = OCC_BLUE
    OCC_ZAix = OCC_RED

    def __init__(self, *args, **kwds):
        self.rgba_value: tuple[int, int, int, float] = (0, 0, 0, 1.0)
        R, G, B, A = 0, 0, 0, 1.0
        if len(args) == 1:
            if isinstance(args[0], (tuple, list)):
                if len(args[0]) == 3:
                    R, G, B = args[0]
                    A = 1.0
                if len(args[0]) == 4:
                    R, G, B, A = args[0]
        elif len(args) == 3:
            R, G, B = args
            A = 1.0
        elif len(args) == 4:
            R, G, B, A = args
        # end if
        if check_RGB(R) and check_RGB(G) and check_RGB(B) and check_Alpha(A):
            self.rgba_value = (R, G, B, A)
        # end if

    # end __init__

    # end alternate constructor
    def __call__(self, *args, **kwds):
        return self.to_Quantity()

    # end __call__
    def __repr__(self) -> str:
        return f"{self.r}, {self.g}, {self.b}, {self.alpha}"

    # end __repr__
    @property
    def r(self) -> int:
        return self.rgba_value[0]

    # end r
    @property
    def g(self) -> int:
        return self.rgba_value[1]

    # end g
    @property
    def b(self) -> int:
        return self.rgba_value[2]

    # end b
    @property
    def alpha(self) -> float:
        return self.rgba_value[3]

    # end alpha
    def from_rgb(self, r: int | tuple | list, g: int = 0, b: int = 0, a: float = 1.0):
        if isinstance(r, tuple):
            if len(r) == 3:
                self.rgba_value = (*r, a)
            if len(r) == 4:
                self.rgba_value = r
            return None
        # end if
        if isinstance(r, list):
            if len(r) == 3:
                self.rgba_value = (*r, a)
            if len(r) == 4:
                self.rgba_value = r
                return None
        # end if

    # end def
    def to_Quantity(self):
        return Quantity_Color(
            float(self.r) / 255.0, float(self.g) / 255.0, float(self.b) / 255.0, Quantity_TOC_RGB
        )

    # end def
    def to_hex(self):
        return "#{:02X}{:02X}{:02X}".format(self.r, self.g, self.b)

    # end def
    def to_ARGB(self):
        return "#{:02X}{:02X}{:02X}{:02X}".format(int(self.alpha), self.r, self.g, self.b)

    # end def
    def to_HSL(self):
        r, g, b = self.r / 255.0, self.g / 255.0, self.b / 255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        delta = max_val - min_val

        # Lightness
        l = (max_val + min_val) / 2.0

        # Saturation
        if delta == 0:
            s = 0
            h = 0  # Hue is undefined when delta is 0, but typically set to 0
        else:
            s = delta / (2.0 - max_val - min_val) if l > 0.5 else delta / (max_val + min_val)

            # Hue
            if max_val == r:
                h = (g - b) / delta + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / delta + 2
            else:
                h = (r - g) / delta + 4
            h /= 6

        # Convert hue to degrees, saturation and lightness to percentage
        h = round(h * 360)
        s = round(s * 100)
        l = round(l * 100)

        return (h, s, l, round(self.alpha, 2))

    # end def


# end class

# 彩虹颜色表
rainbow_color = [
    (255, 0, 0),  # 红色 (Red)
    (0, 255, 0),  # 绿色 (Green)
    (255, 255, 0),  # 黄色 (Yellow)
    (0, 255, 255),  # 青色 (Cyan)
    (128, 0, 128),  # 紫色 (Purple)
    (255, 165, 0),  # 橙色 (Orange)
    (0, 0, 255),  # 蓝色 (Blue)
    (0, 0, 0),  # 黑色 (Black)
    (200, 200, 200),  # 灰白色
    # (255, 165, 16),
    # (0, 44, 83),
    # (255, 189, 102),
    # (12, 132, 198),
    # (247, 77, 77),
    # (36, 85, 164),
    # (65, 183, 172),
    # (0, 44, 83),
    # (255, 165, 16),
    # (12, 132, 198),
    # (255, 189, 102),
    # (247, 77, 77),
    # (36, 85, 164),
    # (65, 183, 172),
    # (255, 165, 16),
    # (0, 44, 83),
    # (255, 189, 102),
    # (12, 132, 198),
    # (247, 77, 77),
    # (36, 85, 164),
    # (65, 183, 172),
    # (0, 44, 83),
    # (255, 165, 16),
    # (12, 132, 198),
    # (255, 189, 102),
    # (247, 77, 77),
    # (36, 85, 164),
    # (65, 183, 172),
]
color_list = cycle([COLOR(i)() for i in rainbow_color])

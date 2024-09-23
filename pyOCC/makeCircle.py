from mathTools import threePointFixedCircle

from . import getXYZ


def makeCirclefromThreePoint(point1, point2, point3):
    """三点定圆"""
    p1 = getXYZ(point1)
    p2 = getXYZ(point2)
    p3 = getXYZ(point3)
    circle_center, radius, angle = threePointFixedCircle(p1, p2, p3)

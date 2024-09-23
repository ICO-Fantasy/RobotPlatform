from __future__ import annotations

import numpy as np
from OCC.Core.gp import gp_Vec

from .Point import Point


class Vector:
    def __init__(self, x=0.0, y=0.0, z=0.0, start_point=None | Point):
        """创建一个向量

        Parameters
        ----------
        `x` : float, optional
            点的 X 坐标，by default 0.0
        `y` : float, optional
            点的 Y 坐标，by default 0.0
        `z` : float, optional
            点的 Z 坐标，by default 0.0
        `start_point` : Point, optional
            向量的起点，by default Point(0.0, 0.0, 0.0)
        """
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.start_point = start_point if start_point is not None else Point(0.0, 0.0, 0.0)

    # end default constructor
    def __add__(self, other_vector: Vector):
        """定义加法操作"""
        if isinstance(other_vector, Vector):
            # 检查是否是 Vector 类型的对象
            return Vector(self.x + other_vector.x, self.y + other_vector.y, self.z + other_vector.z, self.start_point)
        else:
            raise TypeError(f"Unsupported operand type for +: Vector and {type(other_vector)}")

    # end def
    def __sub__(self, other_vector: Vector):
        """定义减法操作"""
        if isinstance(other_vector, Vector):
            # 检查是否是 Vector 类型的对象
            return Vector(self.x - other_vector.x, self.y - other_vector.y, self.z - other_vector.z, self.start_point)
        else:
            raise TypeError(f"Unsupported operand type for -: Vector and {type(other_vector)}")

    # end def
    def __mul__(self, other_vector: Vector):
        """点乘操作

        Parameters
        ----------
        other_vector : Vector
            _description_
        """
        if isinstance(other_vector, Vector):
            # 检查是否是 Vector 类型的对象
            return self.x * other_vector.x + self.y * other_vector.y + self.z * other_vector.z

    # end def
    def __matmul__(self, other_vector: Vector):
        """叉乘操作

        Parameters
        ----------
        other_vector : Vector
            _description_
        """
        if isinstance(other_vector, Vector):
            np_vec = np.array([self.x, self.y, self.z])
            other_np_vec = np.array([other_vector.x, other_vector.y, other_vector.z])
            new_vec = np_vec @ other_np_vec
            return Vector(new_vec[0], new_vec[1], new_vec[2])
        else:
            raise TypeError("Unsupported operand type for @")

    # end def
    def __getitem__(self, index):
        """定义索引操作，使 Point[0] 返回 self._x, Point[1] 返回 self._y, Point[2] 返回 self._z"""
        match index:
            case 0:
                return self.x
            case 1:
                return self.y
            case 2:
                return self.z
            case _:
                raise IndexError("Index out of range")
        # end match

    # end def
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    # end def
    def from_gp_Vec(self, a_gp_vec: gp_Vec):
        """读取 gp_Vec 的数据到 Vector 对象

        Parameters
        ----------
        a_gp_vec : gp_Vec
            OCC 的点
        """
        self.x = a_gp_vec.X()
        self.y = a_gp_vec.Y()
        self.z = a_gp_vec.Z()

    # end def
    def to_gp_Vec(self) -> gp_Vec:
        """将 Vector 对象输出为 gp_Vec

        Returns
        -------
        gp_Vec
        """
        gp_Vec()
        return gp_Vec(self.x, self.y, self.z)

    # end def
    def endPoint(self) -> Point:
        """返回向量的终点"""
        return self.start_point + Point(self.x, self.y, self.z)

    # end def
    def Normalized(self) -> Vector:
        """返回单位化的向量"""
        np_vec = np.array([self.x, self.y, self.z])
        # 计算向量的模
        vector_norm = np.linalg.norm(np_vec)
        # 将向量的每个分量除以模，得到单位向量
        unit_vector = np_vec / vector_norm
        return Vector(*unit_vector, self.start_point)

    # end def
    def Normalize(self):
        """将向量单位化"""
        np_vec = np.array([self.x, self.y, self.z])
        # 计算向量的模
        vector_norm = np.linalg.norm(np_vec)
        # 将向量的每个分量除以模，得到单位向量
        unit_vector = np_vec / vector_norm
        self.x, self.y, self.z = unit_vector

    # end def
    # def findIntersection(self, other_vector: Vector):
    #     np_vec = np.array([self.x, self.y, self.z])
    #     other_np_vec = np.array([other_vector.x, other_vector.y, other_vector.z])
    #     new_vec = np_vec @ other_np_vec

    #     # 检查是否向量平行（如果叉乘结果为零）
    #     if np.allclose(new_vec, [0.0, 0.0, 0.0]):
    #         # 向量平行，可能没有交点
    #         return None

    #     # 计算参数 t1 和 t2
    #     t1 = diff_vector.dot_product(cross_product) / cross_product.dot_product(cross_product)
    #     t2 = cross_product.dot_product(diff_vector) / cross_product.dot_product(cross_product)

    #     # 计算交点坐标
    #     intersection_point = self.start_point + t1 * self
    #     return intersection_point

    # # end def
    def twoEdgeIntersection(self, other_vector: Vector, tolerance=1e-6) -> tuple[bool, Vector | None]:
        startPointAB, endPointAB = self.start_point, self.endPoint()
        startPointCD, endPointCD = other_vector.start_point, other_vector.endPoint()

        a11 = endPointAB[0] - startPointAB[0]
        a12 = startPointCD[0] - endPointCD[0]
        b1 = startPointCD[0] - startPointAB[0]

        a21 = endPointAB[1] - startPointAB[1]
        a22 = startPointCD[1] - endPointCD[1]
        b2 = startPointCD[1] - startPointAB[1]

        a31 = endPointAB[2] - startPointAB[2]
        a32 = startPointCD[2] - endPointCD[2]
        b3 = startPointCD[2] - startPointAB[2]

        A11 = a11**2 + a21**2 + a31**2
        A12 = a11 * a12 + a21 * a22 + a31 * a32
        A21 = A12
        A22 = a12**2 + a22**2 + a32**2
        B1 = a11 * b1 + a21 * b2 + a31 * b3
        B2 = a12 * b1 + a22 * b2 + a32 * b3

        EPS = 1.0e-10
        temp = A11 * A22 - A12 * A21
        if abs(temp) < EPS:
            if (
                pointOnLineSegment(line1, startPointCD, tolerance)
                or pointOnLineSegment(line1, endPointCD, tolerance)
                or pointOnLineSegment(line2, startPointAB, tolerance)
                or pointOnLineSegment(line2, endPointAB, tolerance)
            ):
                return True, gp_Pnt()  # 返回 True 表示相交，但不返回具体交点位置
        else:
            t = [-(A12 * B2 - A22 * B1) / temp, (A11 * B2 - A21 * B1) / temp]
            if (t[0] >= 0 - EPS and t[0] <= 1.0 + EPS) and (t[1] >= 0 - EPS and t[1] <= 1.0 + EPS):
                if (
                    abs(
                        (startPointAB[0] + (endPointAB[0] - startPointAB[0]) * t[0])
                        - (startPointCD[0] + (endPointCD[0] - startPointCD[0]) * t[1])
                    )
                    < tolerance
                    and abs(
                        (startPointAB[1] + (endPointAB[1] - startPointAB[1]) * t[0])
                        - (startPointCD[1] + (endPointCD[1] - startPointCD[1]) * t[1])
                    )
                    < tolerance
                    and abs(
                        (startPointAB[2] + (endPointAB[2] - startPointAB[2]) * t[0])
                        - (startPointCD[2] + (endPointCD[2] - startPointCD[2]) * t[1])
                    )
                    < tolerance
                ):
                    intersection_point = gp_Pnt(
                        startPointAB[0] + (endPointAB[0] - startPointAB[0]) * t[0],
                        startPointAB[1] + (endPointAB[1] - startPointAB[1]) * t[0],
                        startPointAB[2] + (endPointAB[2] - startPointAB[2]) * t[0],
                    )
                    return True, intersection_point
        return False, gp_Pnt()  # 返回 False 表示不相交，不返回具体交点位置


# end class
if __name__ == "__main__":
    # 创建 Point 对象
    point1 = Vector(1.0, 2.0, 3.0)
    point2 = Vector(4.0, 5.0, 6.0)

    # 参与 NumPy 计算
    result = point1 + point2
    print(result)  # 输出 [ 5.  7.  9.]
# end main

"""
Descriptions
------------
机器人 DH 参数表示

Data
----
2024-01-29

Author
------
ICO
"""
import numpy as np
from loguru import logger

from .dynamic import rotation_x, rotation_y, rotation_z
from .transform import Radian, TransformMatrix_4x4


def standard_DH2Transform(theta: Radian, d: float, a: float, alpha: Radian) -> tuple[TransformMatrix_4x4, TransformMatrix_4x4]:
    """标准 DH 表示转换到齐次变换矩阵\n
    `T_{i-1,i} = θ_{i} @ d_{i} @ a_{i} @ α_{i} `\n
    所有参数均为第 i 个参数

    Parameters
    ----------
    `theta` : _type_
        _description_
    `d` : _type_
        _description_
    `a` : _typ e_
        _description_
    `alpha` : _type_
        _description_

    Returns
    -------
    TransformMatrix_4x4
        _description_
    """
    s_t = np.sin(theta)
    c_t = np.cos(theta)
    s_a = np.sin(alpha)
    c_a = np.cos(alpha)

    transform_matrix = np.matrix(
        [
            [c_t, -s_t * c_a, s_t * s_a, a * c_t],
            [s_t, c_t * c_a, -c_t * s_a, a * s_t],
            [0, s_a, c_a, d],
            [0, 0, 0, 1],
        ]
    )
    return transform_matrix


# end def
def Modified_DH2Transform(d: float, theta: Radian, a: float, alpha: Radian) -> TransformMatrix_4x4:
    """改进 DH 表示转换到齐次变换矩阵\n
    `T_{i-1,i} =  α_{i-1} @ a_{i-1} @ d_{i} @ θ_{i}`
    alpha 和 a 为第 i-1 个参数，theta 和 d 为第 i 个参数
    Parameters
    ----------
    `a` : _typ e_
        _description_
    `d` : _type_
        _description_
    `alpha` : _type_
        _description_
    `theta` : _type_
        _description_

    Returns
    -------
    TransformMatrix_4x4
        _description_
    """
    s_t = np.sin(theta)
    c_t = np.cos(theta)
    s_a = np.sin(alpha)
    c_a = np.cos(alpha)

    transform_matrix = np.matrix(
        [
            # [c_t, -s_t * c_a, s_t * s_a, a * c_t],
            # [s_t, c_t * c_a, -c_t * s_a, a * s_t],
            # [0, s_a, c_a, d],
            [0, 0, 0, 1],
        ]
    )
    return transform_matrix


# end def

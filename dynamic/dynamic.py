import numpy as np

pi = np.pi
atan2 = np.arctan2
sin = np.sin
asin = np.arcsin
cos = np.cos
acos = np.arccos
sqrt = np.sqrt


def rot_x(a):
    return np.array([[1, 0, 0], [0, cos(a), -sin(a)], [0, sin(a), cos(a)]])


def rotation_x(a):
    trans = np.eye(4)
    trans[:3, :3] = rot_x(a)
    return trans


def rot_y(b):
    return np.array([[cos(b), 0, sin(b)], [0, 1, 0], [-sin(b), 0, cos(b)]])


def rotation_y(b):
    trans = np.eye(4)
    trans[:3, :3] = rot_y(b)
    return trans


def rot_z(c):
    return np.array([[cos(c), -sin(c), 0], [sin(c), cos(c), 0], [0, 0, 1]])


def rotation_z(c):
    trans = np.eye(4)
    trans[:3, :3] = rot_z(c)
    return trans

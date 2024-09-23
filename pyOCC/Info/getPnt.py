from OCC.Core.gp import gp_Pnt


def getXYZ(pnt: gp_Pnt):
    """获取 Pnt 的三坐标

    Parameters
    ----------
    pnt : gp_Pnt
        _description_

    Returns
    -------
    list[float, float, float]
        _description_
    """
    return [pnt.X(), pnt.Y(), pnt.Z()]


# end def

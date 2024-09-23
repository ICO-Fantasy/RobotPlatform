from OCC.Core.gp import *


def changeRefCoord(old_trsf: gp_Trsf, new_ref: gp_Trsf):
    """
    两坐标变换的相对参考系应该一致（默认均相对于原点）
    """
    return_trsf = gp_Trsf()
    return_trsf.Multiply(old_trsf)
    return_trsf.PreMultiply(new_ref)
    return return_trsf


# end def

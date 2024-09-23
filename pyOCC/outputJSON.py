import json

from OCC.Core.gp import *


def trsfToJSON(atrsf: gp_Trsf):
    """
    Return
    ------
    `Location`: [x,y,z], `Matrix`: Rmatrix(3*3), `shape`: float, `scale`: float
    """
    location = [atrsf.Value(1, 4), atrsf.Value(2, 4), atrsf.Value(3, 4)]
    Rmatrix = [
        atrsf.Value(1, 1),
        atrsf.Value(1, 2),
        atrsf.Value(1, 3),
        atrsf.Value(2, 1),
        atrsf.Value(2, 2),
        atrsf.Value(2, 3),
        atrsf.Value(3, 1),
        atrsf.Value(3, 2),
        atrsf.Value(3, 3),
    ]
    shpae = atrsf.Form()
    scale = atrsf.ScaleFactor()
    data = {"Location": location, "Matrix": Rmatrix, "shape": shpae, "scale": scale}
    print(1111)
    print(f'"Location": {location}, "Matrix": {Rmatrix}, "shape": {shpae}, "scale": {scale}')
    return json.dumps(data)


if __name__ == "__main__":
    atrsf = gp_Trsf()
    atrsf.SetTranslationPart(gp_Vec(10, 20, 30))
    atrsf.SetRotationPart(gp_Quaternion(gp_Vec(0, 0, 1), 180))
    trsfToJSON(atrsf)
# end main

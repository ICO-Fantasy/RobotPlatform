from pprint import pprint

files = [r"D:\Download\line.cpt", r"D:\Download\points.txt"]

for f in files:
    with open(f, "r") as f:
        lines = f.readlines()
    # end open file
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    print("\n")
    points = []
    for line in lines:
        p = line.split()
        if len(p) == 3:
            points.append((float(p[0]), float(p[1]), float(p[2])))
    pprint(points)

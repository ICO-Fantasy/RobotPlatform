import inspect
import re


def print_Var_Name(p):
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r"\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)", line)
        if m:
            print(m.group(1))
            return m.group(1)


if __name__ == "__main__":
    spam = 42
    print(print_Var_Name(spam))

import json

from xmindparser import xmind_to_dict, xmind_to_json

xmind_file = r"D:\Download\机器人产品界面通用功能梳理.xmind"
# out_file = xmind_to_json(xmind_file)
out = xmind_to_dict(xmind_file)
print(out)
out_file = r"D:\Download\out.json"
# out to json save in file
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=4)

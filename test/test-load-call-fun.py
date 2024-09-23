import importlib.util
import sys


def load_and_call_function(module_path, function_name):
    try:
        spec = importlib.util.spec_from_file_location("custom_module", module_path)
        custom_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(custom_module)

        if hasattr(custom_module, function_name):
            function = getattr(custom_module, function_name)
            function()
        else:
            print(f"Module has no attribute: {function_name}")
    except Exception as e:
        return f"Error: {e}"


# 使用动态加载
load_and_call_function("D:/ICO/RobotPlatform/test02_2.py", "a_fun")
